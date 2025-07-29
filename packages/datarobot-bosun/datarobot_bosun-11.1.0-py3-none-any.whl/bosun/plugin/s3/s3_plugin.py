#  ---------------------------------------------------------------------------------
#  Copyright (c) 2021 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2023.
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
import pprint
from pathlib import Path

import boto3
import yaml

from bosun.model_connector.constants import ModelPackageConstants
from bosun.plugin.action_status import ActionStatus
from bosun.plugin.action_status import ActionStatusInfo
from bosun.plugin.bosun_plugin_base import BosunPluginBase
from bosun.plugin.constants import DeploymentInfoConfigConstants
from bosun.plugin.constants import DeploymentState
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.s3.s3_plugin_config import S3PluginConfig


class S3Plugin(BosunPluginBase):
    CONTENTS_KEY = "Contents"

    def __init__(self, plugin_config, private_config_file, pe_info, dry_run):
        super().__init__(plugin_config, private_config_file, pe_info, dry_run)

        self._read_config_file()
        self._config = S3PluginConfig(self._plugin_config)
        self._s3 = boto3.client("s3")

    def _read_config_file(self):
        """
        Reading the plugin specific config file if such is provided. And overriding this plugin
        configuration
        :return:
        """
        if self._private_config_file is None:
            return

        self._logger.info(f"S3 plugin private config file: {self._private_config_file}")

        with open(self._private_config_file) as conf_file:
            config = yaml.safe_load(conf_file)
        self._logger.info(config)
        self._plugin_config.update(config)
        if self._logger.isEnabledFor(logging.DEBUG):
            self._logger.debug(self.get_sanitized_config(self._plugin_config))

    @staticmethod
    def _is_path_exists(obj_list, path):
        if S3Plugin.CONTENTS_KEY not in obj_list:
            return False
        for key in obj_list[S3Plugin.CONTENTS_KEY]:
            if key["Key"].startswith(path):
                return True
        return False

    def _list_objects_matching(self, prefix="", suffix=""):
        response = self._s3.list_objects(Bucket=self._config.bucket_name, Prefix=prefix)
        objects = []
        for obj in response.get(S3Plugin.CONTENTS_KEY, []):
            key = obj["Key"]
            if key.endswith(suffix):
                objects.append(key)
        return objects

    def _deployment_dir(self, di: DeploymentInfo):
        return self._deployment_dir_from_id(di.id)

    def _deployment_dir_from_id(self, deployment_id):
        return (
            os.path.join(self._config.base_dir, self._config.deployment_dir_prefix + deployment_id)
            + os.path.sep
        )

    def _deployment_info_file(self, di: DeploymentInfo):
        return os.path.join(self._deployment_dir(di), self._config.deployment_info_file)

    def _write_deployment_info_file(self, di: DeploymentInfo):
        model_id = di.new_model_id if di.new_model_id is not None else di.model_id
        data = {
            "deployment_id": di.id,
            "model_id": model_id,
        }

        self._s3.put_object(
            Bucket=self._config.bucket_name,
            Key=self._deployment_info_file(di),
            Body=yaml.dump(data),
        )

    def _get_deployment_dirs(self):
        deployment_prefix = os.path.join(self._config.base_dir, self._config.deployment_dir_prefix)
        response = self._s3.list_objects(Bucket=self._config.bucket_name, Prefix=deployment_prefix)

        deployment_set = set()
        if S3Plugin.CONTENTS_KEY in response:
            for obj in response[S3Plugin.CONTENTS_KEY]:
                parent_path = Path(obj["Key"]).parent
                deployment_set.add(str(parent_path))

        return deployment_set

    def _deployment_status(self, deployment_dir, model_format=None, model_execution_type=None):
        obj_list = self._s3.list_objects(Bucket=self._config.bucket_name, Prefix=deployment_dir)
        self._logger.debug(pprint.pformat(obj_list))
        if not self._is_path_exists(obj_list, deployment_dir):
            return ActionStatusInfo(
                ActionStatus.ERROR,
                msg=f"No deployment dir: {deployment_dir}",
                state=DeploymentState.ERROR,
            )
        if model_format and model_execution_type == ModelPackageConstants.MODEL_EXECUTION_DEDICATED:
            model_files = self._list_objects_matching(
                prefix=deployment_dir,
                suffix=DeploymentInfoConfigConstants.model_artifact_suffix(model_format),
            )

            if len(model_files) != 1:
                return ActionStatusInfo(
                    ActionStatus.ERROR, msg="Missing model artifact", state=DeploymentState.ERROR
                )

        deployment_info = os.path.join(deployment_dir, self._config.deployment_info_file)
        if not self._is_path_exists(obj_list, deployment_info):
            return ActionStatusInfo(
                ActionStatus.ERROR,
                msg=f"Deployment info file is missing: {deployment_info}",
                state=DeploymentState.ERROR,
            )

        return ActionStatusInfo(ActionStatus.OK, state=DeploymentState.READY)

    def _delete_deployment(self, deployment_dir):
        obj_list = self._s3.list_objects(Bucket=self._config.bucket_name, Prefix=deployment_dir)
        if S3Plugin.CONTENTS_KEY in obj_list:
            for obj in obj_list[S3Plugin.CONTENTS_KEY]:
                self._s3.delete_object(Bucket=self._config.bucket_name, Key=obj["Key"])

    def plugin_start(self):
        self._logger.info("S3 plugin_start called")

        obj_list = self._s3.list_objects(Bucket=self._config.bucket_name)
        self._logger.debug(pprint.pformat(obj_list))
        found_base_dir = self._is_path_exists(obj_list, self._config.base_dir)
        if not found_base_dir:
            status = ActionStatus.ERROR
            msg = "Unable to detect folder: {} in bucket: {}".format(
                self._config.base_dir, self._config.bucket_name
            )
            self._logger.info(msg)
        else:
            status = ActionStatus.OK
            msg = "all ok"
        return ActionStatusInfo(status, msg=msg)

    def plugin_stop(self):
        self._logger.info("S3 plugin_stop called")
        return ActionStatusInfo(ActionStatus.OK)

    def _create_deployment_structure(self, di: DeploymentInfo):
        self._logger.info(f"Applying deployment: {di.id}")
        assert di.model_artifact is not None

        deployment_dir = self._deployment_dir(di)
        obj_list = self._s3.list_objects(Bucket=self._config.bucket_name, Prefix=deployment_dir)
        self._logger.debug(pprint.pformat(obj_list))

        if not self._is_path_exists(obj_list, deployment_dir):
            self._logger.info(f"Deployment directory does not exist: {deployment_dir}")

        model_base_path = os.path.basename(di.model_artifact)
        model_path = os.path.join(deployment_dir, model_base_path)

        self._logger.info(
            "Uploading model artifact: {}, size: {}".format(
                di.model_artifact, os.path.getsize(di.model_artifact)
            )
        )
        self._s3.upload_file(
            Bucket=self._config.bucket_name, Key=model_path, Filename=str(di.model_artifact)
        )

        self._logger.info("Updating deployment info file")
        self._write_deployment_info_file(di)

    def deployment_start(self, di: DeploymentInfo):
        self._logger.info(f"Starting deployment {di.id}")

        self._create_deployment_structure(di)
        return ActionStatusInfo(ActionStatus.OK, state=DeploymentState.READY)

    def deployment_stop(self, deployment_id: str):
        """
        Stop the cron job and delete it
        :return:
        """
        self._logger.info("Stopping deployment - doing nothing - no file will be deleted")
        deployment_dir = self._deployment_dir_from_id(deployment_id)
        self._delete_deployment(deployment_dir)

        status = ActionStatus.OK
        return ActionStatusInfo(status=status, state=DeploymentState.STOPPED)

    def deployment_replace_model(self, di: DeploymentInfo):
        """
        Will put a model artifact in a place the prediction job can consume it
        :param deployment_info: Info about the deployment
        :param model_artifact_path:
        :return:
        """
        self._logger.info(f"-- Replacing model for deployment: {di.id} dry_run: {self._dry_run}")
        deployment_dir = self._deployment_dir(di)
        self._delete_deployment(deployment_dir)

        self._create_deployment_structure(di)
        return ActionStatusInfo(
            ActionStatus.OK,
            msg=f"Model replaced successfully, new model id: {di.new_model_id}",
            state=DeploymentState.READY,
        )

    def pe_status(self):
        """
        Do status check
        :return:
        """
        self._logger.info("Getting status of s3 model registry")
        obj_list = self._s3.list_objects(
            Bucket=self._config.bucket_name, Prefix=self._config.base_dir
        )
        if self._is_path_exists(obj_list, self._config.base_dir):
            status = ActionStatus.OK
            status_msg = None
        else:
            status = ActionStatus.ERROR
            status_msg = f"Error: no base dir: {self._config.base_dir}"

        self._logger.info(f"pe_status: {status} {status_msg}")
        return ActionStatusInfo(status=status, msg=status_msg)

    def deployment_status(self, di: DeploymentInfo):
        """
        :param deployment_info: Info about the deployment to check
        Do status check
        :return:
        """
        self._logger.info("Getting status for python batch deployment")
        deployment_dir = self._deployment_dir(di)

        return self._deployment_status(deployment_dir, di.model_format, di.model_execution_type)

    def deployment_list(self):
        self._logger.info("Getting the list of running deployments")

        deployments_map = {}
        deployment_set = self._get_deployment_dirs()

        for deployment_dir in deployment_set:
            deployments_status = self._deployment_status(deployment_dir)
            deployment_id = os.path.basename(deployment_dir).replace(
                self._config.deployment_dir_prefix, ""
            )
            deployments_map[deployment_id] = deployments_status.to_dict()

        if len(deployment_set) == 0:
            status_msg = "No containers running"
        else:
            status_msg = f"Number of deployments: {len(deployment_set)}"

        self._logger.info(status_msg)
        self._logger.info("Deployments: " + str(deployments_map))
        return ActionStatusInfo(ActionStatus.OK, msg=status_msg, data=deployments_map)
