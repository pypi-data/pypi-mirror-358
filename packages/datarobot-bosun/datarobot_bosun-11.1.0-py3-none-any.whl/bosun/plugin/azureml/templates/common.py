#  ---------------------------------------------------------------------------------
#  Copyright (c) 2023 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2024.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#  ---------------------------------------------------------------------------------
import json
import logging
import os
import shutil
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from typing import Union

import pandas as pd
from datarobot_predict.scoring_code import ModelType
from datarobot_predict.scoring_code import ScoringCodeModel
from datarobot_predict.scoring_code import TimeSeriesType
from pydantic import BaseModel
from pydantic import Extra
from pydantic import validator
from pydantic.utils import to_lower_camel

from datarobot_mlops.event import Event
from datarobot_mlops.event import EventType
from datarobot_mlops.mlops import MLOps

MONITORING_ENABLED = os.getenv("MONITORING_ENABLED") == "True"
DEPLOYMENT_ID = os.getenv("MLOPS_DEPLOYMENT_ID")

ASSOCIATION_ID_COL = os.getenv("MLOPS_ASSOCIATION_ID_COLUMN")
ASSOCIATION_ID_ALLOW_MISSING = os.getenv("MLOPS_ASSOCIATION_ID_ALLOW_MISSING_VALUES") == "True"

MAX_EXPLANATIONS = os.getenv("MAX_EXPLANATIONS", 0)
THRESHOLD_HIGH = os.getenv("THRESHOLD_HIGH")
THRESHOLD_LOW = os.getenv("THRESHOLD_LOW")

_model = None
_mlops = None
_model_id = None


def cast(value, value_type):
    try:
        return value_type(value)
    except (ValueError, TypeError):
        return None


class GenericModelParams(BaseModel):
    class Config:
        extra = Extra.forbid
        alias_generator = to_lower_camel
        allow_population_by_field_name = True

    max_explanations: int = cast(MAX_EXPLANATIONS, int)
    threshold_high: Optional[float] = cast(THRESHOLD_HIGH, float)
    threshold_low: Optional[float] = cast(THRESHOLD_LOW, float)


class TSModelParams(GenericModelParams):
    time_series_type: TimeSeriesType = TimeSeriesType.FORECAST
    forecast_point: Optional[datetime] = None
    predictions_start_date: Optional[datetime] = None
    predictions_end_date: Optional[datetime] = None
    prediction_intervals_length: Optional[int] = None

    # Note: reuse tracking doesn't work with the way we are testing this
    # code with exec() so just turn it off.
    @validator("time_series_type", pre=True, allow_reuse=True)
    def enum_value_or_name(cls, v):
        if isinstance(v, TimeSeriesType):
            return v
        elif isinstance(v, str):
            if v.isdigit():
                return TimeSeriesType(int(v))
            else:
                return TimeSeriesType[v.upper()]
        else:
            return TimeSeriesType(v)


class ErrorCodes(Enum):
    # Copied from datarobot/DataRobot/blob/master/predictions_api/constants.py#L66

    # The error code is returned when a requested passthrough column has the same
    # name as one of the output column names in the tabular format (i.e. CSV). For
    # instance: POSITIVE_CLASS or FORECAST_POINT.
    PASSTHROUGH_COLUMNS_CONFLICT = "passthrough_columns_conflict"

    # The error code is returned when a request passthrough column could not be
    # found in the scoring dataset.
    PASSTHROUGH_COLUMN_DOES_NOT_EXIST = "passthrough_column_does_not_exist"

    # The error code is returned when one or more features required for predictions
    # are missing from the scoring dataset.
    MISSING_COLUMNS = "missing_columns"

    # The error code is returned when ALL features required for predictions are
    # missing from the scoring dataset.
    MISSING_ALL_COLUMNS = "missing_all_columns"

    # The error code is returned when the request waited in uWSGI listen queue too
    # long, and there's no need to process it anymore. Normally we have a 600
    # seconds timeout on ALB, which means connections that are idling longer will be
    # closed. Unfortunately the request could not be removed from uWSGI listen,
    # hence the application can check the request start time and reject expired
    # requests in order avoid computing something that could not be returned to a
    # client anyway.
    REQUEST_EXPIRED = "request_expired"


# When running in the VSCode debugger, `JAVA_HOME` isn't being set and is needed
# by `jpype.startJVM()` but we can derive it by looking for the `java` command
# in the PATH.
def set_java_home():
    if "JAVA_HOME" not in os.environ:
        java_path = shutil.which("java")
        # If we didn't find java, don't raise an error yet and let jpype have
        # a go at it and it will raise an error if it couldn't find it.
        if java_path is not None:
            logging.info("Using path to `java` executable to set JAVA_HOME")
            os.environ["JAVA_HOME"] = str(Path(java_path).parent.parent)


def load_model(model_path):
    global _model
    global _model_id

    if not model_path.exists():
        raise RuntimeError(f"Model JAR is not present: {model_path}")

    if _model is not None:
        logging.info("Found cached model: %s", _model)
    else:
        logging.info("Starting up JVM (JAVA_HOME=%s)", os.environ.get("JAVA_HOME"))
        _model = ScoringCodeModel(str(model_path))
        logging.info(
            "Loaded Model(id=%s; type=%s): %s", _model.model_id, _model.model_type, model_path
        )
        # Allow the modelId to be overridden by the environment in case the scoring JAR
        # has the wrong ID (mainly during testing).
        _model_id = os.getenv("MLOPS_MODEL_ID", _model.model_id)

    logging.info("Model Info: %s", _model.model_info)
    return _model, _model_id


def read_feature_types():
    default_feature_types_path = Path(__file__).parent / "feature_types.json"
    feature_types_path = os.getenv("MLOPS_MODEL_FEATURE_TYPES_PATH", default_feature_types_path)
    with open(feature_types_path, "r") as f:
        return json.load(f)


def get_mlops(
    model_id, feature_types=None, deployment_id=DEPLOYMENT_ID, enabled=MONITORING_ENABLED
):
    global _mlops

    if enabled and _mlops is None:
        if model_id is None:
            raise RuntimeError("Need to load the model before initializing MLOps")
        _mlops = (
            # Rely on most configuration via Env vars so we can easily change behavior without
            # needing to change any code.
            MLOps()
            .set_deployment_id(deployment_id)
            .set_model_id(model_id)
            # Don't need to use async mode because the Kafka spooler type is already async
            .set_async_reporting(False)
        )
        if feature_types:
            _mlops.set_feature_types(feature_types)
        _mlops.init()
    return _mlops


def get_model_id():
    return _model_id


def report_prediction_server_error_via_tracking_agent(
    mlops_sdk: Optional[MLOps],
    message: str,
    status_code: int,
    model_id: Optional[str] = None,
    deployment_id=DEPLOYMENT_ID,
    error_code: Optional[ErrorCodes] = None,
):
    """Report pred server error to Tracking Agent."""
    if mlops_sdk is None:
        return

    response_data = {"message": message}
    if error_code is not None:
        response_data["error_code"] = str(error_code.value)

    error_event = Event(
        event_type=EventType.PRED_REQUEST_FAILED,
        message=message,
        entity_id=deployment_id,
        data={
            "status_code": status_code,
            "response_body": json.dumps(response_data),
            "model_id": model_id or get_model_id(),
            "error_code": error_code.value if error_code else None,
        },
    )
    mlops_sdk.report_event(event=error_event)


def report_service_health_via_tracking_agent(
    mlops_sdk: Optional[MLOps],
    start_time_ns: int,
    predictions: pd.DataFrame,
):
    """Report service health stats to Tracking Agent."""
    if mlops_sdk is None:
        return

    elapsed = time.monotonic_ns() - start_time_ns
    mlops_sdk.report_deployment_stats(
        num_predictions=len(predictions),
        execution_time_ms=elapsed // 1000000,
    )


def report_predictions_data_via_tracking_agent(
    mlops_sdk: Optional[MLOps],
    scoring_model: ScoringCodeModel,
    predictions: pd.DataFrame,
    scoring_dataframe: pd.DataFrame,
    params: Union[GenericModelParams, TSModelParams],
    max_unaggregated_rows: int = float("inf"),
    allow_missing_association_id=ASSOCIATION_ID_ALLOW_MISSING,
    association_id_col=ASSOCIATION_ID_COL,
):
    """Report predictions data to Tracking Agent."""
    if mlops_sdk is None:
        return

    # This logic was lifted from the Prediction Server code: if MMM is configured to require
    # association IDs for the deployment but we find some were missing in this request, we just
    # drop the column for the whole dataset (which will disable accuracy tracking for this batch).
    if (
        not allow_missing_association_id
        and association_id_col in scoring_dataframe
        and (rows_missing_association_id := scoring_dataframe[association_id_col].isnull()).any()
    ):
        logging.warning(
            "Disabling accuracy tracking for this batch: found rows missing association ID:\n%s",
            scoring_dataframe[rows_missing_association_id],
        )
        scoring_dataframe = scoring_dataframe.drop(association_id_col, axis=1)

    if scoring_model.model_type == ModelType.TIME_SERIES:
        raise NotImplementedError("Reporting on TimeSeries model is not supported")

    skip_drift_tracking = False
    skip_accuracy_tracking = False
    # If prediction explanations were enabled, there will be extra columns in the predictions
    # dataset that we need to strip out for the reporting library.
    predictions: Union[pd.Series, pd.DataFrame] = (
        predictions["PREDICTION"]
        if scoring_model.model_type == ModelType.REGRESSION
        else predictions.iloc[:, : len(scoring_model.class_labels)]
    )

    # If the dataset is above the user-defined threshold, compute the aggregated stats client-side
    # (to save on bandwidth and processing cycles) but also be sure to send other key data raw.
    if len(scoring_dataframe) > max_unaggregated_rows:
        mlops_sdk.report_aggregated_predictions_data(
            features_df=scoring_dataframe,
            predictions=predictions.to_numpy().tolist(),
            class_names=scoring_model.class_labels,
        )
        # Drift has been computed in aggregate so don't count it again in the raw sample
        skip_drift_tracking = True

        # If we have association ID info, pull those rows out to report as raw for accuracy
        # tracking (but don't use for challengers as it may not be a random sample).
        if (
            association_id_col in scoring_dataframe
            and (rows_with_association_id := scoring_dataframe[association_id_col].notnull()).any()
        ):
            mlops_sdk.report_predictions_data(
                association_ids=scoring_dataframe[association_id_col][
                    rows_with_association_id
                ].tolist(),
                predictions=predictions[rows_with_association_id].to_numpy().tolist(),
                class_names=scoring_model.class_labels,
                skip_drift_tracking=True,
                skip_accuracy_tracking=False,
            )
            skip_accuracy_tracking = True

        # Take a random sample to report as raw data
        scoring_dataframe = scoring_dataframe.sample(max_unaggregated_rows)
        predictions = predictions.loc[scoring_dataframe.index]

    mlops_sdk.report_predictions_data(
        features_df=scoring_dataframe,
        predictions=predictions.to_numpy().tolist(),
        class_names=scoring_model.class_labels,
        skip_drift_tracking=skip_drift_tracking,
        skip_accuracy_tracking=skip_accuracy_tracking,
    )
