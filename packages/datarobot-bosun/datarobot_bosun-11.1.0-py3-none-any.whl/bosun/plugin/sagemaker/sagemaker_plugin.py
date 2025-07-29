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
import time
from datetime import datetime
from typing import Any
from typing import Dict

from bosun.plugin.action_status import ActionDataFields
from bosun.plugin.action_status import ActionStatus
from bosun.plugin.action_status import ActionStatusInfo
from bosun.plugin.bosun_plugin_base import BosunPluginBase
from bosun.plugin.constants import DeploymentState
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.deployment_utils import DeploymentUtils as du
from bosun.plugin.endpoint_info import EndpointInfo
from bosun.plugin.sagemaker.client.aws_client import BaseSageMakerClient
from bosun.plugin.sagemaker.client.aws_utils import AwsUtils
from bosun.plugin.sagemaker.config.config_keys import Key
from bosun.plugin.sagemaker.config.config_keys import SageMakerEndpointType
from bosun.plugin.sagemaker.config.sagemaker_client_config import SageMakerConfig
from bosun.plugin.sagemaker.config.sagemaker_client_config import kv_validator
from bosun.plugin.sagemaker.sagemaker_status_reporter import MLOpsSageMakerStatusReporter


class SageMakerPlugin(BosunPluginBase):
    def __init__(self, plugin_config, private_config_file, pe_info, dry_run):
        super().__init__(plugin_config, private_config_file, pe_info, dry_run)
        self._logger.debug("SageMakerPlugin init")
        self._config = None

    def get_aws_client(
        self,
    ) -> BaseSageMakerClient:
        if not self._config:
            self._logger.debug("Loading config...")
            self._config = SageMakerConfig.read_config(
                parent_config=self._plugin_config,
                config_file_path=self._private_config_file,
                prediction_environment=self._pe_info,
                deployment=DeploymentInfo(self._deployment_info) if self._deployment_info else None,
            )
        self._logger.debug("Configuring AWS SageMaker client...")
        return BaseSageMakerClient(self._config)

    # =======Plugin required functions ===
    def plugin_start(self):
        """
        Checking access to AWS SageMaker
        :return:
        """
        self._logger.info("SageMaker plugin_start called")
        try:
            self.get_aws_client().get_sagemaker_endpoints_by_pe_tag()
            return ActionStatusInfo(ActionStatus.OK)
        except Exception as ex:
            status = ActionStatus.ERROR
            msg = "Unable to get access to AWS SageMaker"
            self._logger.error(msg)
            self._logger.debug(ex)
            return ActionStatusInfo(status, msg=msg)

    def plugin_stop(self):
        """
        Currently no operation is needed here
        :return: ActionStatusInfo
        """
        self._logger.info("SageMaker Plugin plugin_stop called")
        return ActionStatusInfo(ActionStatus.OK)

    def deployment_list(self):
        self._logger.debug("SageMaker Plugin deployment_list called")
        aws_client = self.get_aws_client()
        sagemaker_endpoints = aws_client.get_sagemaker_endpoints_by_pe_tag()
        deployments_status_map = {}
        for sagemaker_endpoint in sagemaker_endpoints:
            try:
                sagemaker_endpoint_status = aws_client.get_sagemaker_endpoint_details(
                    sagemaker_endpoint
                )

                endpoint_deployments_status = {
                    deployment_id: ActionStatusInfo(
                        ActionStatus.OK, state=deployment_details.get("state")
                    ).to_dict()
                    for deployment_id, deployment_details in sagemaker_endpoint_status.items()
                }
                deployments_status_map.update(endpoint_deployments_status)
            except Exception as ex:
                msg = f"Unable to get access to AWS SageMaker Endpoint: {sagemaker_endpoint}"
                self._logger.error(msg)
                self._logger.debug(ex)

        status_msg = (
            f"Found {len(deployments_status_map)} deployment(s)"
            if len(deployments_status_map) > 0
            else "No deployments found"
        )

        self._logger.info(status_msg)

        return ActionStatusInfo(ActionStatus.OK, msg=status_msg, data=deployments_status_map)

    def pe_status(self):
        """
        Verify access to AWS SageMaker service
        :return: ActionStatusInfo
        """
        self._logger.debug("SageMaker Plugin pe_status called")
        try:
            msg = "SageMaker connection successful"
            aws_client = self.get_aws_client()
            aws_client.get_sagemaker_endpoints_by_pe_tag()
            self._logger.debug(msg)
            return ActionStatusInfo(ActionStatus.OK, msg=msg)
        except Exception as ex:
            msg = "Unable to get access to AWS SageMaker"
            self._logger.error(msg)
            self._logger.debug(ex)
            return ActionStatusInfo(ActionStatus.ERROR, msg=msg)

    def get_sagemaker_endpoint_status(self, aws_client, sagemaker_endpoint_name, deployment_id):
        endpoint_details_result = aws_client.get_sagemaker_endpoint_details(sagemaker_endpoint_name)
        if deployment_id in endpoint_details_result:
            deployment_details = endpoint_details_result.get(deployment_id)
            sagemaker_model_id = deployment_details.get("model_id")
            self._logger.info(
                f"Found SageMaker Endpoint Configuration for deployment_id={deployment_id}"
                f" and  SageMaker Model with model_id={sagemaker_model_id}"
            )
            return ActionStatusInfo(
                ActionStatus.OK,
                state=deployment_details.get("state"),
                data={ActionDataFields.CURRENT_MODEL_ID: sagemaker_model_id},
            )
        else:
            return ActionStatusInfo(
                ActionStatus.UNKNOWN,
                msg=f"Error: Cant find endpoint configuration with deployment_id={deployment_id}",
                state=DeploymentState.ERROR,
            )

    def deployment_status(self, di: DeploymentInfo):
        """
        Checks consistency and state of SageMaker resources corresponding to DataRobot deployment:
        SageMaker endpoint exists in a healthy state and has correct endpoint configuration
        :param di: deployment information
        :return: ActionStatusInfo
        """
        self._logger.debug("SageMaker Plugin deployment_status called")
        try:
            aws_client = self.get_aws_client()
            self._logger.debug(f"Invoking get_sagemaker_endpoint_by_deployment_tag({di.id})")

            sagemaker_endpoint_names = aws_client.get_sagemaker_endpoint_by_deployment_tag()

            if len(sagemaker_endpoint_names) == 0:
                self._logger.info(f"SageMaker Endpoint for deployment_id={di.id} not found")
                return ActionStatusInfo(
                    ActionStatus.UNKNOWN,
                    msg=f"Error: SageMaker Endpoint for deployment_id={di.id} not found",
                    state=DeploymentState.STOPPED,
                )
            elif len(sagemaker_endpoint_names) == 1:
                sagemaker_endpoint_name = sagemaker_endpoint_names[0]
                self._logger.info(
                    f"Found SageMaker Endpoint: sagemaker_endpoint_name={sagemaker_endpoint_name} "
                    f"for deployment_id={di.id}, trying to get endpoint_status..."
                )
                return self.get_sagemaker_endpoint_status(
                    aws_client, sagemaker_endpoint_name, di.id
                )

            elif len(sagemaker_endpoint_names) > 1:
                return ActionStatusInfo(
                    ActionStatus.UNKNOWN,
                    msg=f"Error: Found multiple endpoints with the same deployment_id={di.id}",
                    state=DeploymentState.ERROR,
                )
        except Exception as ex:
            self._logger.error(f"SageMaker Endpoint for deployment_id={di.id} not found")
            return ActionStatusInfo(
                ActionStatus.ERROR,
                msg=f"Error message: {str(ex)}",
                state=DeploymentState.UNKNOWN,
            )

    def _get_s3_model_key(self, deployment_id: str, model_id: str) -> str:
        s3_model_deployment_path = (
            f"sagemaker/{self._pe_info.id}/deployments/{deployment_id}/models/{model_id}/"
        )
        return s3_model_deployment_path

    def env_var_dict(
        self,
        deployment_id: str,
        model_id: str,
        feature_types: Dict[str, Any] = None,
        deployment_settings: Dict[str, Any] = None,
        model_package_details: Dict[str, Any] = None,
    ):

        env_variables = {
            "DEPLOYMENT_ID": deployment_id,
            "MODEL_ID": model_id,
            "MLOPS_DEPLOYMENT_ID": deployment_id,
            "MLOPS_MODEL_ID": model_id,
            "ADDRESS": "0.0.0.0:8080",  # required for SageMaker
        }

        if feature_types is not None:
            input_header = [feature_column["name"] for feature_column in feature_types]
            self._logger.debug(f"DataRobot feature_names_list:{input_header}")
            env_variables.update(
                {
                    "INPUT_HEADER": ", ".join(
                        ['"{}"'.format(column_name) for column_name in input_header]
                    )
                }
            )

        drift_reporting_enabled = "False"
        if deployment_settings is not None:
            drift_reporting_enabled = str(
                deployment_settings["featureDrift"].get("enabled", False)
                or deployment_settings["targetDrift"].get("enabled", False)
            )

        if model_package_details is not None:
            target_details = model_package_details.get("target")
            if target_details is not None and target_details.get("type") is not None:
                target_type = target_details.get("type").lower()
                env_variables.update({"TARGET_TYPE": target_type})
                class_names = target_details.get("classNames")
                if target_type == "binary":
                    if class_names is not None and len(class_names) == 2:
                        env_variables.update({"POSITIVE_CLASS_LABEL": class_names[0]})
                        env_variables.update({"NEGATIVE_CLASS_LABEL": class_names[1]})
                elif target_type == "multiclass":
                    env_variables.update({"CLASS_LABELS_FILE": "/opt/code/classLabels.txt"})

            if target_details is not None and target_details.get("name") is not None:
                env_variables.update({"TARGET_NAME": target_details.get("name")})

        if self._config.get_mlops_sqs_queue_url:
            mlops_sqs_queue_url = (
                self._config.get_mlops_sqs_queue_url
                # adding actual region to the SQS url
                .replace("/queue.", f"/sqs.{self._config.aws_region}.")
            )
            env_variables.update(
                {
                    "MONITOR": "True",
                    "MONITOR_SETTINGS": f"spooler_type=sqs;sqs_queue_url={mlops_sqs_queue_url}",
                    "MLOPS_DRIFT_REPORTING_ENABLED": drift_reporting_enabled,
                    "PREDICTION_API_MONITORING_ENABLED": "True",
                    "AWS_REGION": self._config.aws_region,
                    "MLOPS_SQS_VISIBILITY_TIMEOUT": str(
                        self._config.get_mlops_sqs_visibility_timeout
                    ),
                }
            )
        else:
            env_variables.update(
                {
                    "MLOPS_DRIFT_REPORTING_ENABLED": "False",
                    "PREDICTION_API_MONITORING_ENABLED": "False",
                    "MONITOR": "False",
                }
            )
        return env_variables

    @staticmethod
    def get_model_type(di: DeploymentInfo) -> str:
        # TODO: refactor to enum and extend this model
        if di.model_execution_type == "custom_inference_model":
            return "custom_inference_model"
        elif di.model_execution_type == "dedicated" and di.model_format == "datarobotScoringCode":
            return "datarobot_scoring_code"
        else:
            raise ValueError(
                f"Not supported model format: type={di.model_execution_type};format={di.model_format}"
            )

    def manage_deployment(self, di: DeploymentInfo, model_replacement: bool = False):
        assert di.model_artifact is not None

        endpoint_info = self._get_endpoint_info()
        sagemaker_endpoint_name = endpoint_info.name

        aws_client = self.get_aws_client()
        model_type = self.get_model_type(di)

        info_message = "Initializing MLOpsSageMakerStatusReporter..."
        self._logger.debug(info_message)
        mlops_reporter = MLOpsSageMakerStatusReporter(
            plugin_config=self._plugin_config,
            deployment=di,
            endpoint_type=SageMakerEndpointType.REALTIME,  # This is only endpoint type supported for now
            model_replacement=model_replacement,
        )
        model_id = di.new_model_id if model_replacement else di.model_id
        instance_type = self._config.default_initial_instance_type
        instance_count = self._config.default_initial_instance_count

        try:
            # Step 0: Trying to get existing SageMaker Endpoint by Tag:
            self._logger.debug(f"Invoking get_sagemaker_endpoint_by_deployment_tag({di.id})")
            sagemaker_endpoint_names = aws_client.get_sagemaker_endpoint_by_deployment_tag()
            sagemaker_endpoint_count = len(sagemaker_endpoint_names)
            self._logger.debug(
                f"Found {str(sagemaker_endpoint_count)} existing "
                f"SageMaker endpoints with deployment_id={di.id}"
            )

            if sagemaker_endpoint_count > 1:
                self._logger.info(f"Found multiple endpoints with the same deployment_id={di.id}")
                return ActionStatusInfo(
                    ActionStatus.UNKNOWN,
                    msg=f"Error: Found multiple endpoints with the same deployment_id={di.id}",
                    state=DeploymentState.ERROR,
                )
            elif sagemaker_endpoint_count == 1:
                sagemaker_endpoint_name = sagemaker_endpoint_names[0]
                if not model_replacement:
                    # TODO: this case might be valid in case of multi-model deployment, but not supported yet
                    return ActionStatusInfo(
                        ActionStatus.UNKNOWN,
                        msg=f"Found existing SageMaker endpoint: {sagemaker_endpoint_name} with "
                        f"the same deployment_id={di.id}",
                        state=DeploymentState.ERROR,
                    )
                else:
                    info_message = (
                        f"Found existing SageMaker Endpoint: endpoint_name={sagemaker_endpoint_name} "
                        f"for deployment_id={di.id}, trying to update endpoint with a new model..."
                    )
                    self._logger.info(info_message)
                    mlops_reporter.report_deployment(info_message)
            else:  # in case of sagemaker_endpoint_count == 0:
                if model_replacement:
                    self._logger.info(f"SageMaker Endpoint for deployment_id={di.id} not found")
                    return ActionStatusInfo(
                        ActionStatus.UNKNOWN,
                        msg=f"SageMaker Endpoint for deployment_id={di.id} not found",
                        state=DeploymentState.STOPPED,
                    )

            # checking that SageMaker model created already:
            existing_model_check = aws_client.get_sagemaker_model_by_tag(model_replacement)

            if len(existing_model_check) == 0:
                info_message = "Uploading model package to S3..."
                self._logger.info(info_message)
                mlops_reporter.report_deployment(info_message)

                s3_obj_name_model = aws_client.upload_model_artifact(
                    di.model_artifact,
                    self._get_s3_model_key(di.id, model_id),
                )

                model_file = os.path.basename(s3_obj_name_model)
                output_model_s3_key = s3_obj_name_model.replace(model_file, "output/model.tar.gz")

                info_message = "Uploading model metadata to S3..."
                self._logger.info(info_message)
                mlops_reporter.report_deployment(info_message)
                env_variables = self.upload_model_metadata(aws_client, di, model_id)

                # creating aws-compatible unique name for the SageMaker model:
                sagemaker_model_name = AwsUtils.aws_resource_name(di.id, model_id)

                info_message = f"Start building model image: {sagemaker_model_name}"
                self._logger.info(info_message)
                mlops_reporter.report_deployment(info_message)

                # TODO: optimize logic to reuse same codebuild project
                codebuild_project_name = f"build-datarobot-{di.id}-{model_id}"

                ecr_model_image_repo_uri = aws_client.build_deployment_model_image(
                    model_type,
                    s3_obj_name_model,
                    di.id,
                    model_id,
                    output_model_s3_key,
                    codebuild_project_name,
                    model_replacement,
                )

                info_message = (
                    f"Creating SageMaker Model {sagemaker_model_name} with model_id={model_id}"
                )
                self._logger.info(info_message)

                # Step  Creating SageMaker Model
                mlops_reporter.report_deployment(info_message)

                aws_client.create_sagemaker_model(
                    sagemaker_model_name,
                    ecr_model_image_repo_uri,
                    output_model_s3_key,
                    env_variables,
                    model_replacement,
                )

                existing_model_check = aws_client.get_sagemaker_model_by_tag(model_replacement)

                if len(existing_model_check) == 1:
                    info_message = (
                        f"SageMaker Model {sagemaker_model_name} has been successfully created"
                    )
                    self._logger.info(info_message)
                else:
                    self._logger.info(f"SageMaker Model {sagemaker_model_name} Error")
                    return ActionStatusInfo(
                        ActionStatus.UNKNOWN,
                        msg=f"SageMaker Model {sagemaker_model_name} Error",
                        state=DeploymentState.STOPPED,
                    )

            elif len(existing_model_check) == 1:
                sagemaker_model_name = existing_model_check[0]
                info_message = f"Reusing existing SageMaker Model {sagemaker_model_name}"
                self._logger.info(info_message)
                mlops_reporter.report_deployment(info_message)
                mlops_reporter.report_deployment("Skipping Model package uploading")
                mlops_reporter.report_deployment("Skipping Model Image building")
                mlops_reporter.report_deployment("Skipping SageMaker Model creation")
            else:
                info_message = (
                    f"Found multiple existing SageMaker Models: {', '.join(existing_model_check)} "
                    f"with the same: deployment_id={di.id} and model_id={di.id}"
                )
                return ActionStatusInfo(
                    ActionStatus.UNKNOWN,
                    msg=info_message,
                    state=DeploymentState.ERROR,
                )

            # creating aws-compatible unique name for the SageMaker endpoint configuration:
            config_datetime_suffix = datetime.now().strftime("%Y%m%d-%H%M%S")
            sagemaker_endpoint_config_name = AwsUtils.aws_resource_name(
                di.id, config_datetime_suffix
            )

            # creating aws-compatible name for the SageMaker endpoint configuration variant name:
            sagemaker_endpoint_config_variant_name = AwsUtils.aws_resource_name("model", model_id)

            # Step 2 Creating SageMaker Endpoint Configuration:
            info_message = (
                f"Creation SageMaker endpoint configuration {sagemaker_endpoint_config_name} ..."
            )
            self._logger.debug(info_message)
            mlops_reporter.report_deployment(info_message)
            aws_client.create_sagemaker_endpoint_configuration(
                sagemaker_endpoint_config_name,
                sagemaker_model_name,
                sagemaker_endpoint_config_variant_name,
                instance_type,
                instance_count,
                model_replacement,
            )

            # Step 3 Creating/Updating SageMaker Endpoint
            if model_replacement:
                info_message = f"Updating SageMaker endpoint: {sagemaker_endpoint_name} ..."
                self._logger.debug(info_message)
                mlops_reporter.report_deployment(info_message)
                # Updating SageMaker Endpoint with new configuration
                aws_client.update_sagemaker_endpoint(
                    sagemaker_endpoint_name,
                    sagemaker_endpoint_config_name,
                )
                sagemaker_deployment_status = ActionStatusInfo(
                    ActionStatus.OK, state=DeploymentState.REPLACING_MODEL
                )
            else:
                # Creating new SageMaker Endpoint
                info_message = f"Creating new SageMaker endpoint: {sagemaker_endpoint_name} ..."

                self._logger.debug(info_message)
                mlops_reporter.report_deployment(info_message)
                aws_client.create_sagemaker_endpoint(
                    sagemaker_endpoint_name,
                    sagemaker_endpoint_config_name,
                )

                sagemaker_deployment_status = ActionStatusInfo(
                    ActionStatus.OK, state=DeploymentState.LAUNCHING
                )

            prediction_url = (
                f"https://runtime.sagemaker.{self._config.aws_region}.amazonaws.com"
                f"/endpoints/{sagemaker_endpoint_name}/invocations"
            )
            dashboard_url = (
                f"https://{self._config.aws_region}.console.aws.amazon.com/sagemaker"
                f"/home?region={self._config.aws_region}#/endpoints/{sagemaker_endpoint_name}"
            )
            data = {
                ActionDataFields.PREDICTION_URL: prediction_url,
                ActionDataFields.DASHBOARD_URL: dashboard_url,
            }

            while (
                sagemaker_deployment_status.status == ActionStatus.OK
                and sagemaker_deployment_status.state
                in [DeploymentState.LAUNCHING, DeploymentState.REPLACING_MODEL]
            ):
                time.sleep(30)
                sagemaker_deployment_status = self.get_sagemaker_endpoint_status(
                    aws_client, sagemaker_endpoint_name, di.id
                )
                self._logger.debug(
                    f"SageMaker endpoint status: {sagemaker_deployment_status.state}"
                )

            return ActionStatusInfo(
                sagemaker_deployment_status.status,
                state=sagemaker_deployment_status.state,
                data=data,
            )

        except Exception as error:
            self._logger.info(error)
            return ActionStatusInfo(ActionStatus.ERROR, msg="Error Deploying model to SageMaker")

    def upload_model_metadata(self, aws_client, di, model_id):

        feature_types = None
        deployment_settings = None
        model_package_details = None

        if di.feature_types_path is not None:
            feature_types = du.load_feature_types(di.feature_types_path)
            self._logger.debug(f"DataRobot Model feature_types:{feature_types}")
            s3_obj_feature_types = aws_client.upload_model_artifact(
                di.feature_types_path,
                self._get_s3_model_key(di.id, model_id),
            )
            self._logger.debug(f"DataRobot feature_types uploaded to:{s3_obj_feature_types}")
        else:
            self._logger.warning("Cant load feature_types: feature_types_path not provided!")
        if di.settings_path is not None:
            deployment_settings = du.load_deployment_settings(di.settings_path)
            self._logger.debug(f"DataRobot deployment_settings:{deployment_settings}")
            s3_obj_deployment_settings = aws_client.upload_model_artifact(
                di.settings_path,
                self._get_s3_model_key(di.id, model_id),
            )
            self._logger.debug(
                f"DataRobot deployment_settings uploaded to:{s3_obj_deployment_settings}"
            )
        else:
            self._logger.warning("Cant load deployment_settings: settings_path not provided!")
        if di.model_package_details_path is not None:
            self._logger.debug(
                f"DataRobot di.model_package_details_path:{di.model_package_details_path}"
            )
            model_package_details = du.load_deployment_settings(di.model_package_details_path)
            self._logger.debug(f"DataRobot target_info:{model_package_details}")
            s3_obj_model_package_details = aws_client.upload_model_artifact(
                di.model_package_details_path,
                self._get_s3_model_key(di.id, model_id),
            )
            self._logger.debug(
                f"DataRobot model_package_details uploaded to:{s3_obj_model_package_details}"
            )
            target_details = model_package_details.get("target")
            if target_details is not None and "Multiclass" == target_details.get("type"):
                class_names = target_details.get("classNames")
                if class_names is not None:
                    labels_file_dir = di.model_package_details_path.resolve().parent
                    labels_file_path = du.create_class_labels_file(labels_file_dir, class_names)
                    s3_obj_class_labels_file = aws_client.upload_model_artifact(
                        labels_file_path,
                        self._get_s3_model_key(di.id, model_id),
                    )
                    self._logger.debug(
                        f"DataRobot class_labels_file uploaded to:{s3_obj_class_labels_file}"
                    )
        else:
            self._logger.warning(
                "Cant load model_package_details: model_package_details_path not provided!"
            )

        return self.env_var_dict(
            di.id,
            model_id,
            feature_types,
            deployment_settings,
            model_package_details,
        )

    def deployment_start(self, di: DeploymentInfo):
        """
        Create a SageMaker model, SageMaker endpoint configuration and SageMaker endpoint
        corresponding to DataRobot deployment.
        :param di: deployment information
        :return:
        """
        self._logger.info("SageMaker Plugin deployment_start called")
        self._logger.info(f"DataRobot Model artifact:{di.model_artifact}")
        self._logger.info(f"DataRobot DeploymentInfo:{di}")
        self._logger.info(f"Starting deployment_id={di.id} with model_id={di.model_id}")
        return self.manage_deployment(di, False)

    def deployment_replace_model(self, di: DeploymentInfo):
        """
        Update SageMaker endpoint and configuration with a new model
        TODO: implement blue-green deployment strategy
        :param di: deployment information
        :return:
        """
        self._logger.info("SageMaker Plugin deployment_replace_model called")
        self._logger.info(f"DataRobot Model artifact:{di.model_artifact}")
        self._logger.info(f"DataRobot DeploymentInfo:{di}")
        self._logger.info(
            f"Starting replacing model_id={di.model_id} to new_model_id={di.new_model_id} for "
            f"deployment_id={di.id}"
        )
        return self.manage_deployment(di, True)

    def deployment_stop(self, deployment_id: str):
        """
        Deleting SageMaker Deployment
        :param deployment_id: deployment information
        :return:
        """
        self._logger.info("SageMaker Plugin deployment_stop called")
        try:
            aws_client = self.get_aws_client()
            self._logger.debug(
                f"Invoking get_sagemaker_endpoint_by_deployment_tag({deployment_id})"
            )
            sagemaker_endpoint_names = aws_client.get_sagemaker_endpoint_by_deployment_tag()

            if len(sagemaker_endpoint_names) == 0:
                self._logger.info(f"SageMaker Endpoint for deployment_id={deployment_id} not found")
                return ActionStatusInfo(
                    ActionStatus.OK,
                    msg=f"Error: SageMaker Endpoint for deployment_id={deployment_id} not found",
                    state=DeploymentState.STOPPED,
                )
            elif len(sagemaker_endpoint_names) > 1:
                self._logger.info(
                    f"Found multiple endpoints with the same deployment_id={deployment_id}"
                )
                return ActionStatusInfo(
                    ActionStatus.OK,
                    msg=f"Error: Found multiple endpoints with the same deployment_id={deployment_id}",
                    state=DeploymentState.ERROR,
                )
            else:
                sagemaker_endpoint_name = sagemaker_endpoint_names[0]
                self._logger.info(
                    f"Found SageMaker Endpoint: sagemaker_endpoint_name={sagemaker_endpoint_name} "
                    f"for deployment_id={deployment_id}, trying to delete endpoint ..."
                )

                sagemaker_endpoint_details = aws_client.get_sagemaker_endpoint_details(
                    sagemaker_endpoint_name
                )
                # Checking that deployment_id matches:
                if deployment_id in sagemaker_endpoint_details:
                    if len(sagemaker_endpoint_details) == 1:
                        # delete the endpoint if the last deployment in endpoint is deleted
                        endpoint_config_name = sagemaker_endpoint_details[deployment_id][
                            "endpoint_config_name"
                        ]
                        sagemaker_model_name = sagemaker_endpoint_details[deployment_id][
                            "sagemaker_model_name"
                        ]
                        self._logger.info(
                            "Going to delete the endpoint %s", sagemaker_endpoint_name
                        )
                        aws_client.delete_sagemaker_endpoint(sagemaker_endpoint_name)
                        self._logger.info(
                            "Going to delete the endpoint config %s",
                            endpoint_config_name,
                        )
                        aws_client.delete_sagemaker_endpoint_config(endpoint_config_name)
                        self._logger.info(
                            "Going to delete the endpoint model %s",
                            sagemaker_model_name,
                        )
                        aws_client.delete_sagemaker_model_deployment(sagemaker_model_name)

                        max_status_check_attempts = 5

                        for _ in range(max_status_check_attempts):
                            # TODO: move all time-delay value to configurable parameters
                            time.sleep(30)
                            sagemaker_endpoint_names = (
                                aws_client.get_sagemaker_endpoint_by_deployment_tag()
                            )
                            if len(sagemaker_endpoint_names) == 0:
                                return ActionStatusInfo(
                                    ActionStatus.OK, state=DeploymentState.STOPPED
                                )
                        else:
                            self._logger.warning(
                                "% is still not deleted but giving up waiting",
                                sagemaker_endpoint_name,
                            )
                            return ActionStatusInfo(ActionStatus.ERROR, state=DeploymentState.ERROR)

                    elif len(sagemaker_endpoint_details) > 1:
                        # TODO: handle cases where we have several deployments per single endpoint
                        # if endpoint contains multiple deployments, delete a single deployment by ID
                        return ActionStatusInfo(ActionStatus.OK, state=DeploymentState.UNKNOWN)

        except Exception as error:
            self._logger.info(error)
            return ActionStatusInfo(
                ActionStatus.ERROR, msg="Error deleting deployment from SageMaker"
            )

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

        tags_str = metadata.get(Key.AWS_ENVIRONMENT_TAGS.name)
        tags = kv_validator(tags_str, Key.AWS_ENVIRONMENT_TAGS)

        # if not set, creating aws-compatible unique name for the SageMaker Endpoint:
        default_sagemaker_endpoint_name = AwsUtils.aws_resource_name(
            self._pe_info.id, deployment_info.id
        )
        sagemaker_endpoint_name = metadata.get(
            Key.ENDPOINT_NAME.name, default_sagemaker_endpoint_name
        )
        return EndpointInfo(
            {
                "name": sagemaker_endpoint_name,
                "endpointType": metadata.get(
                    Key.ENDPOINT_TYPE.name, SageMakerEndpointType.REALTIME.name
                ),
                "predictionEnvironmentId": self._pe_info.id,
                "tags": tags,
            }
        )
