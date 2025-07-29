#  ---------------------------------------------------------------------------------
#  Copyright (c) 2023 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2023.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#  ---------------------------------------------------------------------------------
import http.client as http_codes
import logging
import os
import random
import string
import time
from enum import Enum
from pathlib import Path

import pandas as pd


class OutputFormat(Enum):
    DEFAULT = "DEFAULT"  # single CSV file w/o headers
    CUSTOM_OUTPUT_PARQUET = "CUSTOM_OUTPUT_PARQUET"  # a parquet file per batch
    CUSTOM_OUTPUT_CSV = "CUSTOM_OUTPUT_CSV"  # a CSV file per batch


MAX_RAW_ROWS = 10000
MODEL_PATH = (
    Path(os.environ["AZUREML_MODEL_DIR"]) / os.environ["DATAROBOT_MODEL_FILENAME"]
).resolve(strict=False)
OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", OutputFormat.DEFAULT.value)
OUTPUT_PATH = os.getenv("AZUREML_BI_OUTPUT_PATH")
OUTPUT_FILE_NAME = os.getenv("OUTPUT_FILE_NAME")


model = None
mlops_sdk = None


def init():
    global model, mlops_sdk
    set_java_home()  # noqa: F821
    model, model_id = load_model(MODEL_PATH)  # noqa: F821
    feature_types = read_feature_types()  # noqa: F821
    mlops_sdk = get_mlops(model_id=model_id, feature_types=feature_types)  # noqa: F821


def run(mini_batch):
    start_time = time.monotonic_ns()
    params = GenericModelParams()  # noqa: F821
    results = make_prediction(model, mini_batch, params, mlops_sdk, start_time)
    return results if OUTPUT_FORMAT == OutputFormat.DEFAULT.value else mini_batch


def make_prediction(model, scoring_batches, params, mlops_sdk, start_time) -> pd.DataFrame:
    incoming = []
    results = []
    for iteration, file_path in enumerate(scoring_batches, start=1):
        try:
            df = pd.read_csv(file_path, dtype=model.features)
        except Exception as err:
            logging.exception("#%s: error while loading inference data: %s", iteration, file_path)
            msg = f"#{iteration}: error while loading inference data: {file_path}: {err}"
            report_prediction_server_error_via_tracking_agent(  # noqa: F821
                mlops_sdk, msg, http_codes.BAD_REQUEST
            )
            continue

        try:
            logging.info("Scoring batch #%s", iteration)
            predictions: pd.DataFrame = model.predict(df, **params.dict())

            if OUTPUT_FORMAT == OutputFormat.CUSTOM_OUTPUT_PARQUET.value:
                unique_file_path = get_custom_output_file_path(file_path, "parquet")
                predictions.to_parquet(unique_file_path)
            # By default, AzureML creates a single CSV file with no headers.
            # Custom CSV output may be used to preserve headers
            elif OUTPUT_FORMAT == OutputFormat.CUSTOM_OUTPUT_CSV.value:
                unique_file_path = get_custom_output_file_path(file_path, "csv")
                predictions.to_csv(unique_file_path, index=False, header=True, mode="w")
        except Exception as err:
            # Log the error but continue so we can correctly support the `error_threshold`
            # the user has configured. The AzureML platform does this by monitoring the
            # the gap between mini-batch input count and returns. 'Batch inferencing' scenario
            # should return a list, dataframe, or tuple with the successful items to try to meet
            # this threshold.
            logging.exception("#%s: error while scoring: %s", iteration, df)
            msg = f"#{iteration}: error while scoring: {df}: {err}"
            report_prediction_server_error_via_tracking_agent(  # noqa: F821
                mlops_sdk, msg, http_codes.UNPROCESSABLE_ENTITY
            )
            predictions = pd.DataFrame()
        if predictions.empty:
            logging.warning("Empty results, batch #%s", iteration)
            # TODO: add logic to fillna prediction data so it will line up with feature data and
            # we can at least send that but for now just skip the batch entirely.
            continue

        # Only if we've made it this far, can we add the mini-batch to our combined results
        incoming.append(df)
        results.append(predictions)
    combined_predictions = pd.concat(results) if results else pd.DataFrame()
    combined_scoring_data = pd.concat(incoming) if incoming else pd.DataFrame()

    report_service_health_via_tracking_agent(  # noqa: F821
        mlops_sdk, start_time, combined_predictions
    )
    # If the combined scoring data is empty then that means this run completely failed so
    # no need to attempt to report any prediction data back to MLOps.
    if not combined_scoring_data.empty:
        report_predictions_data_via_tracking_agent(  # noqa: F821
            mlops_sdk,
            model,
            combined_predictions,
            combined_scoring_data,
            params,
            max_unaggregated_rows=MAX_RAW_ROWS,
        )
    return combined_predictions


def get_custom_output_file_path(input_dataset_path: str, output_file_ext: str):
    """
    An output file name must be unique to prevent files corruption by a parallel write
    from multiple batch nodes.
    """
    input_file_name_no_ext = Path(input_dataset_path).stem
    output_file_name = f"{input_file_name_no_ext}.{output_file_ext}"
    output_file_path = os.path.join(OUTPUT_PATH, output_file_name)
    if not os.path.exists(output_file_path):
        return output_file_path

    # if file exists, append a random suffix to the name to prevent parallel write
    suffix_length = 5
    random_suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=suffix_length))
    unique_output_file_name = f"{input_file_name_no_ext}-{random_suffix}.{output_file_ext}"
    return os.path.join(OUTPUT_PATH, unique_output_file_name)
