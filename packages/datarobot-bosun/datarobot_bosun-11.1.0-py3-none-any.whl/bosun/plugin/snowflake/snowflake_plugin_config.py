#  ---------------------------------------------------------------------------------
#  Copyright (c) 2022 DataRobot, Inc. and its affiliates. All rights reserved.
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
from typing import Optional as Nullable
from typing import Union

import yaml
from schema import Optional
from schema import Or
from schema import Schema

from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.pe_info import PEInfo


class SnowflakePluginConfig:
    AUTH_TYPE = "authType"
    OAUTH_TOKEN = "oauthToken"
    ACCOUNT = "account"
    WAREHOUSE = "warehouse"
    DATABASE = "database"
    SCHEMA = "schema"

    UDF_SCORING_HANDLER = "udfScoringHandler"
    UDF_FUNCTION_PREFIX = "udfFunctionPrefix"
    UDF_RETURN_TYPE = "udfReturnType"
    UDF_SCORING_METHOD_PARAMS = "udfScoringMethodParams"

    USER = "user"
    PASSWORD = "password"

    DEPLOYMENT_ID = "deploymentId"

    PREDICTION_ENV_ID = "predictionEnvId"

    config_keys = [
        AUTH_TYPE,
        OAUTH_TOKEN,
        ACCOUNT,
        WAREHOUSE,
        DATABASE,
        SCHEMA,
        UDF_SCORING_HANDLER,
        UDF_FUNCTION_PREFIX,
        UDF_RETURN_TYPE,
        UDF_SCORING_METHOD_PARAMS,
        USER,
        PASSWORD,
    ]

    config_schema = Schema(
        {
            # per prediction environment, set by file config or env variables
            Optional(OAUTH_TOKEN): Or(None, str),
            Optional(AUTH_TYPE): Or(None, str),
            Optional(USER): Or(None, str),
            Optional(PASSWORD): Or(None, str),
            ACCOUNT: str,
            WAREHOUSE: str,
            DATABASE: str,
            SCHEMA: str,
        },
        ignore_extra_keys=True,
    )

    def __init__(self, plugin_config):
        self._config = plugin_config

    def validate_config(self):
        self.config_schema.validate(self._config)

        if self.auth_type == "oauth" and self.oauth_token is None:
            raise ValueError("OAuth authentication requires a valid access token.")

        if self.auth_type is None and self.user is None:
            raise ValueError(
                "Specify authentication configuration: auth_type/oauth_token or user/password."
            )

    @classmethod
    def read_config(
        cls,
        pe_info: Nullable[PEInfo],
        config_file_path: Nullable[str] = None,
        deployment: Nullable[Union[DeploymentInfo, str]] = None,
    ):
        config = {}

        if config_file_path:
            with open(config_file_path) as conf_file:
                config = yaml.safe_load(conf_file)

        # override configuration with env variables
        for key in cls.config_keys:
            if key in os.environ:
                config[key] = os.environ[key]

        if pe_info:
            config[cls.PREDICTION_ENV_ID] = pe_info.id

        if isinstance(deployment, DeploymentInfo):
            config[cls.DEPLOYMENT_ID] = deployment.id

            # Set configuration from Deployment KV config
            if deployment.kv_config:
                for key in cls.config_keys:
                    if key in deployment.kv_config:
                        config[key] = deployment.kv_config[key]
        elif deployment:
            config[cls.DEPLOYMENT_ID] = deployment

        return SnowflakePluginConfig(config)

    @property
    def account(self):
        return self._config.get(SnowflakePluginConfig.ACCOUNT)

    @property
    def warehouse(self):
        return self._config.get(SnowflakePluginConfig.WAREHOUSE)

    @property
    def database(self):
        return self._config.get(SnowflakePluginConfig.DATABASE)

    @property
    def schema(self):
        return self._config.get(SnowflakePluginConfig.SCHEMA)

    @property
    def udf_scoring_handler(self):
        return self._config.get(SnowflakePluginConfig.UDF_SCORING_HANDLER)

    @property
    def udf_scoring_method_params(self):
        return self._config.get(SnowflakePluginConfig.UDF_SCORING_METHOD_PARAMS)

    @property
    def udf_return_type(self):
        return self._config.get(SnowflakePluginConfig.UDF_RETURN_TYPE)

    @property
    def udf_function_name(self):
        deployment_id = self._config.get(SnowflakePluginConfig.DEPLOYMENT_ID)
        func_name = "{udf_prefix}_{deployment_id}".format(
            udf_prefix=self.udf_function_prefix,
            deployment_id=deployment_id,
        )
        return func_name

    @property
    def udf_function_prefix(self):
        return self._config.get(SnowflakePluginConfig.UDF_FUNCTION_PREFIX, "datarobot_deployment")

    @property
    def auth_type(self):
        return self._config.get(SnowflakePluginConfig.AUTH_TYPE, None)

    @property
    def oauth_token(self):
        return self._config.get(SnowflakePluginConfig.OAUTH_TOKEN, None)

    @property
    def user(self):
        return self._config.get(SnowflakePluginConfig.USER)

    @property
    def password(self):
        return self._config.get(SnowflakePluginConfig.PASSWORD)

    @property
    def prediction_environment_id(self):
        return self._config.get(SnowflakePluginConfig.PREDICTION_ENV_ID)
