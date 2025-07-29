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

from typing import Dict
from typing import Optional

from bosun.plugin.azureml.template_renderer import TemplateRenderer


class AzureMLBatchEndpointScoringSnippet(TemplateRenderer):
    SCORING_SCRIPT = "batch_score.py"
    TEMPLATE_NAME = "scoring_script_builder.py.j2"

    def __init__(self, model_filename: Optional[str] = None, csv_separator: str = ","):
        super().__init__()
        self.datarobot_model_filename = model_filename
        self.csv_separator = csv_separator

    def context(self) -> Dict[str, Optional[str]]:
        return {
            "datarobot_model_filename": self.datarobot_model_filename,
            "csv_separator": self.csv_separator,
            "score_script": self.SCORING_SCRIPT,
        }


class AzureMLOnlineEndpointScoringSnippet(AzureMLBatchEndpointScoringSnippet):
    SCORING_SCRIPT = "online_score.py"
