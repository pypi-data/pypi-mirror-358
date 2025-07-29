#  --------------------------------------------------------------------------------
#  Copyright (c) 2023 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2023.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#
#  --------------------------------------------------------------------------------
import datetime
from typing import Any
from typing import Dict
from typing import Optional as Nullable

import yaml
from dateutil.parser import parser
from schema import And
from schema import Optional
from schema import Or
from schema import Schema
from schema import Use


class EndpointInfo:
    """
    A wrapper for the endpoint info dict (from the endpoint info YAML)
    """

    def __init__(self, endpoint_info: Dict[str, Any]):
        schema = Schema(
            {
                "name": str,
                "endpointType": And(str, len),
                "predictionEnvironmentId": And(str, len),
                Optional("description"): Or(None, str),
                Optional("authType"): Or(None, str),
                Optional("tags", default={}): Or(None, dict),
                Optional("trafficSplit", default={}): Or(None, dict),
                # optional for backwards compatibility
                Optional("id"): Or(None, str),
                Optional("trafficUpdatedAt"): Or(None, Use(parser().parse)),
            },
            ignore_extra_keys=True,
        )

        self._endpoint_info = schema.validate(endpoint_info)

    def to_yaml(self) -> str:
        return yaml.safe_dump(self._endpoint_info, indent=4)

    def __str__(self):
        return self.to_yaml()

    @property
    def id(self) -> str:
        return self._endpoint_info.get("id")

    @property
    def name(self) -> str:
        return self._endpoint_info["name"]

    @property
    def description(self) -> Nullable[str]:
        return self._endpoint_info.get("description")

    @property
    def type(self) -> str:
        return self._endpoint_info["endpointType"]

    @property
    def prediction_environment_id(self) -> str:
        return self._endpoint_info["predictionEnvironmentId"]

    @property
    def auth_type(self) -> str:
        return self._endpoint_info["authType"]

    @property
    def tags(self) -> Nullable[dict]:
        return self._endpoint_info.get("tags")

    @property
    def traffic_split(self) -> Nullable[dict]:
        return self._endpoint_info.get("trafficSplit")

    @property
    def traffic_updated_at(self) -> Nullable[datetime.datetime]:
        return self._endpoint_info.get("trafficUpdatedAt")
