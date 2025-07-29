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
import re
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.pe_info import PEInfo
from bosun.plugin.sagemaker.template_renderer import CustomModelBuildSnippet
from bosun.plugin.sagemaker.template_renderer import ScoringCodeBuildSnippet

AWS_RESOURCE_ARN_SPLIT_LEN = 6
AWS_CODEBUILD_TEMPLATE_DIR = Path(__file__).parent.parent / "build_spec_templates/"


class AwsUtils:
    @staticmethod
    def parse_aws_arn(arn):
        """
        Utility method for parsing aws resource ARN:
        http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
        """
        if "ResourceARN" in arn:
            elements = arn.get("ResourceARN").split(":", 5)
            if len(elements) == AWS_RESOURCE_ARN_SPLIT_LEN:
                result = {
                    "arn": elements[0],
                    "partition": elements[1],
                    "service": elements[2],
                    "region": elements[3],
                    "account": elements[4],
                    "resource": elements[5],
                    "resource_type": None,
                }
                if "/" in result["resource"]:
                    result["resource_type"], result["resource"] = result["resource"].split("/", 1)
                elif ":" in result["resource"]:
                    result["resource_type"], result["resource"] = result["resource"].split(":", 1)
                return result
        return None

    @staticmethod
    def aws_resource_name(resource_name, resource_id):
        """
        creating AWS-compatible unique name for the deployment:
        """
        # TODO: fix other possible cases
        return (
            "datarobot-"
            + resource_name.lower().strip().replace(" ", "-").replace("_", "-")
            + "-"
            + resource_id
        )

    @staticmethod
    def aws_endpoint_config_variant_name(deployment_id, model_id):
        """
        creating AWS-compatible unique name for the endpoint configuration variant:
        """
        return f"datarobot-{deployment_id}-{model_id}"

    @classmethod
    def get_build_config(cls, codebuild_template_name: str) -> Dict[str, Any]:
        """
        Loading AWS CodeBuild template to prepare image and model artifact for SageMaker deployment
        """
        if codebuild_template_name == CustomModelBuildSnippet.MODEL_TYPE_NAME:
            return CustomModelBuildSnippet().render()
        elif codebuild_template_name == ScoringCodeBuildSnippet.MODEL_TYPE_NAME:
            return ScoringCodeBuildSnippet().render()


PREDICTION_ENVIRONMENT_PREFIX = "datarobot-pe"
DATAROBOT_DEPLOYMENT_PREFIX = "datarobot-deployment"
DATAROBOT_MODEL_PREFIX = "datarobot-model"
# The tag key must be a minimum of 0 and a maximum of 128 Unicode characters in UTF-8.
AWS_TAG_KEY_MAX_LENGTH = 127

# The tag value must be a minimum of 0 and a maximum of 256 Unicode characters in UTF-8.
AWS_TAG_VALUE_MAX_LENGTH = 255
AWS_TAGS_VALUE_REGEX = r"^[a-zA-Z0-9](-*[a-zA-Z0-9])*$"


class SageMakerTag(Enum):
    DATAROBOT_PREDICTION_ENVIRONMENT_TAG = "DATAROBOT_PREDICTION_ENVIRONMENT"
    DATAROBOT_DEPLOYMENT_TAG = "DATAROBOT_DEPLOYMENT"
    DATAROBOT_MODEL_TAG = "DATAROBOT_MODEL"
    DATAROBOT_NEW_MODEL_TAG = "DATAROBOT_NEW_MODEL"
    CUSTOM_TAGS = "CUSTOM_TAGS"


class SageMakerRecourseFilter(Enum):
    SAGEMAKER_MODEL_FILTER = "sagemaker:model"
    SAGEMAKER_ENDPOINT_FILTER = "sagemaker:endpoint"


class AwsTagsBuilder:
    def __init__(
        self, pe_info: PEInfo, di: DeploymentInfo = None, custom_tags: Dict[str, str] = None
    ):

        self.aws_tags = {}

        self.add_aws_tag(
            SageMakerTag.DATAROBOT_PREDICTION_ENVIRONMENT_TAG,
            f"{PREDICTION_ENVIRONMENT_PREFIX}-{pe_info.id}",
            pe_info.name,
        )

        if custom_tags is not None:
            for custom_tag_key, custom_tag_value in custom_tags.items():
                self.add_aws_tag(SageMakerTag.CUSTOM_TAGS, custom_tag_key, custom_tag_value)

        if di is not None:
            self.add_aws_tag(
                SageMakerTag.DATAROBOT_DEPLOYMENT_TAG,
                f"{DATAROBOT_DEPLOYMENT_PREFIX}-{di.id}",
                di.name,
            )
            self.add_aws_tag(
                SageMakerTag.DATAROBOT_MODEL_TAG,
                f"{DATAROBOT_MODEL_PREFIX}-{di.model_id}",
                di.model_name,
            )
            if di.new_model_id is not None:
                self.add_aws_tag(
                    SageMakerTag.DATAROBOT_NEW_MODEL_TAG,
                    f"{DATAROBOT_MODEL_PREFIX}-{di.new_model_id}",
                    di.model_name,
                )

    def get_tags(self, *tag_ids) -> List[Dict[str, str]]:
        return [tag for tag_id in tag_ids for tag in self.aws_tags.get(tag_id, [])]

    def get_tags_kv_lowercase(self, *tag_ids) -> List[Dict[str, str]]:
        # Some AWS services required tags with lowercase 'key' and 'value'
        return [
            {"key": tag_element["Key"], "value": tag_element["Value"]}
            for tag_id in tag_ids
            for tag_element in self.aws_tags.get(tag_id, [])
        ]

    def get_tags_key_lowercase(self, *tag_ids) -> List[Dict[str, str]]:
        # Some AWS services required tags with lowercase 'key'
        return [
            {"key": tag_element["Key"]}
            for tag_id in tag_ids
            for tag_element in self.aws_tags.get(tag_id, [])
        ]

    def get_tag_keys(self, *tag_ids) -> List[Dict[str, str]]:
        return [
            {"Key": tag_element["Key"]}
            for tag_id in tag_ids
            for tag_element in self.aws_tags.get(tag_id, [])
        ]

    def validate_aws_tag_key(self, input_string):
        """
        Validates the input string against the aws tag key constrains
        If the input string does not match, throwing exception
        :param input_string: The string to be validated as aws tag key.
        :return: The original string if valid
        """

        # Check if the input string matches the pattern
        is_valid = re.match(AWS_TAGS_VALUE_REGEX, input_string) is not None

        if is_valid and 1 <= len(input_string) <= AWS_TAG_KEY_MAX_LENGTH:
            return input_string
        else:
            raise ValueError("Error: The specified tag key is not valid")

    def prepare_aws_tag_value(self, input_string):
        """
        Validates the input string against the aws tag value constrains
        If the input string does not match, it removes all illegal characters
        and cut it to make sure it is valid
        :param input_string: The string to be validated and cleaned.
        :return: The original string if valid, otherwise the cleaned string.
        """
        # Check if the input string matches tag value constrains
        is_valid = re.match(AWS_TAGS_VALUE_REGEX, input_string) is not None

        if is_valid and len(input_string) < AWS_TAG_VALUE_MAX_LENGTH:
            return input_string
        else:
            # Remove illegal characters
            cleaned_string = re.sub(r"[^a-zA-Z0-9-]", "", input_string)
            # Remove multiple consecutive hyphens
            cleaned_string = re.sub(r"-+", "-", cleaned_string)
            cut_string = cleaned_string[:AWS_TAG_VALUE_MAX_LENGTH]
            return cut_string

    def add_aws_tag(self, tag_name, aws_tag_key, aws_tag_value=None):
        tag_record = {
            "Key": self.validate_aws_tag_key(aws_tag_key),
            "Value": (
                self.prepare_aws_tag_value(aws_tag_value) if aws_tag_value is not None else None
            ),
        }
        self.aws_tags.setdefault(tag_name, []).append(tag_record)
