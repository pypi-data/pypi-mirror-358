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
import typing
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Tuple
from typing import Union

from azure.ai.ml._restclient.v2022_02_01_preview.models import OnlineEndpointData
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import CodeConfiguration
from azure.ai.ml.entities import Environment
from azure.ai.ml.entities import IdentityConfiguration
from azure.ai.ml.entities import ManagedIdentityConfiguration
from azure.ai.ml.entities import ManagedOnlineDeployment
from azure.ai.ml.entities import ManagedOnlineEndpoint
from azure.ai.ml.entities import Model
from azure.ai.ml.entities import OnlineDeployment
from azure.ai.ml.entities import OnlineEndpoint
from azure.ai.ml.entities import OnlineRequestSettings
from azure.ai.ml.entities import SystemData
from azure.ai.ml.exceptions import LocalEndpointInFailedStateError
from azure.ai.ml.exceptions import LocalEndpointNotFoundError
from azure.ai.ml.operations import OnlineEndpointOperations
from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError

from bosun.plugin.azureml.client.base_endpoint_client import BaseEndpointClient
from bosun.plugin.azureml.client.scoring_snippets import AzureMLOnlineEndpointScoringSnippet
from bosun.plugin.azureml.config.azureml_client_config import AZURE_BASE_ENVIRONMENT
from bosun.plugin.azureml.config.azureml_client_config import CONDA_FILE_PATH
from bosun.plugin.azureml.config.azureml_client_config import EndpointConfig
from bosun.plugin.azureml.config.config_keys import Constants
from bosun.plugin.azureml.config.config_keys import EndpointType
from bosun.plugin.azureml.config.config_keys import Key
from bosun.plugin.azureml.config.config_keys import ProvisioningState
from bosun.plugin.constants import DeploymentState
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.endpoint_info import EndpointInfo
from datarobot_mlops.common.version_util import DataRobotAppVersion


class OnlineEndpointClient(BaseEndpointClient):
    ENDPOINT_TYPE = EndpointType.ONLINE
    SNIPPET_GENERATOR = AzureMLOnlineEndpointScoringSnippet

    def __init__(self, config: EndpointConfig):
        super().__init__(config)
        self.compute_virtual_machine = self.config[Key.COMPUTE_VIRTUAL_MACHINE]
        self.compute_instance_count = self.config[Key.COMPUTE_INSTANCE_COUNT]

    def create_endpoint(self, endpoint_info: EndpointInfo) -> str:
        try:
            endpoint = self.get_endpoint(endpoint_info.name)
            if endpoint:
                self.logger.info(
                    f"Found endpoint {endpoint_info.name}. "
                    f"It will be reused for subsequent deployments..."
                )
                # do not re-create existing endpoint, as it will shut down traffic
                return self.map_state(endpoint.provisioning_state)
        except (LocalEndpointNotFoundError, HttpResponseError):
            pass  # NOOP

        endpoint_tags = {
            Key.DATAROBOT_ENVIRONMENT_ID.value: endpoint_info.prediction_environment_id,
        }
        endpoint_tags.update(self.prediction_environment_tags)
        endpoint_tags.update(endpoint_info.tags)

        user_identity = (
            None
            if not self.config.is_monitoring_enabled
            else IdentityConfiguration(
                type=Constants.USER_ASSIGNED_IDENTITY.value,
                user_assigned_identities=[
                    ManagedIdentityConfiguration(
                        resource_id=self.config[Key.AZURE_MANAGED_IDENTITY_ID]
                    )
                ],
            )
        )

        endpoint = ManagedOnlineEndpoint(
            name=endpoint_info.name,
            auth_mode=endpoint_info.auth_type,
            tags=endpoint_tags,
            identity=user_identity,
        )

        result = self._client.online_endpoints.begin_create_or_update(endpoint, local=self._local)
        if not self._local:
            result: OnlineEndpoint = result.result(self.config[Key.ENDPOINT_CREATION_TIMEOUT])

        if result.provisioning_state in self.FAIL_STATES:
            message = f"Failed to create endpoint {endpoint.name}, with status: {result.provisioning_state}"
            self.logger.error(message)
            raise RuntimeError(message)

        return self.map_state(result.provisioning_state)

    def update_endpoint(
        self,
        endpoint_name: str,
        tags: dict = None,
        auth_mode: str = None,
        traffic_settings: dict = None,
        default_deployment: str = None,
    ) -> str:
        """
        :param endpoint_name: str, name of the endpoint to update traffic for
        :param tags: dict, any key-value pairs set by user to tag endpoint resource
        :param auth_mode: str, mechanism used to authenticate HTTP inference requests [key, token]
        :param traffic_settings: dict, applicable only to Online endpoints
            containing the deployment name and its traffic value (int)
        :param default_deployment: str, applicable only to Batch endpoints
            default deployment used for batch predictions

        :returns DeploymentState
        """
        endpoint = self.get_endpoint(endpoint_name)

        if not any([tags, auth_mode, traffic_settings]):
            self.logger.warning(
                "Endpoint %s update will be skipped. No values to update", endpoint_name
            )
            return self.map_state(endpoint.provisioning_state)

        # Do not send managed identity in update requests, since it's not allowed to update,
        # and will fail the request.
        endpoint.identity = None

        if tags:
            endpoint.tags.update(tags)

        if auth_mode:
            endpoint.auth_mode = auth_mode

        if traffic_settings:
            endpoint.traffic.update(traffic_settings)

        extra = {
            "auth_mode": auth_mode,
            "tags": str(tags),
            "traffic_settings": str(traffic_settings),
        }
        self.logger.info("Updating endpoint %s", endpoint_name, extra=extra)
        result = self._client.online_endpoints.begin_create_or_update(endpoint, local=self._local)

        if not self._local:  # local does not support traffic updates
            result = result.result(self.config[Key.ENDPOINT_UPDATE_TIMEOUT])

        if result.provisioning_state == ProvisioningState.SUCCEEDED.value:
            self.logger.info("Endpoint %s is successfully updated", endpoint_name, extra=extra)
        else:
            msg = f"Failed to update the endpoint {endpoint_name}. "
            f"Status: {result.provisioning_state}."
            self.logger.error(msg, extra=extra)
            raise RuntimeError(msg)

        return self.map_state(result.provisioning_state)

    def get_endpoint(self, endpoint_name: str) -> OnlineEndpoint:
        return self._client.online_endpoints.get(endpoint_name, local=self._local)

    def get_endpoint_traffic_settings(self, endpoint_name: str) -> typing.Tuple[datetime, dict]:
        """
        :param endpoint_name: str, name of the endpoint to get settings for
        :return: tuple, traffic modification datetime and
            dictionary of deployment name to traffic value (int)
        """
        endpoints_api: OnlineEndpointOperations = self._client.online_endpoints

        if self._local:
            modified_at = None
            endpoint: OnlineEndpoint = endpoints_api.get(name=endpoint_name, **self.local_parameter)
            return modified_at, endpoint.traffic

        # Read JSON response from an endpoint public API in order to get lastModifiedAt field
        # which is not exposed by the OnlineEndpoint entity. API returns UTC datetime string
        # in ISO 8601 format: e.g. 2020-01-01T12:34:56.999Z
        endpoint: OnlineEndpointData = endpoints_api._online_operation.get(
            resource_group_name=self.config[Key.AZURE_RESOURCE_GROUP],
            workspace_name=self.config[Key.AZURE_WORKSPACE],
            endpoint_name=endpoint_name,
            **endpoints_api._init_kwargs,
        )
        self.logger.info("Found existing endpoint %s.", endpoint_name)
        system_data: SystemData = endpoint.system_data
        azure_endpoint_created_at = system_data.created_at if system_data else None
        azure_endpoint_last_modified_at = system_data.last_modified_at if system_data else None
        self.logger.info(
            f"Azure endpoint created_at: {azure_endpoint_created_at}, "
            f"modified_at: {azure_endpoint_last_modified_at}"
        )
        return (
            azure_endpoint_last_modified_at,
            endpoint.properties.traffic,
        )

    def move_deployment_traffic(
        self, endpoint_name: str, src_deployment_name: str, dest_deployment_name: str
    ):
        """
        Move traffic from an old deployment to a new deployment.
        This method is suitable to move traffic during model replacement, relaunch or
        deletion (from multi-deployment endpoints).
        """
        endpoints_api, _ = self._get_api_clients(self.ENDPOINT_TYPE)

        # get current traffic settings
        endpoint = endpoints_api.get(name=endpoint_name, **self.local_parameter)
        traffic_settings = endpoint.traffic
        self.logger.info("Endpoint %s traffic settings: %s", endpoint_name, str(traffic_settings))
        if not traffic_settings:
            return  # NOOP, nothing to do, since no traffic is configured on the endpoint

        src_traffic_value = traffic_settings.get(src_deployment_name)
        dest_traffic_value = traffic_settings.get(dest_deployment_name, 0)

        if not src_traffic_value:
            return  # NOOP, there is no traffic to source deployment

        # move traffic from source to destination deployment
        traffic_settings[src_deployment_name] = 0
        traffic_settings[dest_deployment_name] = dest_traffic_value + src_traffic_value
        self.update_endpoint(endpoint_name, traffic_settings=traffic_settings)

    def create_deployment(
        self,
        endpoint: EndpointInfo,
        deployment: DeploymentInfo,
        model,
        environment: Environment,
    ):
        model_filename = Path(model.path).name
        scoring_script_name = "score.py"
        deployment_tags = {
            Key.DATAROBOT_DEPLOYMENT_ID.value: deployment.id,
            Key.DATAROBOT_MODEL_ID.value: deployment.current_model_id,
        }
        deployment_tags.update(self.prediction_environment_tags)

        with ScratchDir(cleanup=not self._local) as scoring_code_dir:
            scoring_code_file = scoring_code_dir / scoring_script_name
            scoring_code_file.write_text(self.get_scoring_snippet(model_filename))
            # Fix permissions when running in self._local (e.g. docker bind mount) mode
            scoring_code_dir.chmod(0o755)
            scoring_code_file.chmod(0o644)

            # SDK requires scoring timeout to be in millis
            scoring_timeout_ms = self.config[Key.SCORING_TIMEOUT_SECONDS] * 1000

            deployment = ManagedOnlineDeployment(
                name=deployment.name,
                endpoint_name=endpoint.name,
                model=model,
                environment=environment,
                code_configuration=CodeConfiguration(
                    code=str(scoring_code_dir), scoring_script=scoring_script_name
                ),
                request_settings=OnlineRequestSettings(request_timeout_ms=scoring_timeout_ms),
                instance_type=self.compute_virtual_machine,
                instance_count=self.compute_instance_count,
                environment_variables=self._get_env_vars(deployment, model_filename),
                tags=deployment_tags,
            )

            try:
                result = self._client.online_deployments.begin_create_or_update(
                    # TODO: make `skip_script_validation` configurable
                    deployment=deployment,
                    local=self._local,
                    skip_script_validation=True,
                )
            except LocalEndpointInFailedStateError as e:
                self.logger.error("Failed to create local deployment: %s", e)
                result = ManagedOnlineDeployment(
                    **deployment._to_dict(), provisioning_state=ProvisioningState.FAILED.value
                )

        if not self._local:
            # TODO: this can raise an exception; if it does we should attempt to collect logs from
            # the deployment and return them in the exception message.
            result = result.result(self.config[Key.ENDPOINT_DEPLOYMENT_TIMEOUT])

        if result.provisioning_state == ProvisioningState.SUCCEEDED.value:
            self.logger.info("Deployment %s is successfully created.", deployment.name)
        else:
            msg = (
                f"Failed to create deployment {deployment.name}"
                f" (endpoint={endpoint.name};model={model.name})."
                f" Status: {result.provisioning_state}"
            )
            self.logger.error(msg)
            try:
                logs = self._client.online_deployments.get_logs(
                    name=result.name,
                    endpoint_name=result.endpoint_name,
                    lines=60,  # hopefully this is enough context w/o dumping a ton of text
                    local=self._local,
                )
                self.logger.debug("deployment container logs: %s", logs)
                msg += f"\n\nDeployment Logs:\n{logs}"
            except Exception as e:
                self.logger.warning(
                    "Failed to fetch logs for deployment %s (endpoint=%s): %s",
                    result.name,
                    result.endpoint_name,
                    e,
                )
            raise RuntimeError(msg)

        return result

    def delete_endpoint(self, endpoint_name: str):
        self.logger.info("Deleting online endpoint %s...", endpoint_name)
        timeout_seconds = self.config[Key.ENDPOINT_DELETION_TIMEOUT]
        try:
            result = self._client.online_endpoints.begin_delete(endpoint_name, local=self._local)
        except LocalEndpointNotFoundError:
            # To be idempotent, if the endpoint is already gone then just ignore.
            pass
        else:
            if not self._local:
                result.result(timeout_seconds)

    def delete_deployment_by_id(
        self, endpoint: EndpointInfo, deployment: Union[DeploymentInfo, namedtuple]
    ):
        deployment_name = self.get_deployment_name(endpoint, deployment)
        self.delete_deployment_by_name(endpoint.name, deployment_name)

    def delete_deployment_by_name(self, endpoint_name: str, deployment_name: str):
        self.logger.info(
            "Deleting deployment %s from online endpoint %s...",
            deployment_name,
            endpoint_name,
        )
        result = self._client.online_deployments.begin_delete(
            name=deployment_name, endpoint_name=endpoint_name, local=self._local
        )
        if not self._local:
            result.result(self.config[Key.DEPLOYMENT_DELETION_TIMEOUT])

    def deployment_status(
        self, endpoint_info: EndpointInfo, deployment_info: DeploymentInfo
    ) -> Union[None, Tuple[str, DataRobotAppVersion]]:
        try:
            azure_endpoint: OnlineEndpoint = self._client.online_endpoints.get(
                name=endpoint_info.name, local=self._local
            )
            endpoint_deployments = self.list_deployments_by_endpoint(endpoint_info.name)
            azure_deployment: OnlineDeployment = endpoint_deployments.get(deployment_info.id)
        except (LocalEndpointNotFoundError, ResourceNotFoundError):
            azure_endpoint = None
            azure_deployment = None

        if azure_endpoint is None or azure_deployment is None:
            return None, None  # status unknown

        deployment_state = self.map_online_deployment_state(
            endpoint_state=azure_endpoint.provisioning_state,
            deployment_state=azure_deployment.provisioning_state,
        )
        deployment_env_version = self.get_environment_version(azure_deployment.environment)

        return (deployment_state, deployment_env_version)

    @staticmethod
    def map_online_deployment_state(endpoint_state, deployment_state):
        # (endpoint_state, deployment_state) -> DR deployment_state
        state_map = {
            (  # deployment creation
                ProvisioningState.UPDATING.value,
                ProvisioningState.UPDATING.value,
            ): DeploymentState.LAUNCHING,
            (  # endpoint traffic update
                ProvisioningState.UPDATING.value,
                ProvisioningState.SUCCEEDED.value,
            ): DeploymentState.LAUNCHING,
            (  # deployment deletion. this should be an API bug?
                ProvisioningState.SUCCEEDED.value,
                ProvisioningState.UPDATING.value,
            ): DeploymentState.SHUTTING_DOWN,
            (  # endpoint deletion
                ProvisioningState.DELETING.value,
                ProvisioningState.DELETING.value,
            ): DeploymentState.SHUTTING_DOWN,
            (
                ProvisioningState.SUCCEEDED.value,
                ProvisioningState.SUCCEEDED.value,
            ): DeploymentState.READY,
        }

        return state_map.get((endpoint_state, deployment_state), DeploymentState.UNKNOWN)

    def get_traffic_settings_set_by_user(
        self, endpoint_info: EndpointInfo
    ) -> typing.Dict[str, str]:
        traffic_settings = {}

        try:
            datarobot_traffic_last_modified_at = endpoint_info.traffic_updated_at
            azure_endpoint_last_modified_at, _ = self.get_endpoint_traffic_settings(
                endpoint_info.name
            )
            if self._local or datarobot_traffic_last_modified_at > azure_endpoint_last_modified_at:
                traffic_settings = endpoint_info.traffic_split
            else:
                self.logger.info(
                    "Traffic settings are stale. Skipping traffic update for the endpoint '%s'."
                    "DataRobot traffic modified_at: %s, AzureML endpoint modified_at %s.",
                    endpoint_info.name,
                    datarobot_traffic_last_modified_at,
                    azure_endpoint_last_modified_at,
                )

        except (ResourceNotFoundError, LocalEndpointNotFoundError):
            # for a new endpoint, always apply the traffic settings set by user on DataRobot UI
            traffic_settings = endpoint_info.traffic_split
            self.logger.warning(
                "Endpoint %s not found. A new one will be created.", endpoint_info.name
            )

        except HttpResponseError:
            # do not apply traffic changes if we unsure on it's current state
            # do not fail the flow of deployment creation/update or deletion
            self.logger.error("Can't get endpoint %s", endpoint_info.name, exc_info=True)
        except AttributeError:
            self.logger.error(
                "Can't get 'lastModifiedAt' timestamp for endpoint %s",
                endpoint_info.name,
                exc_info=True,
            )

        return traffic_settings

    def get_latest_environment(self):
        # Override base method because local mode is only supported for online
        # endpoints currently.
        if self._local:
            return Environment(conda_file=CONDA_FILE_PATH, image=AZURE_BASE_ENVIRONMENT)
        return super().get_latest_environment()

    def register_model(self, deployment: DeploymentInfo):
        if self._local:
            self.logger.info("Skipping local model registration")
            return Model(
                name=deployment.model_name,
                path=deployment.model_artifact,
                type=AssetTypes.CUSTOM_MODEL,
            )
        return super().register_model(deployment)

    def archive_model(self, model_name: str):
        if self._local:
            self.logger.info("Skipping local model deletion")
            return
        super().archive_model(model_name)


class ScratchDir(TemporaryDirectory):
    """
    When running in local mode, AzureML bind mounts the scoring script into the container
    so we can't use an actual temporary file/dir. We will still create the dir/file in
    the temp location so hopefully the OS will cleanup the files for us.
    """

    def __init__(self, cleanup=True, **kwargs):
        super().__init__(**kwargs)
        self._do_cleanup = cleanup
        if not cleanup:
            # If we aren't doing cleanup, detach the finalizer that the parent class sets
            self._finalizer.detach()

    def __enter__(self):
        return Path(self.name)

    def cleanup(self):
        if self._do_cleanup:
            super().cleanup()
