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


import logging
import os
import random
import re
import string
from datetime import timedelta
from functools import cached_property
from pathlib import Path
from typing import Dict
from typing import Optional as Nullable

import yaml
from dateutil import parser
from schema import And
from schema import Optional
from schema import Or
from schema import Schema
from schema import SchemaError
from schema import Use

from bosun.plugin.azureml.config.config_keys import EndpointType
from bosun.plugin.azureml.config.config_keys import Key
from bosun.plugin.constants import BosunPluginConfigConstants
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.pe_info import PEInfo
from datarobot_mlops.common.version_util import DataRobotAppVersion

logger = logging.getLogger(__name__)

# Check for updates at:
# https://mcr.microsoft.com/en-us/product/azureml/minimal-ubuntu20.04-py38-cpu-inference/tags
AZURE_BASE_ENVIRONMENT = (
    "mcr.microsoft.com/azureml/minimal-ubuntu20.04-py38-cpu-inference:20240122.v1"
)
AZURE_TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
CONDA_FILE_PATH = AZURE_TEMPLATE_DIR / "conda.yml"

ENDPOINT_NAME_PATTERN = re.compile(r"[a-z]+[a-z0-9-]*")


def output_action_validator(value):
    allowed_values = {"AppendRow", "SummaryOnly"}
    parts = value.split(" ")
    result = "".join(part.capitalize() for part in parts)
    if result not in allowed_values:
        raise SchemaError(None, errors=f"Output action allowed values: [{allowed_values}]")
    return result


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
    return kv_validator(tags, Key.AZURE_ENVIRONMENT_TAGS)


def traffic_validator(traffic_settings):
    return kv_validator(traffic_settings, Key.ENDPOINT_TRAFFIC)


class EndpointConfig:
    # besides of type validation, converts numeric string to int
    optional_int_type = Or(None, Use(int), int)
    optional_float_type = Or(None, Use(float), float)

    base_config_schema = {
        # required subscription/workspace keys
        Key.AZURE_SUBSCRIPTION_ID.name: str,
        Key.AZURE_RESOURCE_GROUP.name: str,
        Key.AZURE_WORKSPACE.name: str,
        Key.AZURE_LOCATION.name: str,
        # optional
        Optional(Key.ENDPOINT_TRAFFIC.name, default={}): Or(None, Use(traffic_validator)),
        Optional(Key.ENDPOINT_TRAFFIC_LAST_MODIFIED_AT.name): Or(None, Use(parser.parse)),
        Optional(Key.AZURE_ENVIRONMENT_TAGS.name, default={}): Or(None, Use(tags_validator)),
        Optional(Key.AZURE_EVENTHUBS_NAMESPACE.name): Or(None, And(str, len)),
        Optional(Key.AZURE_EVENTHUBS_INSTANCE.name): Or(None, And(str, len)),
        Optional(Key.LOGGING_LEVEL.name, default="info"): Or(None, str),
        Optional(Key.DEPLOYMENT_LOG_LINES_COUNT.name, default=100): optional_int_type,
        Optional(
            Key.SCORING_TIMEOUT_SECONDS.name, default=timedelta(seconds=90).total_seconds()
        ): optional_int_type,
        # MLOps imposes a strict 30 min max on all actions so make sure we are under that.
        Optional(
            Key.ENDPOINT_DEPLOYMENT_TIMEOUT.name, default=timedelta(minutes=27.5).total_seconds()
        ): optional_int_type,
        Optional(
            Key.ENDPOINT_DELETION_TIMEOUT.name, default=timedelta(minutes=28).total_seconds()
        ): optional_int_type,
        Optional(
            Key.ENDPOINT_UPDATE_TIMEOUT.name, default=timedelta(minutes=15).total_seconds()
        ): optional_int_type,
        Optional(
            Key.DEPLOYMENT_DELETION_TIMEOUT.name, default=timedelta(minutes=15).total_seconds()
        ): optional_int_type,
        Optional(
            Key.ENDPOINT_CREATION_TIMEOUT.name, default=timedelta(minutes=10).total_seconds()
        ): optional_int_type,
        Optional(Key.AZURE_LOCAL_TESTING.name, default=False): bool,
        Optional(Key.AZURE_MANAGED_IDENTITY_CLIENT_ID.name): Or(None, And(str, len)),
        # prediction explanations settings
        Optional(Key.MAX_EXPLANATIONS.name, default=3): optional_int_type,
        Optional(Key.THRESHOLD_HIGH.name): optional_float_type,
        Optional(Key.THRESHOLD_LOW.name): optional_float_type,
    }

    online_endpoint_schema = {
        **base_config_schema,
        Key.ENDPOINT_NAME.name: str,
        Key.DEPLOYMENT_NAME.name: str,
        Key.COMPUTE_VIRTUAL_MACHINE.name: str,
        Optional(Key.ENDPOINT_TYPE.name): And(Use(EndpointType), EndpointType.ONLINE),
        Optional(Key.COMPUTE_INSTANCE_COUNT.name, default=1): optional_int_type,
        Optional(Key.AZURE_MANAGED_IDENTITY_ID.name): Or(None, And(str, len)),
    }

    batch_endpoint_schema = {
        **base_config_schema,
        Key.ENDPOINT_NAME.name: str,
        Key.DEPLOYMENT_NAME.name: str,
        Key.COMPUTE_CLUSTER.name: str,
        Key.COMPUTE_CLUSTER_INSTANCE_COUNT.name: Use(int),
        Optional(Key.ENDPOINT_TYPE.name): And(Use(EndpointType), EndpointType.BATCH),
        Optional(Key.OUTPUT_ACTION.name, default="AppendRow"): Or(
            None, Use(output_action_validator)
        ),
        Optional(Key.OUTPUT_FILE_NAME.name, default="predictions.csv"): Or(None, str),
        Optional(Key.MINI_BATCH_SIZE.name, default=1): optional_int_type,
        Optional(Key.MAX_RETRIES.name, default=3): optional_int_type,
        Optional(Key.MAX_CONCURRENCY_PER_INSTANCE.name, default=1): optional_int_type,
        Optional(Key.ERROR_THRESHOLD.name, default=-1): optional_int_type,
        Optional(Key.AZURE_LOCAL_TESTING.name, default=False): False,  # batch doesn't support local
        # custom output format (CSV, parquet)
        Optional(Key.OUTPUT_FORMAT.name): Or(None, And(str, len)),
    }

    configs = {
        EndpointType.ONLINE: Schema(online_endpoint_schema, ignore_extra_keys=True),
        EndpointType.BATCH: Schema(batch_endpoint_schema, ignore_extra_keys=True),
        EndpointType.UNKNOWN: Schema(base_config_schema, ignore_extra_keys=True),
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

        # Check to see if required config keys are set to enable monitoring.
        if self._bosun_config[
            BosunPluginConfigConstants.MLOPS_BOSUN_PRED_ENV_ENABLE_MONITORING_KEY
        ]:
            if not self[Key.AZURE_MANAGED_IDENTITY_CLIENT_ID]:
                # This is not an error because we currently don't pass if monitoring enabled
                # on the PE level so we use this config to infer if it is enabled or not.
                logger.info(
                    "Monitoring will be disabled because %s is not set",
                    Key.AZURE_MANAGED_IDENTITY_CLIENT_ID.name,
                )
            elif self.is_online_endpoint and not self[Key.AZURE_MANAGED_IDENTITY_ID]:
                raise ValueError(
                    f"Monitoring requires {Key.AZURE_MANAGED_IDENTITY_ID.name} to be set"
                )

    @classmethod
    def read_config(
        cls,
        parent_config: Dict,
        config_file_path: Nullable[str] = None,
        prediction_environment: Nullable[PEInfo] = None,
        deployment: Nullable[DeploymentInfo] = None,
        is_model_replacement: bool = False,
    ) -> "EndpointConfig":
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

        config = EndpointConfig(
            config, parent_config, prediction_environment, deployment, is_model_replacement
        )
        config.validate_config()
        return config

    @property
    def _config(self):
        return self._transformed_config or self._original_config

    @property
    def is_monitoring_enabled(self):
        return bool(
            self._bosun_config[
                BosunPluginConfigConstants.MLOPS_BOSUN_PRED_ENV_ENABLE_MONITORING_KEY
            ]
            and self[Key.AZURE_MANAGED_IDENTITY_CLIENT_ID]
        )

    @property
    def endpoint_type(self) -> EndpointType:
        endpoint_type_str = self._config.get(Key.ENDPOINT_TYPE.name)
        return EndpointType(endpoint_type_str)

    @property
    def is_online_endpoint(self):
        if self.endpoint_type:
            return self.endpoint_type == EndpointType.ONLINE

        online_endpoint_keys = {Key.COMPUTE_VIRTUAL_MACHINE.name, Key.COMPUTE_INSTANCE_COUNT.name}

        return any(key in self._config for key in online_endpoint_keys)

    @property
    def conda_yaml(self) -> Dict:
        with open(CONDA_FILE_PATH) as config_f:
            return yaml.safe_load(config_f)

    @property
    def environment_name(self) -> str:
        return self.conda_yaml.get("name")

    @property
    def environment_version(self) -> DataRobotAppVersion:
        """
        We use a semantic versioning to track environment updates and warn users to re-launch their
        deployments on Major version changes.

        Users may manually create a new version built from our custom environment version. AzureML
        uses integer increments for versioning. E.g:

        Consider a custom environment with 4 versions built:
        #   Version     Conda version       Comment
        1.  1.0.1       1.0.1               Built by an older MA instance
        2.  1           1.0.1               Built by user
        3.  2           1.0.1               Built by user
        4.  2.0.0       2.0.0               Built by a newer MA instance

        AzureML plugin v1.0.1 will use environment #3 (version 2) for the next deployment.
        AzureML plugin v2.0.0 will use environment #4 (version 2.0.0) for the next deployment.

        NOTE:
         1. Change of the major version will trigger a warning deployment status for all
            the deployments using an older env version.
         2. No warnings triggered for minor/patch version changes.
        """
        conda_version = self.conda_yaml.get("version")
        return DataRobotAppVersion(conda_version)

    @property
    def is_batch_endpoint(self):
        if self.endpoint_type:
            return self.endpoint_type == EndpointType.BATCH

        batch_endpoint_keys = {Key.COMPUTE_CLUSTER.name, Key.COMPUTE_CLUSTER_INSTANCE_COUNT.name}

        return any(key in self._config for key in batch_endpoint_keys)

    @cached_property
    def new_deployment_name(self):
        # TODO check if a generated deployment_name is not taken in endpoint
        """In case of model replacements, a new unique deployment name is required."""
        user_set_deployment_name = self._config.get(Key.DEPLOYMENT_NAME.name, "")
        return self.generate_default_name(user_set_deployment_name)

    @staticmethod
    def generate_default_name(prefix, postfix_length=5):
        if not ENDPOINT_NAME_PATTERN.match(prefix):
            raise ValueError(
                "Names must begin with a lowercase letter, followed by lowercase letters,"
                " numbers or hyphen."
            )

        max_name_len = 32
        trim_name = max_name_len - postfix_length - 1  # minus the dash symbol
        postfix = "".join(random.choice(string.ascii_lowercase) for _ in range(postfix_length))
        return f"{prefix[:trim_name]}-{postfix}"
