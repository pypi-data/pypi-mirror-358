#  --------------------------------------------------------------------------------
#  Copyright (c) 2024 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2024.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#
#  --------------------------------------------------------------------------------
from schema import And
from schema import Optional
from schema import Schema


class ModelPackageInfo:
    """
    A wrapper for the model package info dict (from model pacakge details YAML)
    """

    def __init__(self, model_package_details: dict):
        schema = Schema(
            {
                "id": And(str, len),
                Optional("target", default={}): dict,
            },
            ignore_extra_keys=True,
        )
        self._model_package_info = schema.validate(model_package_details)

    @property
    def id(self):
        return self._model_package_info["id"]

    @property
    def target_type(self):
        return self._model_package_info["target"].get("type", "").lower()

    @property
    def class_names(self):
        return self._model_package_info["target"].get("classNames", [])
