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
import tempfile
from pathlib import Path
from typing import Tuple
from typing import Union

import azure.ai.ml as azureml
from azure.ai.ml.entities import BatchDeployment
from azure.ai.ml.entities import BatchEndpoint
from azure.ai.ml.entities import BatchRetrySettings
from azure.ai.ml.entities import CodeConfiguration
from azure.ai.ml.entities import Environment
from azure.core.exceptions import ResourceNotFoundError
from azure.core.polling import LROPoller

from bosun.plugin.azureml.client.base_endpoint_client import BaseEndpointClient
from bosun.plugin.azureml.client.scoring_snippets import AzureMLBatchEndpointScoringSnippet
from bosun.plugin.azureml.config.azureml_client_config import EndpointConfig
from bosun.plugin.azureml.config.azureml_client_config import Key
from bosun.plugin.azureml.config.config_keys import EndpointType
from bosun.plugin.azureml.config.config_keys import ProvisioningState
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.endpoint_info import EndpointInfo
from datarobot_mlops.common.version_util import DataRobotAppVersion


class BatchEndpointClient(BaseEndpointClient):
    ENDPOINT_TYPE = EndpointType.BATCH
    SNIPPET_GENERATOR = AzureMLBatchEndpointScoringSnippet

    def __init__(self, config: EndpointConfig):
        super().__init__(config)

    def create_endpoint(self, endpoint: EndpointInfo) -> str:
        endpoint_tags = {
            Key.DATAROBOT_ENVIRONMENT_ID.value: endpoint.prediction_environment_id,
        }
        endpoint_tags.update(self.prediction_environment_tags)
        endpoint_tags.update(endpoint.tags)
        endpoint = azureml.entities.BatchEndpoint(name=endpoint.name, tags=endpoint_tags)

        # TODO: the poller is returning the wrong object type
        # (azure.ai.ml._restclient.v2022_05_01.models._models_py3.BatchEndpointData)
        result_poller: LROPoller[BatchEndpoint] = (
            self._client.batch_endpoints.begin_create_or_update(endpoint)
        )
        result: BatchEndpoint = result_poller.result(self.config[Key.ENDPOINT_CREATION_TIMEOUT])
        provisioning_state = result.provisioning_state

        if provisioning_state in self.FAIL_STATES:
            message = (
                f"Failed to create endpoint {endpoint.name}, with status: {provisioning_state}"
            )
            self.logger.error(message)
            raise RuntimeError(message)

        return self.map_state(provisioning_state)

    def update_endpoint(
        self,
        endpoint_name: str,
        tags: dict = None,
        auth_mode: str = None,
        traffic_settings: dict = None,
        default_deployment: str = None,
    ) -> str:
        endpoint = self.get_endpoint(endpoint_name)

        if not any([tags, default_deployment]):
            self.logger.warning(
                "Endpoint %s update will be skipped. No values to update", endpoint_name
            )
            return self.map_state(endpoint.provisioning_state)

        if tags:
            endpoint.tags.update(tags)

        if default_deployment:
            endpoint.default_deployment_name = default_deployment

        extra = {
            "tags": str(tags),
            "default_deployment": default_deployment,
        }
        self.logger.info("Updating the endpoint %s", endpoint_name, extra=extra)

        lro_poller: LROPoller[BatchEndpoint] = self._client.batch_endpoints.begin_create_or_update(
            endpoint
        )
        result: BatchEndpoint = lro_poller.result(self.config[Key.ENDPOINT_CREATION_TIMEOUT])
        provisioning_state = result.provisioning_state

        if provisioning_state in self.FAIL_STATES:
            message = f"Failed to update endpoint {endpoint.name}. Status: {provisioning_state}"
            self.logger.error(message, extra=extra)
            raise RuntimeError(message)

        return self.map_state(provisioning_state)

    def get_endpoint(self, endpoint_name: str) -> BatchEndpoint:
        return self._client.batch_endpoints.get(endpoint_name)

    def create_deployment(
        self,
        endpoint: EndpointInfo,
        deployment: DeploymentInfo,
        model,
        environment: Environment,
    ):
        model_filename = Path(model.path).name
        scoring_script_name = "batch_driver.py"
        deployment_tags = {
            Key.DATAROBOT_DEPLOYMENT_ID.value: deployment.id,
            Key.DATAROBOT_MODEL_ID.value: deployment.current_model_id,
        }
        deployment_tags.update(self.prediction_environment_tags)
        with tempfile.TemporaryDirectory() as scoring_code_dir, open(
            Path(scoring_code_dir) / scoring_script_name, "w"
        ) as scoring_code_file:
            scoring_code_file.write(self.get_scoring_snippet(model_filename))
            scoring_code_file.flush()
            self.copy_feature_types(deployment.feature_types_path, scoring_code_dir)

            deployment = BatchDeployment(
                name=deployment.name,
                endpoint_name=endpoint.name,
                model=model,
                code_configuration=CodeConfiguration(
                    code=str(scoring_code_dir), scoring_script=scoring_script_name
                ),
                environment=environment,
                compute=self.config[Key.COMPUTE_CLUSTER],
                instance_count=self.config[Key.COMPUTE_CLUSTER_INSTANCE_COUNT],
                max_concurrency_per_instance=self.config[Key.MAX_CONCURRENCY_PER_INSTANCE],
                mini_batch_size=self.config[Key.MINI_BATCH_SIZE],
                output_file_name=self.config[Key.OUTPUT_FILE_NAME],
                output_action=self.config[Key.OUTPUT_ACTION],
                error_threshold=self.config[Key.ERROR_THRESHOLD],
                retry_settings=BatchRetrySettings(
                    max_retries=self.config[Key.MAX_RETRIES],
                    timeout=self.config[Key.SCORING_TIMEOUT_SECONDS],
                ),
                logging_level=self.config[Key.LOGGING_LEVEL],
                environment_variables=self._get_env_vars(deployment, model_filename),
                tags=deployment_tags,
            )
            # TODO check status of deployment
            # TODO make `skip_script_validation` configurable
            self._client.batch_deployments.begin_create_or_update(
                deployment, skip_script_validation=True
            ).result(self.config[Key.ENDPOINT_DEPLOYMENT_TIMEOUT])

        # ensure deployment is default in batch endpoint
        self.make_default(deployment.name, endpoint.name)

    def make_default(self, deployment_name, endpoint_name, await_results=True):
        endpoint: BatchEndpoint = self._client.batch_endpoints.get(endpoint_name)
        endpoint.defaults.deployment_name = deployment_name
        poller: LROPoller[BatchEndpoint] = self._client.batch_endpoints.begin_create_or_update(
            endpoint
        )
        if await_results:
            result: BatchEndpoint = poller.result(self.config[Key.ENDPOINT_UPDATE_TIMEOUT])
            provisioning_state = result.provisioning_state
            if provisioning_state in {
                ProvisioningState.FAILED,
                ProvisioningState.DELETING,
                ProvisioningState.CANCELED,
            }:
                message = (
                    f"Failed to set default deployment to endpoint: {endpoint.name}, "
                    f"with status: {provisioning_state}"
                )
                self.logger.error(message)
                raise RuntimeError(message)

            self.logger.info(
                "Default deployment for endpoint '%s' updated to: '%s'",
                endpoint_name,
                deployment_name,
            )

    def delete_endpoint(self, endpoint_name: str):
        self._client.batch_endpoints.begin_delete(name=endpoint_name).result(
            self.config[Key.ENDPOINT_DELETION_TIMEOUT]
        )

    def delete_deployment_by_id(self, endpoint: EndpointInfo, deployment: DeploymentInfo):
        deployment_name = self.get_deployment_name(endpoint, deployment)
        self.delete_deployment_by_name(endpoint.name, deployment_name)

    def delete_deployment_by_name(self, endpoint_name: str, deployment_name: str):
        self.logger.info(
            "Deleting deployment %s from batch endpoint %s...",
            deployment_name,
            endpoint_name,
        )
        self._client.batch_deployments.begin_delete(
            name=deployment_name, endpoint_name=endpoint_name
        ).result(self.config[Key.DEPLOYMENT_DELETION_TIMEOUT])

    def deployment_status(
        self, endpoint_info: EndpointInfo, deployment_info: DeploymentInfo
    ) -> Union[None, Tuple[str, DataRobotAppVersion]]:
        try:
            azure_endpoint: BatchEndpoint = self._client.batch_endpoints.get(
                name=endpoint_info.name
            )
            endpoint_deployments = self.list_deployments_by_endpoint(endpoint_info.name)
            azure_deployment: BatchDeployment = endpoint_deployments.get(deployment_info.id)
        except ResourceNotFoundError:
            azure_endpoint, azure_deployment = None, None

        if azure_endpoint is None or azure_deployment is None:
            return None, None  # status unknown

        deployment_env_version = self.get_environment_version(azure_deployment.environment)
        return (self.map_state(azure_deployment.provisioning_state), deployment_env_version)
