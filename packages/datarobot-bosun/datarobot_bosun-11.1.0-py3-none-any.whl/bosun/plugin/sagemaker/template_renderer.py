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
import os
from typing import Dict
from typing import Optional

import jinja2
from jinja2 import ChoiceLoader
from jinja2 import FileSystemLoader
from jinja2 import PackageLoader


class TemplateRenderer:
    PACKAGE_NAME = "bosun.plugin.sagemaker"

    def __init__(self):
        loader = ChoiceLoader(
            [
                FileSystemLoader(
                    os.environ.get("BOSUN_SAGEMAKER_TEMPLATE_DIR", "/override/templates/")
                ),
                PackageLoader(self.PACKAGE_NAME),
            ]
        )
        self.template_env = jinja2.Environment(
            loader=loader, undefined=jinja2.StrictUndefined, autoescape=True
        )

    @property
    def TEMPLATE_NAME(self) -> str:
        raise NotImplementedError("Subclasses need to override this")

    def context(self) -> Dict[str, Optional[str]]:
        return {}

    def render(self) -> str:
        template = self.template_env.get_template(self.TEMPLATE_NAME)
        return template.render(**self.context())


class CustomModelBuildSnippet(TemplateRenderer):
    MODEL_TYPE_NAME = "custom_inference_model"
    TEMPLATE_NAME = "custom_inference_model.yaml.j2"


class ScoringCodeBuildSnippet(TemplateRenderer):
    MODEL_TYPE_NAME = "datarobot_scoring_code"
    TEMPLATE_NAME = "datarobot_scoring_code_drum.yaml.j2"
