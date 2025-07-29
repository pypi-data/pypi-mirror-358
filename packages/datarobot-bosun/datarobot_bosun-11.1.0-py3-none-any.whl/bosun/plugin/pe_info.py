#  --------------------------------------------------------------------------------
#  Copyright (c) 2021 DataRobot, Inc. and its affiliates. All rights reserved.
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

from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional as Nullable

import dateutil.parser
import yaml
from schema import And
from schema import Optional
from schema import Or
from schema import Schema
from schema import Use

from bosun.plugin.deployment_info import DeploymentInfo


class PEInfo:
    """
    A wrapper for the PE info dict (from the PE info YAML)
    """

    def __init__(self, pe_info: Dict[str, Any]):
        schema = Schema(
            {
                "id": And(str, len),
                Optional("name"): Or(None, str),
                Optional("description"): Or(None, str),
                Optional("createdOn"): Or(None, Use(dateutil.parser.isoparse)),
                Optional("createdBy"): Or(None, str),
                Optional("deployments", default=[]): list,
                Optional("keyValueConfig", default={}): dict,
            },
            ignore_extra_keys=True,
        )

        self._pe_info = schema.validate(pe_info)

    def to_yaml(self):
        return yaml.safe_dump(self._pe_info, indent=4)

    def __str__(self):
        return self.to_yaml()

    @property
    def id(self) -> str:
        return self._pe_info["id"]

    @property
    def name(self) -> Nullable[str]:
        return self._pe_info.get("name")

    @property
    def description(self) -> Nullable[str]:
        return self._pe_info.get("description")

    @property
    def deployments(self) -> List[DeploymentInfo]:
        return [DeploymentInfo(d) for d in self._pe_info["deployments"]]

    @property
    def created_on(self) -> Nullable[datetime]:
        return self._pe_info.get("createdOn")

    @property
    def created_by(self) -> Nullable[str]:
        return self._pe_info.get("createdBy")

    @property
    def kv_config(self) -> Dict[str, Any]:
        return self._pe_info["keyValueConfig"]
