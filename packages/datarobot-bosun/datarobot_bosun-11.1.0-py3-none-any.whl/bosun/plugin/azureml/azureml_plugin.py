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
from typing import Union

from azure.ai.ml.exceptions import LocalEndpointNotFoundError
from azure.core.exceptions import ResourceNotFoundError

from bosun.plugin.action_status import ActionDataFields
from bosun.plugin.action_status import ActionStatus
from bosun.plugin.action_status import ActionStatusInfo
from bosun.plugin.azureml.azureml_status_reporter import MLOpsStatusReporter
from bosun.plugin.azureml.client.base_endpoint_client import ListOnlyEndpointClient
from bosun.plugin.azureml.client.batch_endpoint_client import BatchEndpointClient
from bosun.plugin.azureml.client.online_endpoint_client import OnlineEndpointClient
from bosun.plugin.azureml.config.azureml_client_config import EndpointConfig
from bosun.plugin.azureml.config.azureml_client_config import kv_validator
from bosun.plugin.azureml.config.config_keys import Constants
from bosun.plugin.azureml.config.config_keys import EndpointType
from bosun.plugin.azureml.config.config_keys import Key
from bosun.plugin.bosun_plugin_base import BosunPluginBase
from bosun.plugin.constants import DeploymentState
from bosun.plugin.constants import EndpointConfigConstants
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.endpoint_info import EndpointInfo


class AzureMLPlugin(BosunPluginBase):
    AZURE_CLIENTS = {
        EndpointType.ONLINE: OnlineEndpointClient,
        EndpointType.BATCH: BatchEndpointClient,
        EndpointType.UNKNOWN: ListOnlyEndpointClient,
    }

    def __init__(self, plugin_config, private_config_file, pe_info, dry_run):
        super().__init__(plugin_config, private_config_file, pe_info, dry_run)
        logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(
            logging.WARNING
        )
        self.config = None

        # mute loggers from external modules
        all_loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in all_loggers:
            if logger.name.startswith(("datarobot", "bosun")):
                continue
            logging.getLogger(logger.name).setLevel(logging.ERROR)

    def get_azure_client(
        self,
    ) -> Union[OnlineEndpointClient, BatchEndpointClient, ListOnlyEndpointClient]:
        if not self.config:
            self.config = EndpointConfig.read_config(
                parent_config=self._plugin_config,
                config_file_path=self._private_config_file,
                prediction_environment=self._pe_info,
                deployment=DeploymentInfo(self._deployment_info) if self._deployment_info else None,
            )
        endpoint_type = self.config.endpoint_type
        self._logger.debug("Configuring AzureML client %s...", endpoint_type.name)
        azure_client_cls = self.AZURE_CLIENTS[endpoint_type]
        return azure_client_cls(self.config)

    def endpoint_update(self, endpoint_info: EndpointInfo) -> ActionStatusInfo:
        azure_client = self.get_azure_client()
        try:
            endpoint_status = azure_client.update_endpoint(endpoint_info)
            return ActionStatusInfo(ActionStatus.OK, state=endpoint_status)
        except Exception as e:
            self._logger.exception("Failed to create/update the endpoint %s", endpoint_info.id)
            return ActionStatusInfo(ActionStatus.ERROR, msg=str(e))

    def deployment_list(self):
        azure_client = self.get_azure_client()
        datarobot_model_deployments = azure_client.list_deployments(self._pe_info.id)

        status_msg = (
            (f"Found {len(datarobot_model_deployments)} deployment(s)")
            if len(datarobot_model_deployments) > 0
            else "No deployments found"
        )

        self._logger.info(status_msg)

        deployments_map = {
            deployment_id: ActionStatusInfo(ActionStatus.OK, state=deployment_state).to_dict()
            for deployment_id, (_, deployment_state, _) in datarobot_model_deployments.items()
        }

        return ActionStatusInfo(ActionStatus.OK, msg=status_msg, data=deployments_map)

    def deployment_start(
        self,
        deployment: DeploymentInfo,
        is_model_replacement: bool = False,
        traffic_settings: dict = None,
        reporter: MLOpsStatusReporter = None,
    ):
        try:
            azure_client = self.get_azure_client()

            # Model replacement sets its own unique name, due to AzureML naming restrictions
            if not is_model_replacement:
                # TODO backend should generate name.
                #  Currently UI allows users to set AzureML deployment name different
                #  from DataRobot Deployment name. The reason behind is that DR deployment name is
                #  mutable and AzureMLs names are not.
                deployment.name = azure_client.config[Key.DEPLOYMENT_NAME]

            self._logger.info(
                "Deployment start action invoked for the deployment %s (%s)...",
                deployment.name,
                deployment.id,
            )
            if deployment.model_artifact is None or not deployment.model_artifact.exists():
                return ActionStatusInfo(
                    ActionStatus.ERROR,
                    "Model must be pulled from DataRobot deployment, before pushing it to AzureML.",
                )

            reporter = reporter or MLOpsStatusReporter(
                self._plugin_config,
                deployment,
                azure_client.ENDPOINT_TYPE,
            )

            reporter.report_deployment("Registering the model...")
            model = azure_client.register_model(deployment)

            endpoint_info = self._get_endpoint_info()
            if azure_client.ENDPOINT_TYPE == EndpointType.ONLINE and not is_model_replacement:
                # Traffic settings should be calculated prior to any modifications done to the
                # endpoint. Otherwise, traffic settings passed from the UI will be considered as
                # stale and then ignored.
                traffic_settings = azure_client.get_traffic_settings_set_by_user(endpoint_info)

            if not is_model_replacement:
                reporter.report_deployment(f"Configuring the endpoint '{endpoint_info.name}'...")
                azure_client.create_endpoint(endpoint_info)
                # TODO: we should investigate a way to return/set the DASHBOARD_URL **before** the
                # end of this function because if things fail after this point, it can still be
                # useful for the user to have a pointer to the AzureML console.

            reporter.report_deployment(
                f"Searching for custom environment:"
                f" '{azure_client.config.environment_name}',"
                f" version {azure_client.config.environment_version}..."
            )
            environment = azure_client.get_latest_environment()

            reporter.report_deployment(
                "Creating a new deployment. This action may take up to 20 minutes. "
                "For more details check the https://ml.azure.com/endpoints page."
            )
            azure_client.create_deployment(endpoint_info, deployment, model, environment)

            # Need to fetch the endpoint after creating the deployment because it
            # seems otherwise it won't always have the scoring_uri filled in.
            endpoint = azure_client.get_endpoint(endpoint_info.name)
            if azure_client.ENDPOINT_TYPE == EndpointType.ONLINE:
                if traffic_settings:
                    reporter.report_deployment("Updating the deployment traffic...")
                    self._logger.info(
                        "New traffic configuration: %s for the endpoint: %s",
                        str(traffic_settings),
                        endpoint_info.name,
                    )
                    azure_client.update_endpoint(
                        endpoint_info.name, traffic_settings=traffic_settings
                    )
        except Exception as e:
            self._logger.exception("Failed to start the deployment %s", deployment.id)
            return ActionStatusInfo(ActionStatus.ERROR, msg=str(e))

        self._logger.info("Scoring code model is successfully deployed to AzureML.")
        status = self.deployment_status(deployment)
        status.data = {
            ActionDataFields.PREDICTION_URL: endpoint.scoring_uri,
            ActionDataFields.DASHBOARD_URL: azure_client.make_console_url(endpoint),
        }
        return status

    def deployment_stop(self, deployment_id: str):
        """
        AzureML does not allow to delete deployments with non-zero traffic. Sum of all deployment
        traffic values should be either 0 or 100.
        """
        try:
            azure_client = self.get_azure_client()
            endpoint_name = azure_client.find_endpoint_name_by_deployment_id(
                self._pe_info.id, deployment_id
            )

            if not endpoint_name:
                error_message = (
                    f"Can not find the endpoint by the deployment ID {deployment_id},"
                    f"assuming that the deployment is already stopped."
                )
                self._logger.error(error_message)
                return ActionStatusInfo(ActionStatus.OK, msg=error_message)

            azure_deployments = azure_client.list_deployments_by_endpoint(endpoint_name)

            if len(azure_deployments) == 1:
                # delete the endpoint if the last deployment in endpoint is deleted
                self._logger.info("Going to delete the endpoint %s", endpoint_name)
                azure_client.delete_endpoint(endpoint_name)

            elif len(azure_deployments) > 1:
                # if endpoint contains multiple deployments, delete a single deployment by ID
                deployment_to_delete = azure_deployments.get(deployment_id)
                if deployment_to_delete and self._endpoint_info:
                    default_deployment_id = self._endpoint_info.get(
                        EndpointConfigConstants.DEFAULT_DEPLOYMENT_ID
                    )
                    self._logger.info(
                        "Deployment to redistribute traffic to %s", default_deployment_id
                    )
                    default_deployment = azure_deployments.get(default_deployment_id)

                    # prior to deletion of the online deployment, its traffic must be moved to a
                    # champion model deployment (default_deployment)
                    redistribute_traffic_prior_to_deletion = (
                        azure_client.ENDPOINT_TYPE == EndpointType.ONLINE
                        and default_deployment is not None
                        # there is no point to update traffic for itself
                        and deployment_to_delete.name != default_deployment.name
                    )
                    self._logger.info(
                        "Going to delete the deployment: %s from the multi-deployment endpoint: %s",
                        deployment_to_delete,
                        endpoint_name,
                        extra={
                            "endpointType": azure_client.ENDPOINT_TYPE,
                            "defaultDeploymentId": default_deployment_id,
                            "defaultDeploymentName": (
                                default_deployment.name if default_deployment else None
                            ),
                        },
                    )
                    if redistribute_traffic_prior_to_deletion:
                        azure_client.move_deployment_traffic(
                            endpoint_name,
                            src_deployment_name=deployment_to_delete.name,
                            dest_deployment_name=default_deployment.name,
                        )
                    azure_client.delete_deployment_by_name(endpoint_name, deployment_to_delete.name)

        except (ResourceNotFoundError, LocalEndpointNotFoundError):
            # nothing to do
            self._logger.warning(
                "Deployment does not exist: %s. Skipping deployment stop.", deployment_id
            )
        except Exception as e:
            # Deployment can't be deleted if endpoint has multiple deployments and
            # the deployment traffic settings are not set to zero.
            self._logger.exception("Error stopping deployment")
            return ActionStatusInfo(ActionStatus.ERROR, msg=str(e))

        return ActionStatusInfo(ActionStatus.OK, state=DeploymentState.STOPPED)

    def deployment_replace_model(self, deployment_info: DeploymentInfo):
        """
        Do model replacement using a blue-green deployment strategy:
        - old model continues to serve realtime traffic
        - a new model is deployed with a new unique deployment name suffix
        - endpoint traffic is flipped from old deployment to the new one
        - old deployment is stopped
        """
        endpoint_info = self._get_endpoint_info()
        azure_client = self.get_azure_client()
        traffic_settings = None

        endpoint_deployments = azure_client.list_deployments_by_endpoint(endpoint_info.name)
        current_deployment = endpoint_deployments.get(deployment_info.id)

        old_deployment_name = current_deployment.name
        new_deployment_name = azure_client.config.new_deployment_name

        if azure_client.ENDPOINT_TYPE == EndpointType.ONLINE:
            (
                azure_endpoint_last_modified_at,
                current_traffic_settings,
            ) = azure_client.get_endpoint_traffic_settings(endpoint_info.name)

            # switch traffic from the old deployment to the new one
            traffic_settings = dict(**current_traffic_settings)
            old_deployment_traffic_value = traffic_settings.get(old_deployment_name)
            if not old_deployment_traffic_value:
                self._logger.warning(
                    "No traffic settings found for the deployment %s",
                    old_deployment_name,
                )

            traffic_settings[old_deployment_name] = 0
            traffic_settings[new_deployment_name] = old_deployment_traffic_value or 0

        reporter = MLOpsStatusReporter(
            self._plugin_config,
            deployment_info,
            azure_client.ENDPOINT_TYPE,
        )

        # during the model replacement, there are at least two deployments in the same endpoint
        # thus, a new uniq name should be used for the new deployment
        deployment_replacement = deployment_info.to_dict()
        deployment_replacement["name"] = new_deployment_name
        deployment_start_status = self.deployment_start(
            DeploymentInfo(deployment_replacement),
            is_model_replacement=True,
            traffic_settings=traffic_settings,
            reporter=reporter,
        )

        reporter.report_deployment(f"Removing the old deployment '{old_deployment_name}'...")
        azure_client.delete_deployment_by_name(endpoint_info.name, old_deployment_name)

        return deployment_start_status

    def pe_status(self):
        try:
            azure_client = self.get_azure_client()
            azure_client.list_deployments(self._pe_info.id)
            status = ActionStatus.OK
            status_msg = "Azure connection successful"
        except Exception:
            status = ActionStatus.ERROR
            status_msg = "Azure connection failed"
            self._logger.exception(status_msg)

        return ActionStatusInfo(status=status, msg=status_msg)

    def deployment_status(self, deployment_info: DeploymentInfo):
        endpoint_info = self._get_endpoint_info()
        azure_client = self.get_azure_client()
        try:
            deployment_status, deployment_env_version = azure_client.deployment_status(
                endpoint_info, deployment_info
            )
            if deployment_status is None:
                return ActionStatusInfo(ActionStatus.UNKNOWN, state=DeploymentState.STOPPED)

            required_version = azure_client.config.environment_version
            if deployment_env_version and deployment_env_version.major < required_version.major:
                environment_name = azure_client.config.environment_name
                msg = (
                    f"Deployment uses an outdated custom environment version "
                    f"'{environment_name}:{deployment_env_version}', the current version is "
                    f"'{environment_name}:{required_version}'. "
                    f"Re-launch deployment in order to run it with the new custom environment. "
                    f"More details about the changes can be found in the Conda description: "
                    f"https://ml.azure.com/environments/{environment_name}/version/{required_version}"
                )
                self._logger.warning(msg)
                return ActionStatusInfo(ActionStatus.WARN, state=deployment_status, msg=msg)

            return ActionStatusInfo(ActionStatus.OK, state=deployment_status)
        except Exception as e:
            self._logger.exception("Error checking deployment status")
            return ActionStatusInfo(ActionStatus.ERROR, msg=str(e))

    def plugin_start(self):
        """
        Builds a new Custom environment if one does not exist.
        AzureML internally blocks a deployment until a custom environment is successfully created,
        so we don't need to introduce deployment blocks on our side.

        The deployment timeout must include the time needed for image build (>= 10minutes).
        """
        azure_client = self.get_azure_client()
        azure_client.get_latest_environment()
        return ActionStatusInfo(ActionStatus.OK)

    def plugin_stop(self):
        # NOOP
        return ActionStatusInfo(ActionStatus.OK)

    def _get_endpoint_info(self) -> EndpointInfo:
        """Used to preserve backwards compatibility"""

        # expected to be always set
        assert self._pe_info
        assert self._deployment_info

        # if endpoint object is set, return its value
        required_fields = {"name", "endpointType", "predictionEnvironmentId"}
        if self._endpoint_info and all(field in self._endpoint_info for field in required_fields):
            return EndpointInfo(self._endpoint_info)

        # otherwise, try to read endpoint from deployment's key-value configuration
        deployment_info = DeploymentInfo(self._deployment_info)
        metadata = deployment_info.kv_config

        traffic_split_str = metadata.get(Key.ENDPOINT_TRAFFIC.name)
        traffic_split = kv_validator(traffic_split_str, Key.ENDPOINT_TRAFFIC)
        tags_str = metadata.get(Key.AZURE_ENVIRONMENT_TAGS.name)
        tags = kv_validator(tags_str, Key.AZURE_ENVIRONMENT_TAGS)

        return EndpointInfo(
            {
                "name": metadata.get(Key.ENDPOINT_NAME.name),
                "endpointType": metadata.get(Key.ENDPOINT_TYPE.name),
                "authType": Constants.AUTH_MODE_KEY.value,
                "predictionEnvironmentId": self._pe_info.id,
                "trafficSplit": traffic_split,
                "trafficUpdatedAt": metadata.get(Key.ENDPOINT_TRAFFIC_LAST_MODIFIED_AT.name),
                "tags": tags,
            }
        )
