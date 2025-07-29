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
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from datarobot_mlops.metric import AggregationHelper


class DeploymentUtils:
    @classmethod
    def _read_json_file(cls, json_file_path: Path) -> Dict[str, Any]:
        assert json_file_path
        if json_file_path.is_file():
            # file exists
            with open(json_file_path, "r") as source_file:
                json_data = json.load(source_file)
                return json_data
        else:
            raise ValueError("provided file path doesnt exist")

    @classmethod
    def load_feature_types(cls, feature_types_file: Path) -> Dict[str, Optional[str]]:
        """
        Reading feature_types from a json file
        """
        json_data = cls._read_json_file(feature_types_file)
        # MLOps monitoring library requires all feature data to be in a different format from what
        # the public API outputs.
        feature_types = [AggregationHelper.convert_feature_format(f) for f in json_data["data"]]
        return feature_types

    @classmethod
    def load_deployment_settings(cls, deployment_settings_file: Path) -> Dict[str, Any]:
        """
        utility method to read deployment settings from a json file
        """
        return cls._read_json_file(deployment_settings_file)

    @classmethod
    def create_class_labels_file(cls, dest_dir: Path, class_labels: List[str]) -> Path:
        """
        Creates classLabels.txt file that contains class labels required for DRUM in case of multiclass model.
        """
        assert dest_dir
        target_path = dest_dir / "classLabels.txt"
        with open(target_path, mode="w") as class_labels_file:
            class_labels_file.write("\n".join(class_labels))
        return target_path
