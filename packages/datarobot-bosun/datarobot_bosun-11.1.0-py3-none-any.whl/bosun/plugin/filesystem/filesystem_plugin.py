#  ---------------------------------------------------------------------------------
#  Copyright (c) 2021 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2024.
#
#  DataRobot, Inc. Confidential.
#  This is proprietary source code of DataRobot, Inc. and its affiliates.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.
#  ---------------------------------------------------------------------------------

import glob
import logging
import os
import shutil

import yaml
from schema import And
from schema import Optional
from schema import Schema
from schema import Use

from bosun.model_connector.constants import ModelPackageConstants
from bosun.plugin.action_status import ActionDataFields
from bosun.plugin.action_status import ActionStatus
from bosun.plugin.action_status import ActionStatusInfo
from bosun.plugin.bosun_plugin_base import BosunPluginBase
from bosun.plugin.constants import BosunPluginConfigConstants
from bosun.plugin.constants import DeploymentInfoConfigConstants
from bosun.plugin.constants import DeploymentState
from bosun.plugin.deployment_info import DeploymentInfo


class FSPluginConfig:
    BASE_DIR_KEY = "baseDir"
    DEPLOYMENT_DIR_PREFIX_KEY = "deploymentDirPrefix"
    DEPLOYMENT_INFO_FILE = "deploymentInfoFile"
    DEPLOYMENT_PREDICTION_BASE_URL = "deploymentPredictionBaseUrl"
    DEPLOYMENT_KV_FILE = "deploymentKVFile"

    def __init__(self, plugin_config):
        log = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self._config = plugin_config

        schema = Schema(
            {
                FSPluginConfig.BASE_DIR_KEY: And(str, len),
                FSPluginConfig.DEPLOYMENT_DIR_PREFIX_KEY: str,
                FSPluginConfig.DEPLOYMENT_INFO_FILE: And(str, len),
                FSPluginConfig.DEPLOYMENT_PREDICTION_BASE_URL: And(str, len),
                BosunPluginConfigConstants.MLOPS_BOSUN_PRED_ENV_ENABLE_MONITORING_KEY: bool,
                Optional(FSPluginConfig.DEPLOYMENT_KV_FILE): And(Use(str)),
            },
            ignore_extra_keys=True,
        )

        schema.validate(plugin_config)
        if self._config[BosunPluginConfigConstants.MLOPS_BOSUN_PRED_ENV_ENABLE_MONITORING_KEY]:
            log.warn("Model monitoring is enabled for this PE but ignored by this plugin")

    @property
    def deployment_info_fields(self):
        return ["deployment_id", "model_id"]

    @property
    def base_dir(self):
        return self._config[FSPluginConfig.BASE_DIR_KEY]

    @property
    def prediction_base_url(self):
        return self._config[FSPluginConfig.DEPLOYMENT_PREDICTION_BASE_URL]

    @property
    def deployment_dir_prefix(self):
        return self._config[FSPluginConfig.DEPLOYMENT_DIR_PREFIX_KEY]

    @property
    def deployment_info_file(self):
        return self._config[FSPluginConfig.DEPLOYMENT_INFO_FILE]

    @property
    def deployment_kv_file(self):
        return self._config.get(FSPluginConfig.DEPLOYMENT_KV_FILE, None)


class FilesystemPlugin(BosunPluginBase):
    def __init__(self, plugin_config, private_config_file, pe_info, dry_run):
        super().__init__(plugin_config, private_config_file, pe_info, dry_run)
        self._read_config_file()
        self._config = FSPluginConfig(self._plugin_config)

    #  =====  Plugin Internal functions ==========
    def _create_deployment_structure(self, di: DeploymentInfo):
        self._logger.info(f"Creating deployment structure for: {di.id}")
        assert di.model_artifact is not None

        deployment_dir = self._deployment_dir(di)
        model_base_path = os.path.basename(di.model_artifact)
        model_path = os.path.join(deployment_dir, model_base_path)

        self._logger.info(
            "Copying model artifact: {}, size: {}".format(
                di.model_artifact, os.path.getsize(di.model_artifact)
            )
        )
        os.makedirs(deployment_dir, exist_ok=True)
        shutil.copyfile(di.model_artifact, model_path)

        self._logger.info("Updating deployment info file")
        self._write_deployment_info_file(di)
        self._write_deployment_kv_file(di)

    def _deployment_dir(self, di: DeploymentInfo):
        return self._deployment_dir_from_id(di.id)

    def _deployment_dir_from_id(self, deployment_id):
        return (
            os.path.join(self._config.base_dir, self._config.deployment_dir_prefix + deployment_id)
            + os.path.sep
        )

    def _deployment_info_file(self, di: DeploymentInfo):
        return os.path.join(self._deployment_dir(di), self._config.deployment_info_file)

    def _deployment_kv_file(self, di: DeploymentInfo):
        return os.path.join(self._deployment_dir(di), self._config.deployment_kv_file)

    def _write_deployment_info_file(self, di: DeploymentInfo):
        model_id = di.new_model_id if di.new_model_id is not None else di.model_id
        data = {
            "deployment_id": di.id,
            "model_id": model_id,
        }
        with open(self._deployment_info_file(di), "w+") as fd:
            yaml.dump(data, fd, default_flow_style=False)

    def _write_deployment_kv_file(self, di: DeploymentInfo):

        # If file is not created if deployment
        if not self._config.deployment_kv_file:
            self._logger.debug("Skipping writing kv file")
            return
        self._logger.debug(f"writing deployment kv file {self._deployment_kv_file(di)}")
        with open(self._deployment_kv_file(di), "w") as fd:
            yaml.dump(di.kv_config, fd, default_flow_style=False)

    def _check_base_dir(self):
        if not os.path.exists(self._config.base_dir):
            return ActionStatusInfo(
                ActionStatus.ERROR, msg=f"Unable to detect folder: {self._config.base_dir}"
            )
        if not os.path.isdir(self._config.base_dir):
            return ActionStatusInfo(
                ActionStatus.ERROR,
                msg=f"Provided folder '{self._config.base_dir}' - is not a directory",
            )
        if not os.access(self._config.base_dir, os.W_OK):
            return ActionStatusInfo(
                ActionStatus.ERROR,
                msg=f"Provided folder '{self._config.base_dir}' - is not write accessible",
            )

        return ActionStatusInfo(ActionStatus.OK, msg="all ok")

    def _read_config_file(self):
        if self._private_config_file is None:
            return

        self._logger.debug(f"Filesystem plugin private config file: {self._private_config_file}")

        with open(self._private_config_file) as conf_file:
            config = yaml.safe_load(conf_file)
        self._logger.debug(config)
        self._plugin_config.update(config)
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(self.get_sanitized_config(self._plugin_config))

    def _deployment_status(self, deployment_dir, model_format=None, model_execution_type=None):
        if not os.path.exists(deployment_dir):
            return ActionStatusInfo(
                ActionStatus.ERROR,
                msg=f"No deployment dir: {deployment_dir}",
                state=DeploymentState.ERROR,
            )

        if model_format and model_execution_type == ModelPackageConstants.MODEL_EXECUTION_DEDICATED:
            suffix = DeploymentInfoConfigConstants.model_artifact_suffix(model_format)
            model_files = glob.glob(os.path.join(deployment_dir, f"*.{suffix}"))
            if len(model_files) != 1:
                return ActionStatusInfo(
                    ActionStatus.ERROR, msg="Missing model artifact", state=DeploymentState.ERROR
                )

        deployment_info = os.path.join(deployment_dir, self._config.deployment_info_file)
        if not os.path.exists(deployment_info):
            return ActionStatusInfo(
                ActionStatus.ERROR,
                msg=f"No deployment info file: {deployment_info}",
                state=DeploymentState.ERROR,
            )

        with open(deployment_info) as info:
            config = yaml.safe_load(info)
            missing_fields = [f for f in self._config.deployment_info_fields if f not in config]
            if len(missing_fields) > 0:
                return ActionStatusInfo(
                    ActionStatus.ERROR,
                    msg=f"Invalid config file, missing fields: {missing_fields}",
                    state=DeploymentState.ERROR,
                )

        return ActionStatusInfo(
            ActionStatus.OK,
            state=DeploymentState.READY,
            data={ActionDataFields.CURRENT_MODEL_ID: config["model_id"]},
        )

    # =======Plugin required functions ===
    def plugin_start(self):
        """
        Check base directory exists
        :return:
        """
        self._logger.info("-------> plugin_start called")
        return self._check_base_dir()

    def plugin_stop(self):
        """
        Currently no operation is needed here
        :return:
        """
        self._logger.info("-------> plugin_stop called")
        return ActionStatusInfo(ActionStatus.OK)

    def deployment_list(self):
        self._logger.debug("-------> deployment_list called")

        deployments_map = {}
        list_deployment = glob.glob(
            os.path.join(self._config.base_dir, f"{self._config.deployment_dir_prefix}*")
        )

        for deployment_dir in list_deployment:
            deployments_status = self._deployment_status(deployment_dir)
            deployment_id = os.path.basename(deployment_dir).replace(
                self._config.deployment_dir_prefix, ""
            )
            deployments_map[deployment_id] = deployments_status.to_dict()

        if len(list_deployment) == 0:
            status_msg = "No containers running"
        else:
            status_msg = f"Number of deployments: {len(list_deployment)}"

        self._logger.info(status_msg)
        if deployments_map:
            self._logger.info("Deployments: " + str(deployments_map))
        return ActionStatusInfo(ActionStatus.OK, msg=status_msg, data=deployments_map)

    def deployment_start(self, di: DeploymentInfo):
        """
        Create a directory structure for deployment
        :param deployment_info: deployment information
        :return:
        """
        self._logger.debug("-------> deployment_start called")

        self._create_deployment_structure(di)
        self._logger.info("Filesystem deployment_start completed successfully")
        prediction_url = "{}/deployments/{}{}/predictions".format(
            self._config.prediction_base_url, self._config.deployment_dir_prefix, di.id
        )
        data = {ActionDataFields.PREDICTION_URL: prediction_url}
        return ActionStatusInfo(ActionStatus.OK, state=DeploymentState.READY, data=data)

    def deployment_stop(self, deployment_id: str):
        """
        Removes deployment directory under base dir
        :param deployment_info: deployment information
        :return:
        """
        self._logger.info("-------> deployment_stop called")
        deployment_dir = self._deployment_dir_from_id(deployment_id)

        self._logger.info(f"Stopping deployment - removing deployment dir {deployment_dir}")
        try:
            if os.path.exists(deployment_dir):
                shutil.rmtree(deployment_dir)
            self._logger.info("Filesystem deployment_stop completed successfully")
            return ActionStatusInfo(status=ActionStatus.OK, state=DeploymentState.STOPPED)
        except OSError:
            return ActionStatusInfo(status=ActionStatus.ERROR, state=DeploymentState.ERROR)

    def deployment_replace_model(self, di: DeploymentInfo):
        """
        Update directory content for current deployment
        :param deployment_info: deployment information
        :return:
        """
        self._logger.debug("-------> deployment_replace_model called")
        try:
            shutil.rmtree(self._deployment_dir(di))
        except OSError:
            return ActionStatusInfo(status=ActionStatus.ERROR, state=DeploymentState.ERROR)

        self._logger.info(f"Replacing deployment {di.id}")
        self._create_deployment_structure(di)
        self._logger.info("Filesystem deployment_replace_model completed successfully")
        return ActionStatusInfo(ActionStatus.OK, state=DeploymentState.READY)

    def deployment_status(self, di: DeploymentInfo):
        """
        Check that deployment directory exists and has correct content
        :param deployment_info: deployment information
        :return:
        """
        self._logger.debug("-------> deployment_status called")
        deployment_dir = self._deployment_dir(di)

        return self._deployment_status(deployment_dir, di.model_format, di.model_execution_type)

    def pe_status(self):
        """
        Verify that base directory exists and is a directory
        :return:
        """
        self._logger.debug("<---------> pe_status called")
        pe_status = self._check_base_dir()
        if pe_status.status != ActionStatus.OK:
            return pe_status

        assert self._pe_info is not None
        self._logger.debug(f"PE is ok .. checking deployments [{len(self._pe_info.deployments)}]")
        # TODO: Add logic for orphaned deployments, as k8s plugin
        all_deployments_status = {}
        for di in self._pe_info.deployments:
            self._logger.debug(f"Checking status for deployment: {di.id}")
            deployment_dir = self._deployment_dir(di)
            d_status = self._deployment_status(
                deployment_dir, di.model_format, di.model_execution_type
            )

            all_deployments_status[di.id] = d_status.to_dict()
            if d_status.status != ActionStatus.OK:
                self._logger.warning(d_status.to_yaml())
        if bool(all_deployments_status):
            pe_status.data = {ActionDataFields.DEPLOYMENTS_STATUS: all_deployments_status}

        return pe_status
