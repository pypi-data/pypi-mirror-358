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
import os
import random
import re
import string
from typing import Dict
from typing import Optional as Nullable

import yaml
from schema import Optional
from schema import Or
from schema import Schema
from schema import SchemaError
from schema import Use

from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.pe_info import PEInfo
from bosun.plugin.sagemaker.config.config_keys import Key
from bosun.plugin.sagemaker.config.config_keys import SageMakerEndpointType

SAGEMAKER_ENDPOINT_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}")


def kv_validator(kv_pairs: str, field: Key):
    """
    DataRobot UI pass key-value pairs using the following format:
    key_name1:value1;key_name2:;key_name3:value3

    key names are mandatory, values are optional.
    """
    result = {}
    validation_error = SchemaError(
        None,
        errors=f"Invalid formatting of the {field.name}. "
        f"Expected formatting: key-name1:key-value;key-name2:key-value2",
    )

    kv_pairs = kv_pairs.strip(" ;") if kv_pairs else None

    if not kv_pairs:
        return result

    try:
        for pair in kv_pairs.split(";"):
            kv = pair.split(":")
            if len(kv) != 2:
                # key value pairs are separated by ':'
                raise validation_error

            key = kv[0].strip()
            value = kv[1].strip()

            if not key:
                # empty keys are not allowed
                raise validation_error

            result[key] = value if value else None

        return result
    except ValueError:
        raise validation_error


def tags_validator(tags):
    return kv_validator(tags, Key.AWS_ENVIRONMENT_TAGS)


class SageMakerConfig:
    # besides of type validation, converts numeric string to int
    optional_int_type = Or(None, Use(int), int)
    optional_float_type = Or(None, Use(float), float)

    base_config_schema = {
        # required aws resources keys
        Key.AWS_REGION.name: str,
        Key.AWS_S3_BUCKET.name: str,
        Key.AWS_ECR_REPOSITORY.name: str,
        Optional(Key.AWS_ROLE_SAGEMAKER_ARN.name): str,
        # optional
        Optional(Key.AWS_ECR_CACHE.name, default="datarobot"): str,
        Optional(Key.MLOPS_SQS_QUEUE_URL.name): Or(None, str),
        Optional(Key.MLOPS_SQS_VISIBILITY_TIMEOUT.name, default=30): optional_int_type,
        Optional(Key.AWS_ROLE_CODEBUILD_ARN.name): Or(None, str),
        Optional(Key.AWS_ENVIRONMENT_TAGS.name, default={}): Or(None, Use(tags_validator)),
    }

    realtime_inference_schema = {
        **base_config_schema,
        Optional(Key.ENDPOINT_NAME.name): str,
        Optional(Key.ENDPOINT_TYPE.name): Or(None, SageMakerEndpointType.REALTIME.value),
        Optional(Key.COMPUTE_VIRTUAL_MACHINE.name, default="ml.m4.xlarge"): str,
        Optional(Key.COMPUTE_INSTANCE_COUNT.name, default=1): optional_int_type,
    }

    configs = {
        SageMakerEndpointType.REALTIME: Schema(realtime_inference_schema, ignore_extra_keys=True),
    }

    def __init__(
        self,
        plugin_config: Dict,
        parent_config: Dict,
        prediction_environment=None,
        deployment=None,
        is_model_replacement=False,
    ):
        # configuration is transformed after validation, by the Use class
        self._transformed_config = None
        self._original_config = plugin_config
        self._bosun_config = parent_config
        self.prediction_environment = prediction_environment
        self.deployment = deployment
        self.is_model_replacement = is_model_replacement

    def __getitem__(self, key: Key):
        return self._config.get(key.name)

    def validate_config(self):
        schema = self.configs[self.endpoint_type]
        self._transformed_config = schema.validate(self._original_config)

    @classmethod
    def read_config(
        cls,
        parent_config: Dict,
        config_file_path: Nullable[str] = None,
        prediction_environment: Nullable[PEInfo] = None,
        deployment: Nullable[DeploymentInfo] = None,
        is_model_replacement: bool = False,
    ):
        def get_kv_config(entity):
            result = {}
            if entity.kv_config:
                for key in Key.all():
                    if key in entity.kv_config:
                        result[key] = entity.kv_config[key]
            return result

        config = {}
        if config_file_path:
            with open(config_file_path) as conf_file:
                config = yaml.safe_load(conf_file)

        # override configuration with env variables
        for key in Key.all():
            if key in os.environ:
                config[key] = os.environ[key]

        if prediction_environment:
            pe_additional_metadata = get_kv_config(prediction_environment)
            config.update(pe_additional_metadata)

        if deployment:
            deployment_additional_metadata = get_kv_config(deployment)
            config.update(deployment_additional_metadata)

        config = SageMakerConfig(
            config, parent_config, prediction_environment, deployment, is_model_replacement
        )
        config.validate_config()
        return config

    @property
    def _config(self):
        return self._transformed_config or self._original_config

    @property
    def deployment_info_fields(self):
        return ["deployment_id", "model_id"]

    @property
    def endpoint_type(self) -> SageMakerEndpointType:
        # Currently only realtime inference endpoint is supported
        # TODO: add support for other inference types
        return SageMakerEndpointType.REALTIME

    @property
    def aws_region(self):
        return self[Key.AWS_REGION]

    @property
    def aws_codebuild_service_role(self):
        if self[Key.AWS_ROLE_CODEBUILD_ARN] is not None:
            return self[Key.AWS_ROLE_CODEBUILD_ARN]
        else:
            return self[Key.AWS_ROLE_SAGEMAKER_ARN]

    @property
    def aws_role_resource_arn(self):
        return self[Key.AWS_ROLE_SAGEMAKER_ARN]

    @property
    def bucket_name(self):
        return self[Key.AWS_S3_BUCKET]

    @property
    def default_model_image(self):
        return self[Key.AWS_ECR_REPOSITORY]

    @property
    def aws_ecr_cache(self):
        return self[Key.AWS_ECR_CACHE]

    @property
    def default_scoring_code_model_image(self):
        return self[Key.AWS_ECR_REPOSITORY]

    @property
    def default_initial_instance_type(self):
        return self[Key.COMPUTE_VIRTUAL_MACHINE]

    @property
    def default_initial_instance_count(self):
        return self[Key.COMPUTE_INSTANCE_COUNT]

    @property
    def get_mlops_sqs_queue_url(self):
        return self[Key.MLOPS_SQS_QUEUE_URL]

    @property
    def get_mlops_sqs_visibility_timeout(self):
        return self[Key.MLOPS_SQS_VISIBILITY_TIMEOUT]

    @property
    def get_custom_tags(self):
        return self[Key.AWS_ENVIRONMENT_TAGS]

    @staticmethod
    def generate_default_name(prefix):
        # The name of the SageMaker endpoint must be unique within an AWS Region in your AWS account.
        # The name is case-insensitive
        # Length Constraints: Maximum length of 63.
        # Pattern: ^[a-zA-Z0-9](-*[a-zA-Z0-9]){0,62}
        if not SAGEMAKER_ENDPOINT_NAME_PATTERN.match(prefix):
            raise ValueError("Names must contain only letters and numbers or hyphen")
        max_name_len = 64
        postfix = "".join(random.choice(string.ascii_lowercase) for _ in range(12))
        trim_name_len = max_name_len - len(postfix) - 1  # minus the dash symbol
        return f"{prefix[:trim_name_len]}-{postfix}"
