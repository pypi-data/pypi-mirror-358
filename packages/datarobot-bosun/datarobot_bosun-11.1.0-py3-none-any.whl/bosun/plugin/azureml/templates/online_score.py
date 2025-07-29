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
import http.client as http_codes
import logging
import os
import time
from pathlib import Path
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union

import pandas as pd
from azureml.contrib.services.aml_request import AMLRequest
from azureml.contrib.services.aml_request import rawhttp
from azureml.contrib.services.aml_response import AMLResponse
from datarobot_predict.scoring_code import ModelType
from datarobot_predict.scoring_code import ScoringCodeModel
from pydantic import BaseModel
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import abort

from datarobot_mlops.mlops import MLOps

MODEL_PATH = Path(os.environ["AZUREML_MODEL_DIR"]) / os.environ["DATAROBOT_MODEL_FILENAME"]


model = None
mlops_sdk = None


def init():
    global model, mlops_sdk
    set_java_home()  # noqa: F821
    model, model_id = load_model(MODEL_PATH)  # noqa: F821
    mlops_sdk = get_mlops(model_id=model_id)  # noqa: F821


@rawhttp
def run(request: AMLRequest):
    # TODO: would be nice if we could start the clock at the very beginning of
    # the request but we would need to utilize @app.before_request()
    start_time = time.monotonic_ns()

    param_validator = (
        TSModelParams  # noqa: F821
        if model.model_type == ModelType.TIME_SERIES
        else GenericModelParams  # noqa: F821
    )

    try:
        if request.mimetype == "text/csv":
            df, params = _handle_csv_content(request, model, param_validator)
        elif request.mimetype == "application/json":
            df, params = _handle_json_content(request, param_validator)
        else:
            msg = 'Unsupported Content-Type; please use "application/json" or "text/csv"'
            status_code = http_codes.UNPROCESSABLE_ENTITY
            report_prediction_server_error_via_tracking_agent(  # noqa: F821
                mlops_sdk,
                msg,
                status_code,
            )
            return AMLResponse(msg, status_code)
    except HTTPException as err:
        logging.exception("Aborted while processing request")
        report_prediction_server_error_via_tracking_agent(  # noqa: F821
            mlops_sdk,
            err.response.response[0].decode("UTF-8"),
            err.code,
        )
        return err.response
    except ValidationError as err:
        logging.exception("User param validation failed")
        msg = f"Request parameters are incorrect: {err}"
        status_code = http_codes.UNPROCESSABLE_ENTITY
        report_prediction_server_error_via_tracking_agent(  # noqa: F821
            mlops_sdk,
            msg,
            status_code,
        )
        return AMLResponse(msg, status_code)

    return make_prediction(model, df, params, mlops_sdk, start_time)


def _handle_json_content(
    request: AMLRequest, param_validator: Type[BaseModel]
) -> Tuple[pd.DataFrame, BaseModel]:
    # To avoid confusion, don't support both query params and params from the JSON payload.
    if request.args:
        abort(
            AMLResponse(
                'Query parameters are not supported for "application/json" Content-Type',
                http_codes.UNPROCESSABLE_ENTITY,
            )
        )
    if (
        not (input_data := request.json.get("inputData"))
        or not isinstance(input_data, dict)
        or not all(field in input_data for field in ("columns", "index", "data"))
    ):
        abort(
            AMLResponse(
                '"inputData" field is missing from the payload or not in the correct format.'
                ' The payload should be of the form: {"inputData": df.to_dict(orient="split")}',
                http_codes.UNPROCESSABLE_ENTITY,
            )
        )

    inference_data = request.json.pop("inputData")
    df = pd.DataFrame(**inference_data)
    params = param_validator.parse_obj(request.json)
    return df, params


def _handle_csv_content(
    request: AMLRequest, model: ScoringCodeModel, param_validator: Type[BaseModel]
) -> Tuple[pd.DataFrame, BaseModel]:
    try:
        df = pd.read_csv(request.stream, dtype=model.features)
    except pd.errors.ParserError as err:
        abort(AMLResponse(f"CSV input is malformed: {err}", http_codes.BAD_REQUEST))
    params = param_validator.parse_obj(request.args)
    return df, params


def make_prediction(
    model: ScoringCodeModel,
    scoring_data: pd.DataFrame,
    params: BaseModel,
    mlops_sdk: Optional[MLOps],
    start_time: int,
) -> Union[dict, AMLResponse]:

    try:
        results = model.predict(scoring_data, **params.dict())
    except Exception as err:
        logging.exception("Failed to make prediction")
        msg = f"Unable to compute prediction with given params: {err}"
        status_code = http_codes.UNPROCESSABLE_ENTITY
        report_prediction_server_error_via_tracking_agent(mlops_sdk, msg, status_code)  # noqa: F821
        return AMLResponse(msg, status_code)

    report_service_health_via_tracking_agent(mlops_sdk, start_time, results)  # noqa: F821
    report_predictions_data_via_tracking_agent(  # noqa: F821
        mlops_sdk, model, results, scoring_data, params
    )
    return results.to_dict(orient="list")
