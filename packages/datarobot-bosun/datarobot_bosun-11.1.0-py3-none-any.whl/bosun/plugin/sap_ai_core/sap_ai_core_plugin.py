#  ---------------------------------------------------------------------------------
#     Copyright (c) 2024 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2024.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#  ---------------------------------------------------------------------------------

from bosun.plugin.action_status import ActionDataFields
from bosun.plugin.action_status import ActionStatus
from bosun.plugin.action_status import ActionStatusInfo
from bosun.plugin.bosun_plugin_base import BosunPluginBase
from bosun.plugin.constants import DeploymentState
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.sap_ai_core.client.sap_ai_core_client import SapAICoreClient
from bosun.plugin.sap_ai_core.client.sap_ai_core_client import SapAICoreClientException
from bosun.plugin.sap_ai_core.sap_ai_core_config import SapAICoreConfig


class SapAICorePlugin(BosunPluginBase):

    def __init__(self, plugin_config, private_config_file, pe_info, dry_run):
        super().__init__(plugin_config, private_config_file, pe_info, dry_run)
        self._logger.debug("SAP AI Core plugin init")
        self._config = None

    def _get_ai_core_client(self) -> SapAICoreClient:
        if not self._config:
            self._logger.debug("Loading config...")
            self._config = SapAICoreConfig.read_config(
                parent_config=self._plugin_config,
                config_file_path=self._private_config_file,
                prediction_environment=self._pe_info,
                deployment=DeploymentInfo(self._deployment_info) if self._deployment_info else None,
            )
        self._logger.debug("Configuring Sap AI Core client...")
        return SapAICoreClient(self._config)

    def plugin_start(self) -> ActionStatusInfo:
        """
        This functions runs when management agent starts, is idempotent since agent can be
         restarted at any time. It ensures that:
        1. DR secrets are register otherwise it created.
        2. Register GitHub repo that contains argo workflows if needed.
        3. Create SAP application using GitHub repo if needed.
        """
        try:
            client = self._get_ai_core_client()
            self._logger.info(
                f"SAP plugin starts, using AICoreV2Client version: {client.get_version()}"
            )

            # 1. register dr secretes
            client.register_dr_secrets()

            # 2. register image registry
            client.register_registry()

            # 3. register GitHub
            client.register_repository()

            # 4. create application ( scenarios & executables)
            client.create_scoring_code_application()

            return ActionStatusInfo(ActionStatus.OK)
        except SapAICoreClientException as e:
            return ActionStatusInfo(ActionStatus.ERROR, str(e))

    def plugin_stop(self) -> ActionStatusInfo:
        """
        Currently no operation is needed here
        """
        self._logger.info("SAP AI Core Plugin plugin_stop called")
        return ActionStatusInfo(ActionStatus.OK)

    def deployment_list(self) -> ActionStatusInfo:
        """
        List all deployments managed by this plugin and return their status.
        """
        try:
            client = self._get_ai_core_client()

            # Get all deployments with datarobot-<pred_env_id> prefix
            deployments = client.get_datarobot_deployments()
            status_msg = (
                f"Found {len(deployments)} deployment(s)"
                if len(deployments) > 0
                else "No deployments found"
            )
            self._logger.debug(status_msg)

            deployments_map = {
                dep["deployment_id"]: ActionStatusInfo(
                    ActionStatus.OK, state=dep["state"], data=dep
                ).to_dict()
                for dep in deployments
            }
            return ActionStatusInfo(ActionStatus.OK, msg=status_msg, data=deployments_map)
        except SapAICoreClientException as e:
            return ActionStatusInfo(ActionStatus.ERROR, str(e))

    def deployment_start(self, deployment_info: DeploymentInfo) -> ActionStatusInfo:
        """
        Create a new deployment. Idempotent; can be called on existing deployment.
        Waits until deployment is 'Running' and ready to serve predictions to return state=READY.
        Otherwise, return state=ERROR if wait exceed timeout (30 min default) and still not ready.
        """
        try:
            client = self._get_ai_core_client()
            # 1. Verify that there is not SAP deployment associated with deployment_id/model_id
            deployment_details = client.get_deployment_details(
                deployment_info.id, deployment_info.model_id
            )

            # If multiple deployments found return status UNKNOWN
            if len(deployment_details) > 1:
                return ActionStatusInfo(
                    ActionStatus.UNKNOWN,
                    msg=f"Error: Found multiple deployments with the same id={deployment_info.id}",
                    state=DeploymentState.ERROR,
                )
            elif len(deployment_details) == 1:
                # if only one deployment found, does not create a new one returns status of
                # existing one
                deployment = deployment_details[0]
                return ActionStatusInfo(
                    ActionStatus.OK,
                    state=deployment.get("state"),
                    data={
                        ActionDataFields.CURRENT_MODEL_ID: deployment.get("model_id"),
                        ActionDataFields.PREDICTION_URL: deployment.get("url"),
                    },
                )

            # 2. Creates SAP deployment and waits until ready.
            deployment = client.create_deployment(deployment_info)
            return ActionStatusInfo(
                ActionStatus.OK,
                state=deployment.get("state"),
                data={
                    ActionDataFields.CURRENT_MODEL_ID: deployment.get("model_id"),
                    ActionDataFields.PREDICTION_URL: deployment.get("url"),
                },
            )
        except SapAICoreClientException as e:
            self._logger.error(f"Error creating deployment - {e}")
            return ActionStatusInfo(ActionStatus.ERROR, str(e))

    def deployment_stop(self, dr_deployment_id: str) -> ActionStatusInfo:
        """
        Deletes deployment associated with datarobot deployment_id
        """
        try:
            client = self._get_ai_core_client()
            # The input to this function is only deployment_id so to fetch running deployments
            # we need to filter based on only one variable. This search will ideally return only
            # one SAP deployment.
            sap_deployment_ids = [
                dep["sap_deployment_id"]
                for dep in client.get_datarobot_deployments()
                if dep.get("deployment_id") == dr_deployment_id
            ]

            if len(sap_deployment_ids) == 0:
                status_msg = f"Deployment with id: {dr_deployment_id} not found."
                self._logger.warning(status_msg)
                return ActionStatusInfo(
                    ActionStatus.OK, msg=status_msg, state=DeploymentState.STOPPED
                )
            elif len(sap_deployment_ids) > 1:
                status_msg = (
                    f"Multiple deployments found for deployment id {dr_deployment_id} - "
                    f" SAP deployment ids: {sap_deployment_ids}"
                )
                self._logger.error(status_msg)
                return ActionStatusInfo(
                    ActionStatus.OK, msg=status_msg, state=DeploymentState.UNKNOWN
                )

            # To delete a SAP deployment is required to stopped first, this function
            # waits until deployment is successfully deleted or timeout
            client.delete_deployment(sap_deployment_ids[0])
            return ActionStatusInfo(ActionStatus.OK, state=DeploymentState.STOPPED)
        except SapAICoreClientException as e:
            self._logger.exception("Error stopping deployment")
            return ActionStatusInfo(ActionStatus.ERROR, str(e))

    def deployment_replace_model(self, deployment_info: DeploymentInfo) -> ActionStatusInfo:
        """
        Replace the model of an existing deployment with a new one. Waits until deployment
        is ready to server prediction or timeout (30 min default) exceeds.
        """
        try:
            client = self._get_ai_core_client()

            # 1. Verify that there is only one SAP deployment associated with deployment_id/model_id
            deployment_details = client.get_deployment_details(
                deployment_info.id, deployment_info.model_id
            )
            if len(deployment_details) == 0:
                return ActionStatusInfo(
                    ActionStatus.OK,
                    msg=f"Error: No deployment found with id={deployment_info.id}.",
                    state=DeploymentState.STOPPED,
                )
            elif len(deployment_details) > 1:
                return ActionStatusInfo(
                    ActionStatus.UNKNOWN,
                    msg=f"Error: Found multiple deployments with the same id={deployment_info.id}",
                    state=DeploymentState.ERROR,
                )

            # 2. Update the SAP deployment with new model, waits until ready
            sap_deployment_id = deployment_details[0]["sap_deployment_id"]
            deployment = client.deployment_update(deployment_info, sap_deployment_id)
            return ActionStatusInfo(
                ActionStatus.OK,
                state=deployment.get("state"),
                data={
                    ActionDataFields.CURRENT_MODEL_ID: deployment.get("model_id"),
                    ActionDataFields.PREDICTION_URL: deployment.get("url"),
                },
            )
        except SapAICoreClientException as e:
            self._logger.error(f"Error while replacing model - {e}")
            return ActionStatusInfo(ActionStatus.ERROR, str(e))

    def deployment_status(self, deployment_info: DeploymentInfo) -> ActionStatusInfo:
        """
        Return health status of Deployment, check that only one SAP deployment exists. Based
        on SAP status determine if RUNNING, STOPPED, UNKNOWN
        """
        try:
            client = self._get_ai_core_client()
            deployment_details = client.get_deployment_details(
                deployment_info.id, deployment_info.model_id
            )
            if len(deployment_details) == 0:
                return ActionStatusInfo(
                    ActionStatus.UNKNOWN,
                    msg=f"Error: No deployment found with id={deployment_info.id}.",
                    state=DeploymentState.STOPPED,
                )
            elif len(deployment_details) > 1:
                return ActionStatusInfo(
                    ActionStatus.UNKNOWN,
                    msg=f"Error: Found multiple deployments with the same id={deployment_info.id}",
                    state=DeploymentState.UNKNOWN,
                )

            deployment = deployment_details[0]
            return ActionStatusInfo(
                ActionStatus.OK,
                state=deployment.get("state"),
                data={
                    ActionDataFields.CURRENT_MODEL_ID: deployment.get("model_id"),
                    ActionDataFields.PREDICTION_URL: deployment.get("url"),
                },
            )
        except SapAICoreClientException as e:
            self._logger.error(f"Error creating deployment - {e}")
            return ActionStatusInfo(ActionStatus.ERROR, str(e))

    def pe_status(self) -> ActionStatusInfo:
        """
        Checks connectivity to SAP AI Core, and return health status of all deployments.
        """
        try:
            client = self._get_ai_core_client()
            client.get_version()  # sanity check to confirm we can talk to SAP API
        except SapAICoreClientException as e:
            return ActionStatusInfo(ActionStatus.ERROR, msg=f"SAP AI Core API Issue: {e}")

        try:
            sap_deployments_map = {
                dep["deployment_id"]: ActionStatusInfo(
                    ActionStatus.OK, state=dep["state"], data=dep
                ).to_dict()
                for dep in client.get_datarobot_deployments()
            }

            pe_deployments = dict()
            for di in self._pe_info.deployments:
                if di.id in sap_deployments_map:
                    pe_deployments[di.id] = sap_deployments_map[di.id]
                else:
                    status_msg = "No record of deployment running in SAP."
                    pe_deployments[di.id] = ActionStatusInfo(
                        ActionStatus.UNKNOWN, msg=status_msg, state=DeploymentState.STOPPED
                    ).to_dict()

            expected_vs_reality = set(sap_deployments_map) - set(pe_deployments)
            if expected_vs_reality:
                status = ActionStatus.WARN
                status_msg = f"Orphaned deployments exist: {expected_vs_reality}"
            else:
                status = ActionStatus.OK
                status_msg = "Cluster is Healthy"

            data = {ActionDataFields.DEPLOYMENTS_STATUS: pe_deployments} if pe_deployments else None
            return ActionStatusInfo(status, msg=status_msg, data=data)
        except SapAICoreClientException as e:
            self._logger.error(f"Error  deployment - {e}")
            return ActionStatusInfo(ActionStatus.ERROR, str(e))
