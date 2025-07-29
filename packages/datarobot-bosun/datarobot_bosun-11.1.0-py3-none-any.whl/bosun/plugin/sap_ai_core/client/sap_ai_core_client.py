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
import base64
import json
import logging
import time
from typing import Dict
from typing import List

import requests
from ai_api_client_sdk.exception import AIAPINotFoundException
from ai_api_client_sdk.exception import AIAPIServerException
from ai_api_client_sdk.models.deployment import Deployment
from ai_api_client_sdk.models.parameter_binding import ParameterBinding
from ai_api_client_sdk.models.status import Status
from ai_api_client_sdk.models.target_status import TargetStatus
from ai_api_client_sdk.models.version_list import VersionList
from ai_core_sdk.ai_core_v2_client import AICoreV2Client

from bosun.plugin.constants import DeploymentState
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.deployment_utils import DeploymentUtils
from bosun.plugin.model_package_info import ModelPackageInfo
from bosun.plugin.sap_ai_core.sap_ai_core_config import DEFAULT_ACTION_SLEEP_TIME_SEC
from bosun.plugin.sap_ai_core.sap_ai_core_config import SapAICoreConfig
from bosun.plugin.sap_ai_core.sap_ai_core_config import SapConfigKey as Key

DATAROBOT_PREFIX = "datarobot"


class SapAICoreClientException(Exception):
    pass


class SapAICoreClient:

    _EXTERNAL_TO_INTERNAL_STATE_MAP = {
        Status.DEAD: DeploymentState.ERROR,
        Status.RUNNING: DeploymentState.READY,
        Status.STOPPING: DeploymentState.SHUTTING_DOWN,
        Status.STOPPED: DeploymentState.STOPPED,
        Status.COMPLETED: DeploymentState.STOPPED,
        Status.PENDING: DeploymentState.LAUNCHING,
        Status.UNKNOWN: DeploymentState.UNKNOWN,
    }

    def __init__(self, config: SapAICoreConfig = None) -> None:
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._config = config

        self._client = AICoreV2Client(
            base_url=f"{self._config[Key.SAP_AI_API_URL]}/v2",
            auth_url=f"{self._config[Key.SAP_AI_AUTH_URL]}/oauth/token",
            client_id=self._config[Key.SAP_CLIENT_ID],
            client_secret=self._config[Key.SAP_CLIENT_SECRET],
            resource_group=self._config.resource_group_id,
        )

    def register_dr_secrets(self) -> None:
        """
        Register the dr secrets(DATAROBOT_ENDPOINT and DATAROBOT_API_TOKEN), currently the only
        way to register generic secrets is using API endpoints directly.
        """
        headers = {
            "Authorization": self._client.rest_client.get_token(),
            "Content-Type": "application/json",
            "AI-Resource-Group": self._config.resource_group_id,
        }
        response = requests.get(
            f"{self._config[Key.SAP_AI_API_URL]}/v2/admin/secrets", headers=headers
        )
        if response.status_code != 200:
            raise SapAICoreClientException(f"Failed to fetch secrets - {response.text}")

        # Checks if secrets with specific name already exists
        sap_secrets = response.json().get("resources", [])
        for secret in sap_secrets:
            if secret["name"] == self._config.datarobot_secrets_name:
                self._logger.warning(
                    f"Secrets with name {self._config.datarobot_secrets_name} already exists."
                )
                return

        self._logger.info(f"Registering DataRobot URL: {self._config.datarobot_endpoint_url}")
        b64_datarobot_endpoint = base64.b64encode(self._config.datarobot_endpoint_url.encode())
        b64_datarobot_api_token = base64.b64encode(self._config[Key.DATAROBOT_API_TOKEN].encode())
        data = {
            "name": self._config.datarobot_secrets_name,
            "data": {
                "DATAROBOT_ENDPOINT": b64_datarobot_endpoint.decode(),
                "DATAROBOT_API_TOKEN": b64_datarobot_api_token.decode(),
            },
        }
        response = requests.post(
            f"{self._config[Key.SAP_AI_API_URL]}/v2/admin/secrets", headers=headers, json=data
        )
        if response.status_code == 200:
            self._logger.info("Datarobot secrets registered.")
        else:
            raise SapAICoreClientException("failed to register secrets - {}".format(response.text))

    def get_version(self) -> VersionList:
        return self._client.meta.get_versions()

    def register_repository(self) -> None:
        try:
            github_repo_url = self._config[Key.SAP_GITHUB_REPOSITORY]

            # Check if repo is already register
            response = self._client.repositories.query()
            for repo in response.resources:
                if repo.url == github_repo_url:
                    self._logger.info("Repository already registered")
                    return

            response = self._client.repositories.create(
                name=self._config.sap_application_name,
                url=github_repo_url,
                username=self._config.github_username,
                password=self._config.github_token,
            )
            self._logger.debug(f"Repository successfully registered - {response.message}")
        except AIAPIServerException as e:
            msg = f"Error registering repository: {e}"
            self._logger.error(msg)
            raise SapAICoreClientException(msg)

    def register_registry(self):
        try:
            response = self._client.docker_registry_secrets.query()
            for registry in response.resources:
                if registry.name == self._config[Key.DR_REGISTRY_SECRETS_NAME]:
                    self._logger.info("Docker registry already registered")
                    return

            registry_secrets = {
                "auths": {
                    self._config[Key.DR_REGISTRY_HOST]: {
                        "username": self._config[Key.DR_REGISTRY_USER],
                        "password": self._config[Key.DR_REGISTRY_TOKEN],
                    }
                }
            }
            payload = {".dockerconfigjson": json.dumps(registry_secrets)}
            response = self._client.docker_registry_secrets.create(
                name=self._config[Key.DR_REGISTRY_SECRETS_NAME], data=payload
            )
            self._logger.debug(f"Registry secrets successfully registered - {response.message}")
        except AIAPIServerException as e:
            msg = f"Error registering registry secrets: {e}"
            self._logger.error(msg)
            raise SapAICoreClientException(msg)

    def create_scoring_code_application(self) -> None:
        try:
            application_name = self._config.sap_application_name

            # Check if application already exist for GitHub repo
            response = self._client.applications.query()
            for app in response.resources:
                if app.application_name == application_name:
                    self._logger.info("Application already exists")
                    return

            response = self._client.applications.create(
                application_name=self._config.sap_application_name,
                repository_url=self._config[Key.SAP_GITHUB_REPOSITORY],
                path=self._config[Key.SAP_GITHUB_REPOSITORY_PATH],
                revision="HEAD",
            )
            self._logger.debug(f"Application created - {response.message}")
        except AIAPIServerException as e:
            msg = f"Error registering application: {e}"
            self._logger.error(msg)
            raise SapAICoreClientException(msg)

    def deployment_update(self, deployment_info: DeploymentInfo, sap_deployment_id: str) -> Dict:
        try:
            if not deployment_info.model_package_details_path:
                raise SapAICoreClientException("Cannot find model package details path.")

            model_package_details = DeploymentUtils.load_deployment_settings(
                deployment_info.model_package_details_path
            )

            # 1.  Create  new configuration with input parameters, new_mode_id
            configuration_id = self._create_configuration(
                deployment_id=deployment_info.id,
                model_id=deployment_info.new_model_id,
                model_package_info=ModelPackageInfo(model_package_details),
            )

            # 2. Update the deployment with new configuration
            response = self._client.deployment.modify(
                deployment_id=sap_deployment_id,
                configuration_id=configuration_id,
                resource_group=self._config.resource_group_id,
            )
            self._logger.debug(f"Deployment updated - {response.message}")

            # 3. wait until deployment is running
            self._wait_for_deployment_running(sap_deployment_id)

            # 4. Get details of running deployment
            response = self._client.deployment.get(
                deployment_id=sap_deployment_id, resource_group=self._config.resource_group_id
            )
            return self._get_deployment_details(response)
        except AIAPIServerException as e:
            msg = f"Error creating deployment: {e}"
            self._logger.error(msg)
            raise SapAICoreClientException(msg)

    def create_deployment(self, deployment_info: DeploymentInfo) -> Dict:
        try:
            if not deployment_info.model_package_details_path:
                raise SapAICoreClientException("Cannot find model package details path.")

            model_package_details = DeploymentUtils.load_deployment_settings(
                deployment_info.model_package_details_path
            )

            # 1.  Create configuration with input parameters
            configuration_id = self._create_configuration(
                deployment_id=deployment_info.id,
                model_id=deployment_info.model_id,
                model_package_info=ModelPackageInfo(model_package_details),
            )

            # 2. Create deployment based on configuration
            response = self._client.deployment.create(
                configuration_id=configuration_id, resource_group=self._config.resource_group_id
            )
            sap_deployment_id = response.id

            # 3. wait until deployment is running
            self._wait_for_deployment_running(sap_deployment_id)

            # 4. Get details of running deployment
            response = self._client.deployment.get(
                deployment_id=sap_deployment_id, resource_group=self._config.resource_group_id
            )
            return self._get_deployment_details(response)
        except AIAPIServerException as e:
            msg = f"Error creating deployment: {e}"
            self._logger.error(msg)
            raise SapAICoreClientException(msg)

    def delete_deployment(self, sap_deployment_id: str) -> None:
        try:
            # 1. To delete a deployment SAP requires to be stopped first
            response = self._client.deployment.modify(
                deployment_id=sap_deployment_id,
                target_status=Status.STOPPED,
                resource_group=self._config.resource_group_id,
            )
            self._logger.debug(f"Deployment stopped - {response.message}")

            # 2. Wait until deployment is stopped
            self._wait_for_deployment_stopped(sap_deployment_id)

            # 3. Delete deployment
            response = self._client.deployment.delete(
                deployment_id=sap_deployment_id, resource_group=self._config.resource_group_id
            )
            self._wait_for_deployment_deleted(sap_deployment_id)

            self._logger.debug(f"Deployment deleted - {response.message}")
        except AIAPIServerException as e:
            msg = f"Error deleting deployment: {e}"
            self._logger.error(msg)
            raise SapAICoreClientException(msg)

    def get_deployment_details(self, dr_deployment_id: str, model_id: str) -> List[Dict]:
        config_name = self._build_configuration_name(dr_deployment_id, model_id)
        try:
            response = self._client.deployment.query(
                scenario_id=self._config[Key.SAP_SCENARIO_ID],
                configuration_id=None,
                executable_ids=[self._config[Key.SAP_EXECUTABLE_ID]],
            )

            deployments = [
                self._get_deployment_details(dep)
                for dep in response.resources
                if dep.configuration_name == config_name
            ]

            return deployments
        except AIAPIServerException as e:
            msg = f"Error getting details for deployment {dr_deployment_id} - {e}"
            self._logger.error(msg)
            raise SapAICoreClientException(msg)

    def get_datarobot_deployments(self) -> List[Dict]:
        try:
            response = self._client.deployment.query(
                scenario_id=self._config[Key.SAP_SCENARIO_ID],
                configuration_id=None,
                executable_ids=[self._config[Key.SAP_EXECUTABLE_ID]],
            )

            prefix = f"{DATAROBOT_PREFIX}-{self._config.prediction_environment.id}"
            deployments = [
                self._get_deployment_details(dep)
                for dep in response.resources
                if dep.configuration_name.startswith(prefix)
            ]

            self._logger.debug(f"{len(deployments)} datarobot deployment found.")
            return deployments
        except AIAPIServerException as e:
            msg = f"Error getting list of active deployments - {e}"
            self._logger.error(msg)
            raise SapAICoreClientException(msg)

    def _build_configuration_name(self, deployment_id: str, model_id: str) -> str:
        prediction_env_id = self._config.prediction_environment.id
        return f"{DATAROBOT_PREFIX}-{prediction_env_id}-{deployment_id}-{model_id}"

    def _wait_for_deployment_running(self, sap_deployment_id: str) -> None:
        timeout = time.time() + self._config[Key.SAP_MAX_ACTION_TIMEOUT_SEC]
        status_details = None

        while time.time() < timeout:
            response = self._client.deployment.get(
                deployment_id=sap_deployment_id, resource_group=self._config.resource_group_id
            )
            status_details = response.status_details
            if response.status == Status.RUNNING:
                return

            if response.status in [Status.DEAD, Status.STOPPED, Status.STOPPING]:
                self._logger.warning(f"Status details of deployment  - {status_details}")
                raise SapAICoreClientException(
                    f"Deployment transition to unwanted stated - {response.status}"
                )

            time.sleep(DEFAULT_ACTION_SLEEP_TIME_SEC)

        self._logger.warning(f"Status details of deployment  - {status_details}")
        msg = (
            "The deployment has been launched but is taking longer than expected to be ready."
            " We will continue to monitor its status and report any changes. We recommend you"
            " examine the cluster or you can attempt to relaunch the deployment to try again."
        )
        raise SapAICoreClientException(msg)

    def _wait_for_deployment_stopped(self, sap_deployment_id: str) -> None:
        timeout = time.time() + self._config[Key.SAP_MAX_ACTION_TIMEOUT_SEC]

        while time.time() < timeout:
            response = self._client.deployment.get(
                deployment_id=sap_deployment_id, resource_group=self._config.resource_group_id
            )
            if response.status == Status.STOPPED:
                return

            if response.status == Status.DEAD:
                self._logger.warning("Deployment terminated with error - ")
                return

            time.sleep(DEFAULT_ACTION_SLEEP_TIME_SEC)

        timeout_min = self._config.max_action_timeout_min
        error_msg = (
            f"Timeout of {timeout_min} minutes has been reached; the deployment was not"
            " successfully sttoped. We recommend reviewing the SAP AI Core dashboard for more"
            " details. Alternatively, you may attempt to stop the deployment and try again."
        )
        raise SapAICoreClientException(error_msg)

    def _wait_for_deployment_deleted(self, sap_deployment_id: str) -> None:
        timeout = time.time() + self._config[Key.SAP_MAX_ACTION_TIMEOUT_SEC]

        while time.time() < timeout:
            try:
                response = self._client.deployment.get(
                    deployment_id=sap_deployment_id, resource_group=self._config.resource_group_id
                )
                if response.target_status != TargetStatus.DELETED:
                    raise SapAICoreClientException("Deployment is not mark for deletion")

            except AIAPINotFoundException:
                self._logger.debug(f"Deployment {sap_deployment_id} not found")
                return

            time.sleep(DEFAULT_ACTION_SLEEP_TIME_SEC)

        timeout_min = self._config.max_action_timeout_min
        error_msg = (
            f"Timeout of {timeout_min} minutes has been reached; the deployment was not"
            " successfully deleted. We recommend reviewing the SAP AI Core dashboard for more"
            " details. Alternatively, you may attempt to stop the deployment and try again."
        )
        raise SapAICoreClientException(error_msg)

    def _get_deployment_details(self, deployment: Deployment) -> Dict:
        # get deployment configuration details
        configuration = self._client.configuration.get(deployment.configuration_id)
        parameters_map = {p.key: p.value for p in configuration.parameter_bindings}

        return {
            "url": f"{deployment.deployment_url}/v1/predict/",
            "sap_deployment_id": deployment.id,
            "model_id": parameters_map.get("MLOPS_MODEL_ID"),
            "deployment_id": parameters_map.get("MLOPS_DEPLOYMENT_ID"),
            "state": self._EXTERNAL_TO_INTERNAL_STATE_MAP[deployment.status],
        }

    def _create_configuration(
        self, deployment_id: str, model_id: str, model_package_info: ModelPackageInfo
    ) -> str:
        target_type = model_package_info.target_type
        if not target_type:
            raise SapAICoreClientException("Target type is not specified")

        input_parameters = [
            ParameterBinding(key="MLOPS_DEPLOYMENT_ID", value=deployment_id),
            ParameterBinding(key="MLOPS_MODEL_ID", value=model_id),
            ParameterBinding(key="MLOPS_MODEL_PACKAGE_ID", value=model_package_info.id),
            ParameterBinding(key="TARGET_TYPE", value=target_type),
            ParameterBinding(key="MONITOR", value=str(self._config.is_monitoring_enabled)),
            ParameterBinding(key="MONITOR_SETTINGS", value="MLOPS_SPOOLER_TYPE=API"),
            ParameterBinding(key="MLOPS_IMAGE_NAME", value=self._config[Key.DR_IMAGE_NAME]),
            ParameterBinding(
                key="MLOPS_REGISTRY_SECRETS_NAME", value=self._config[Key.DR_REGISTRY_SECRETS_NAME]
            ),
            ParameterBinding(key="MLOPS_SECRETS_NAME", value=self._config.datarobot_secrets_name),
            ParameterBinding(
                key="MLOPS_SAP_RESOURCE_PLAN", value=self._config[Key.SAP_RESOURCE_PLAN]
            ),
        ]

        if target_type == "binary":
            class_names = model_package_info.class_names
            if len(class_names) != 2:
                raise SapAICoreClientException("Binary type should only contains 2 class names")

            input_parameters.append(
                ParameterBinding(key="POSITIVE_CLASS_LABEL", value=class_names[0])
            )
            input_parameters.append(
                ParameterBinding(key="NEGATIVE_CLASS_LABEL", value=class_names[1])
            )

        try:
            response = self._client.configuration.create(
                name=self._build_configuration_name(deployment_id, model_id),
                scenario_id=self._config[Key.SAP_SCENARIO_ID],
                executable_id=self._config[Key.SAP_EXECUTABLE_ID],
                resource_group=self._config.resource_group_id,
                parameter_bindings=input_parameters,
                input_artifact_bindings=None,
            )
            self._logger.debug(f"Configuration created - {response.message}")
            return response.id
        except AIAPIServerException as e:
            msg = f"Error creating configuration: {e}"
            self._logger.error(msg)
            raise SapAICoreClientException(msg)
