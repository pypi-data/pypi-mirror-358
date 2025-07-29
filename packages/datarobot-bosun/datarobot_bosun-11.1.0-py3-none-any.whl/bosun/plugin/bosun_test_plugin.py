#  --------------------------------------------------------------------------------
#  Copyright (c) 2020 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2023.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#
#  --------------------------------------------------------------------------------

import datetime
import glob
import json
import logging
import os
import time

import yaml

from bosun.plugin.action_status import ActionDataFields
from bosun.plugin.action_status import ActionStatus
from bosun.plugin.action_status import ActionStatusInfo
from bosun.plugin.bosun_plugin_base import BosunPluginBase
from bosun.plugin.constants import BosunPluginConfigConstants
from bosun.plugin.constants import DeploymentState
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.endpoint_info import EndpointInfo


class BosunTestPlugin(BosunPluginBase):
    """
    A test plugin. This plugin is used to test Bosun agent behavior. This plugin is not running
    any "real" action, but will call time.sleep instead and will print some information about the
    action being called into the logs.
    """

    CONFIG_FILE_ENTRY = "config_file"

    def __init__(
        self, plugin_config: object, private_config_file: str, pe_info: dict, dry_run: bool
    ):
        super().__init__(plugin_config, private_config_file, pe_info, False)
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(f"plugin config: {self.get_sanitized_config(plugin_config)}")

        # The plugin config dictionary can contain a pointer to a private config file for this
        # specific plugin script. So we can get specific config in any format known only to this
        # implementation of the plugin.
        if private_config_file:
            with open(private_config_file) as config_fh:
                private_config = json.load(config_fh)
        else:
            private_config = {}

        self._launch_time_sec = private_config.get("launch_time_sec", 10)
        self._stop_time_sec = private_config.get("stop_time_sec", 8)
        self._replace_model_time = private_config.get("replace_model_time_sec", 10)
        self._pe_status_time = private_config.get("pe_status_time_sec", 3)
        self._deployment_status_time = private_config.get("deployment_status_time_sec", 2)
        self._deployment_list_time = private_config.get("deployment_list_time_sec", 2)
        self._raise_exception = private_config.get("raise_exception", False)
        self._plugin_start_time = private_config.get("plugin_start_time", 5)
        self._plugin_stop_time = private_config.get("plugin_stop_time", 5)
        self._plugin_tmp_dir = private_config.get("tmp_dir", "/tmp")
        self._assert_has_api_token = private_config.get("assert_has_api_token", False)

    def _raise_exception_if_set(self):
        if self._raise_exception:
            raise Exception("Bosun Test plugin is raising an exception")

    def _get_pe_filename(self):
        return os.path.join(
            self._plugin_tmp_dir, "pe_" + self._plugin_config["MLOPS_BOSUN_PRED_ENV_ID"] + ".yaml"
        )

    def _get_deployment_filename(self, deployment_info: DeploymentInfo):
        return self._get_deployment_filename_from_id(deployment_info.id)

    def _get_deployment_filename_from_id(self, deployment_id):
        return os.path.join(self._plugin_tmp_dir, "deployment_" + deployment_id + ".yaml")

    @staticmethod
    def _get_deployment_content(deployment_info: DeploymentInfo):
        content = {
            "name": deployment_info.name,
            "model_id": deployment_info.model_id,
            "key_value_config": deployment_info.kv_config,
            "model_execution_type": deployment_info.model_execution_type,
            "model_artifact": str(deployment_info.model_artifact),
            "state": "running",
        }
        if deployment_info.new_model_id:
            content["new_model_id"] = deployment_info.new_model_id
        return content

    def plugin_start(self):
        self._logger.info("Plugin start for Test plugin- nothing to do")
        self._raise_exception_if_set()

        if self._assert_has_api_token:
            if not self._plugin_config.get(BosunPluginConfigConstants.MLOPS_API_TOKEN_KEY):
                raise RuntimeError("MLOps API token was not passed to plugin by Bosun Agent")
            if not self._plugin_config.get(BosunPluginConfigConstants.MLOPS_URL_KEY):
                raise RuntimeError("MLOps URL token was not passed to plugin by Bosun Agent")

        time.sleep(self._plugin_start_time)
        self._logger.info("Done plugin start for Test plugin")
        with open(self._get_pe_filename(), "w") as pe:
            pe.write(yaml.safe_dump({"state": "running"}))
        return ActionStatusInfo(ActionStatus.OK)

    def plugin_stop(self):
        self._logger.info("Plugin stop for Test plugin")
        self._raise_exception_if_set()
        time.sleep(self._plugin_stop_time)
        self._logger.info("Done plugin stop for Test plugin")
        pe_file = self._get_pe_filename()
        if os.path.exists(pe_file):
            os.remove(pe_file)
        return ActionStatusInfo(ActionStatus.OK)

    def deployment_start(self, di: DeploymentInfo):
        """
        Add a cron job per deployment
        :return:
        """
        self._logger.info("start deployment_launch")
        self._raise_exception_if_set()
        time.sleep(self._launch_time_sec)
        with open(self._get_deployment_filename(di), "w") as deployment_file:
            content = self._get_deployment_content(di)
            deployment_file.write(yaml.safe_dump(content))

        self._logger.info("done  deployment_launch")
        return ActionStatusInfo(ActionStatus.OK, msg="Launch successful", state="ready")

    def deployment_stop(self, deployment_id: str):
        """
        Stop the cron job and delete it
        :return:
        """
        self._logger.info("start deployment_stop")
        self._raise_exception_if_set()
        deployment_path = self._get_deployment_filename_from_id(deployment_id)
        if os.path.exists(deployment_path):
            os.remove(deployment_path)

        time.sleep(self._stop_time_sec)
        self._logger.info("done  deployment_stop")
        return ActionStatusInfo(ActionStatus.OK, msg="Stop Successful", state="stopped")

    def deployment_replace_model(self, di: DeploymentInfo):
        """
        Will put a model artifact in a place the cronjob can consume it
        :param deployment_info: Info about the deployment
        :param model_artifact_path:
        :return:
        """
        model_artifact_path = di.model_artifact
        self._logger.info(f"start replacing model: {model_artifact_path}")
        time.sleep(self._replace_model_time)
        deployment_path = self._get_deployment_filename(di)
        try:
            self._raise_exception_if_set()
            with open(deployment_path, "w") as deployment_file:
                content = self._get_deployment_content(di)
                if "new_model_id" in content:
                    content["model_id"] = content["new_model_id"]
                deployment_file.write(yaml.safe_dump(content))
        except Exception as ex:
            if os.path.exists(deployment_path):
                with open(deployment_path) as deployment_file:
                    content = yaml.safe_load(deployment_file.read())
                    if content["model_id"] != di.model_id:
                        return ActionStatusInfo(
                            ActionStatus.ERROR,
                            msg="Failed to replace model, continuing with old one",
                            state=DeploymentState.ERROR,
                            data={ActionDataFields.OLD_MODEL_IN_USE: True},
                        )
                    else:
                        raise ex

        self._logger.info(f"done  replacing model: {model_artifact_path}")
        return ActionStatusInfo(
            ActionStatus.OK,
            msg=f"Model replaced successfully Path: {model_artifact_path}",
            state="ready",
        )

    def pe_status(self):
        """
        Do status check
        :return:
        """
        self._logger.info("start pe_status")
        self._raise_exception_if_set()
        time.sleep(self._pe_status_time)
        pe_file = self._get_pe_filename()
        if os.path.exists(pe_file):
            with open(pe_file, "r+") as pe_file:
                content = yaml.safe_load(pe_file.read())
                content["status_timestamp"] = datetime.datetime.utcnow().isoformat()
                pe_file.seek(0)
                pe_file.write(yaml.safe_dump(content))
                pe_file.truncate()

            all_deployments_status = {}

            assert self._pe_info is not None
            print(self._pe_info)
            for di in self._pe_info.deployments:
                self._logger.info(f"Checking status of deployment: {di.id}")
                deployment_status = self._deployment_status(di.id)
                self._logger.info(deployment_status)
                all_deployments_status[di.id] = deployment_status.to_dict()
            data = {ActionDataFields.DEPLOYMENTS_STATUS: all_deployments_status}
            action_status = ActionStatusInfo(
                ActionStatus.OK, msg="PE Health looks awesome", data=data
            )

        else:
            action_status = ActionStatusInfo(ActionStatus.ERROR, msg="PE not found")
        self._logger.info(f"done  pe_status: {action_status}")
        return action_status

    def deployment_status(self, di: DeploymentInfo):
        """
        :param deployment_info: Info about the deployment to check
        Do status check
        :return:
        """
        self._logger.info("start deployment_status")
        self._raise_exception_if_set()
        time.sleep(self._deployment_status_time)
        return self._deployment_status(di.id)

    def _deployment_status(self, deployment_id):
        deployment_path = self._get_deployment_filename_from_id(deployment_id)
        if os.path.exists(deployment_path):
            with open(deployment_path, "r+") as deployment_file:
                content = yaml.safe_load(deployment_file.read())
                content["status_timestamp"] = datetime.datetime.utcnow().isoformat()
                deployment_file.seek(0)
                deployment_file.write(yaml.safe_dump(content))
                deployment_file.truncate()
                action_status = ActionStatusInfo(
                    ActionStatus.OK,
                    msg="Deployment health looks good",
                    state=DeploymentState.READY,
                    data={ActionDataFields.CURRENT_MODEL_ID: content["model_id"]},
                )
        else:
            action_status = ActionStatusInfo(
                ActionStatus.ERROR, msg="Deployment not found", state=DeploymentState.ERROR
            )
        self._logger.info("done deployment_status")
        return action_status

    def deployment_list(self):
        """
        Get the list of running deployments
        :return:
        """
        self._logger.info("start deployment list")
        self._raise_exception_if_set()
        time.sleep(self._deployment_list_time)
        current_deployment_files = glob.glob(
            os.path.join(self._plugin_tmp_dir, "deployment_*.yaml")
        )

        deployments_map = {}
        for file in current_deployment_files:
            deployment_id = os.path.basename(file).split("_")[1].split(".")[0]
            with open(file) as f:
                deployment_info = yaml.safe_load(f.read())
                deployments_map[deployment_id] = deployment_info

        return ActionStatusInfo(ActionStatus.OK, msg="Deployment list", data=deployments_map)

    def endpoint_update(self, endpoint_info: EndpointInfo) -> ActionStatusInfo:
        """
        Mock update, used to check:
         - if Endpoint DTO is passed to plugin
         - if Endpoint schema validates YAML payload correctly
        """
        self._logger.info("start endpoint_update")
        assert endpoint_info is not None
        assert self._endpoint_info is not None
        return ActionStatusInfo(ActionStatus.OK, msg="Endpoint update successful", state="ready")

    def endpoint_status(self, endpoint_info: EndpointInfo) -> ActionStatusInfo:
        self._logger.info("start endpoint_status")
        assert endpoint_info is not None
        assert self._endpoint_info is not None
        return ActionStatusInfo(ActionStatus.OK, msg="Endpoint status looks good", state="ready")
