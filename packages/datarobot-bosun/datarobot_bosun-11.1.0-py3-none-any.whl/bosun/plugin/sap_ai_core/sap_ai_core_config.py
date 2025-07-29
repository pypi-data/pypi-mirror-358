#  ---------------------------------------------------------------------------------
#  Copyright (c) 2024 DataRobot, Inc. and its affiliates. All rights reserved.
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
from typing import Dict
from typing import Optional as Nullable
from urllib.parse import unquote
from urllib.parse import urlparse

import yaml
from schema import Optional
from schema import Or
from schema import Schema
from schema import Use

from bosun.plugin.constants import BosunPluginConfigConstants
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.pe_info import PEInfo

DEFAULT_ACTION_TIMEOUT_SEC = 60 * 25  # 25 min timeout for actions
DEFAULT_ACTION_SLEEP_TIME_SEC = 10  # 10 seconds between check
DEFAULT_SAP_RESOURCE_PLAN = "starter"
DEFAULT_REGISTRY_HOST = "https://index.docker.io"


class SapConfigKey(object):
    SAP_GITHUB_REPOSITORY = "SAP_GITHUB_REPOSITORY"
    SAP_GITHUB_REPOSITORY_PATH = "SAP_GITHUB_REPOSITORY_PATH"
    SAP_GITHUB_USERNAME = "SAP_GITHUB_USERNAME"
    SAP_GITHUB_TOKEN = "SAP_GITHUB_TOKEN"

    SAP_MAX_ACTION_TIMEOUT_SEC = "SAP_MAX_ACTION_TIMEOUT_SEC"

    DR_SECRETS_NAME = "DR_SECRETS_NAME"
    DR_IMAGE_NAME = "DR_IMAGE_NAME"
    DR_REGISTRY_SECRETS_NAME = "DR_REGISTRY_SECRETS_NAME"
    DR_REGISTRY_HOST = "DR_REGISTRY_HOST"
    DR_REGISTRY_USER = "DR_REGISTRY_USER"
    DR_REGISTRY_TOKEN = "DR_REGISTRY_TOKEN"

    DATAROBOT_PROXY_ENDPOINT = "DATAROBOT_PROXY_ENDPOINT"
    DATAROBOT_ENDPOINT = "DATAROBOT_ENDPOINT"
    DATAROBOT_API_TOKEN = "DATAROBOT_API_TOKEN"

    SAP_RESOURCE_GROUP_ID = "SAP_RESOURCE_GROUP_ID"
    SAP_SCENARIO_ID = "SAP_SCENARIO_ID"
    SAP_EXECUTABLE_ID = "SAP_EXECUTABLE_ID"

    SAP_AI_API_URL = "SAP_AI_API_URL"
    SAP_AI_AUTH_URL = "SAP_AI_AUTH_URL"
    SAP_CLIENT_ID = "SAP_CLIENT_ID"
    SAP_CLIENT_SECRET = "SAP_CLIENT_SECRET"
    SAP_RESOURCE_PLAN = "SAP_RESOURCE_PLAN"

    @classmethod
    def all(cls):
        return {k for k, v in cls.__dict__.items() if k.isupper()}


class SapAICoreConfig:

    base_config_schema = {
        SapConfigKey.SAP_RESOURCE_GROUP_ID: str,
        SapConfigKey.SAP_SCENARIO_ID: str,
        SapConfigKey.SAP_EXECUTABLE_ID: str,
        SapConfigKey.DR_SECRETS_NAME: str,
        SapConfigKey.DR_IMAGE_NAME: str,
        SapConfigKey.DATAROBOT_ENDPOINT: str,
        SapConfigKey.DATAROBOT_API_TOKEN: str,
        SapConfigKey.SAP_AI_API_URL: str,
        SapConfigKey.SAP_AI_AUTH_URL: str,
        SapConfigKey.SAP_CLIENT_ID: str,
        SapConfigKey.SAP_CLIENT_SECRET: str,
        SapConfigKey.SAP_GITHUB_REPOSITORY: str,
        SapConfigKey.SAP_GITHUB_REPOSITORY_PATH: str,
        SapConfigKey.DR_REGISTRY_SECRETS_NAME: str,
        Optional(SapConfigKey.DATAROBOT_PROXY_ENDPOINT, default=""): str,
        Optional(SapConfigKey.DR_REGISTRY_HOST, default=DEFAULT_REGISTRY_HOST): str,
        Optional(SapConfigKey.DR_REGISTRY_USER, default=""): str,
        Optional(SapConfigKey.DR_REGISTRY_TOKEN, default=""): str,
        Optional(SapConfigKey.SAP_RESOURCE_PLAN, default=DEFAULT_SAP_RESOURCE_PLAN): str,
        Optional(SapConfigKey.SAP_GITHUB_USERNAME, default=""): str,
        Optional(SapConfigKey.SAP_GITHUB_TOKEN, default=""): str,
        Optional(SapConfigKey.SAP_MAX_ACTION_TIMEOUT_SEC, default=DEFAULT_ACTION_TIMEOUT_SEC): Or(
            None, Use(int), int
        ),
    }

    base_schema = Schema(base_config_schema, ignore_extra_keys=True)

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

    def __getitem__(self, key: str):
        return self._config[key]

    def validate_config(self):
        self._transformed_config = self.base_schema.validate(self._original_config)

    @property
    def _config(self):
        return self._transformed_config or self._original_config

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
                for key in SapConfigKey.all():
                    if key in entity.kv_config:
                        result[key] = entity.kv_config[key]
            return result

        config = {}
        if config_file_path:
            with open(config_file_path) as conf_file:
                config = yaml.safe_load(conf_file)

        # override configuration with env variables
        for key in SapConfigKey.all():
            if key in os.environ:
                config[key] = os.environ[key]

        if prediction_environment:
            pe_additional_metadata = get_kv_config(prediction_environment)
            config.update(pe_additional_metadata)

        if deployment:
            deployment_additional_metadata = get_kv_config(deployment)
            config.update(deployment_additional_metadata)

        config = SapAICoreConfig(
            config, parent_config, prediction_environment, deployment, is_model_replacement
        )
        config.validate_config()
        return config

    @property
    def resource_group_id(self):
        return self[SapConfigKey.SAP_RESOURCE_GROUP_ID]

    @property
    def sap_application_name(self):
        github_repo = self[SapConfigKey.SAP_GITHUB_REPOSITORY]
        repo_path = unquote(urlparse(github_repo).path).replace(".git", "")
        return repo_path.rpartition("/")[-1]

    @property
    def github_username(self):
        return self[SapConfigKey.SAP_GITHUB_USERNAME]

    @property
    def github_token(self):
        return self[SapConfigKey.SAP_GITHUB_TOKEN]

    @property
    def max_action_timeout_min(self):
        return self[SapConfigKey.SAP_MAX_ACTION_TIMEOUT_SEC] // 60

    @property
    def is_monitoring_enabled(self):
        return self._bosun_config[
            BosunPluginConfigConstants.MLOPS_BOSUN_PRED_ENV_ENABLE_MONITORING_KEY
        ]

    @property
    def datarobot_endpoint_url(self):
        return self[SapConfigKey.DATAROBOT_PROXY_ENDPOINT] or self[SapConfigKey.DATAROBOT_ENDPOINT]

    @property
    def datarobot_secrets_name(self):
        url = unquote(urlparse(self.datarobot_endpoint_url).netloc)
        return f"{self[SapConfigKey.DR_SECRETS_NAME]}-{url}"
