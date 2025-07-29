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
import os
import time
from abc import ABC
from typing import Any
from typing import Dict
from typing import List

import boto3
import botocore
from botocore.exceptions import ClientError

from bosun.plugin.constants import DeploymentState
from bosun.plugin.sagemaker.client.aws_utils import AwsTagsBuilder
from bosun.plugin.sagemaker.client.aws_utils import AwsUtils
from bosun.plugin.sagemaker.client.aws_utils import SageMakerRecourseFilter
from bosun.plugin.sagemaker.client.aws_utils import SageMakerTag
from bosun.plugin.sagemaker.config.config_keys import SageMakerEndpointState
from bosun.plugin.sagemaker.config.sagemaker_client_config import SageMakerConfig

DATAROBOT_PREFIX = "datarobot-"

SAGEMAKER_ENDPOINT_STATUS_MAPPING = {
    SageMakerEndpointState.IN_SERVICE: DeploymentState.READY,
    SageMakerEndpointState.OUT_OF_SERVICE: DeploymentState.STOPPED,
    SageMakerEndpointState.CREATING: DeploymentState.LAUNCHING,
    SageMakerEndpointState.UPDATING: DeploymentState.REPLACING_MODEL,
    SageMakerEndpointState.SYSTEM_UPDATING: DeploymentState.LAUNCHING,
    SageMakerEndpointState.ROLLING_BACK: DeploymentState.UNKNOWN,
    SageMakerEndpointState.DELETING: DeploymentState.SHUTTING_DOWN,
    SageMakerEndpointState.FAILED: DeploymentState.ERROR,
    SageMakerEndpointState.UPDATE_ROLLBACK_FAILED: DeploymentState.ERROR,
}


class BaseSageMakerClient(ABC):
    def __init__(self, config: SageMakerConfig = None):
        self._logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.config = config
        self.session = self.get_session()
        self._tags_client = self.session.client("resourcegroupstaggingapi")
        self._sagemaker_client = self.session.client("sagemaker")
        self._s3_client = self.session.client("s3")
        self._codebuild_client = self.session.client("codebuild")
        self._tags_builder = AwsTagsBuilder(
            pe_info=self.config.prediction_environment,
            di=self.config.deployment,
            custom_tags=self.config.get_custom_tags,
        )

    def get_session(self):
        """
        For session initialization Boto3 will check the next environment variables for credentials:
        AWS_ACCESS_KEY_ID - The access key for your AWS account.
        AWS_SECRET_ACCESS_KEY - The secret key for your AWS account.
        AWS_SESSION_TOKEN - The session key for your AWS account.
        """
        return boto3.Session(region_name=self.config.aws_region)

    def build_deployment_model_image(
        self,
        model_type,
        s3_model_artifact,
        deployment_id,
        model_id,
        output_model_s3_key,
        codebuild_project_name,
        model_replacement,
    ):
        """
        Utility method to upload custom model package,
        build image using AWS CodeBuild and push image to ECR
        """
        model_file = os.path.basename(s3_model_artifact)

        # TODO: refactor this:
        s3_base_path = s3_model_artifact.replace(model_file, "").replace("s3://", "")

        aws_ecr = self.config.default_model_image.split("/")[0]
        ecr_repo = self.config.default_model_image.replace(aws_ecr + "/", "")
        ecr_cache_prefix = f"{aws_ecr}/{self.config.aws_ecr_cache}/"

        build_spec_yaml = AwsUtils.get_build_config(model_type)

        # Checking that project already exist:
        codebuild_project = self.get_build_project(codebuild_project_name)

        env_variables_dict = {
            "MODEL_PACKAGE": model_file,
            "AWS_ECR": aws_ecr,
            "ECR_REPO": ecr_repo,
            "ECR_CACHE": ecr_cache_prefix,
            "DEPLOYMENT_ID": deployment_id,
            "MODEL_ID": model_id,
            "OUTPUT_MODEL_PATH": output_model_s3_key,
        }

        self._logger.info("Starting building Image and pushing to ECR...")
        if codebuild_project is None:
            self.create_code_build_project(
                codebuild_project_name,
                s3_base_path,
                build_spec_yaml,
                model_replacement,
            )
        else:
            self.update_code_build_project(
                codebuild_project_name, s3_base_path, build_spec_yaml, model_replacement
            )

        cm_pps_model_image = self.config.default_model_image + ":" + model_id

        build_id = self.start_code_build(codebuild_project_name, s3_base_path, env_variables_dict)

        # Waiting while building is finishing...
        # TODO: use waiter object here:
        build_status = "IN_PROGRESS"
        while build_status == "IN_PROGRESS":
            build_status = self.get_build_status(build_id)
            self._logger.debug(f"Image build status:{build_status}")
            time.sleep(30)

        if build_status == "SUCCEEDED":
            return cm_pps_model_image
        else:
            raise ValueError(f"Image build status: {build_status}")

    def upload_model_artifact(self, model_artifact: str, s3_model_deployment_path: str) -> str:
        # using basename to get artifact file name
        artifact_file = os.path.basename(model_artifact)
        s3_key = s3_model_deployment_path + artifact_file
        self._logger.info("Starting uploading model package to S3...")
        aws_s3_full_path = self.upload_model_to_s3(model_artifact, s3_key)
        self._logger.info(f"Model artifact: {aws_s3_full_path} uploading completed successfully")
        return aws_s3_full_path

    def get_sagemaker_resources_by_tags(
        self, resource_type_filters: List[Dict[str, str]], tag_filters: List[str]
    ) -> List[str]:
        try:
            resources = []
            paginator = self._tags_client.get_paginator("get_resources")
            # Initialize pagination
            page_iterator = paginator.paginate(
                ResourceTypeFilters=resource_type_filters,
                TagFilters=tag_filters,
                TagsPerPage=100,
            )
            # Loop through each page of results
            for page in page_iterator:
                page_response = self._process_aws_response(page)
                resources.extend(page_response)
            return resources
        except botocore.exceptions.ClientError as error:
            self._logger.error("Unexpected error: {}".format(error))
            raise error

        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))

    def get_sagemaker_endpoints_by_pe_tag(self) -> List[str]:
        return self.get_sagemaker_resources_by_tags(
            resource_type_filters=[
                SageMakerRecourseFilter.SAGEMAKER_ENDPOINT_FILTER.value,
            ],
            tag_filters=self._tags_builder.get_tag_keys(
                SageMakerTag.DATAROBOT_PREDICTION_ENVIRONMENT_TAG,
            ),
        )

    def get_sagemaker_endpoint_by_deployment_tag(self) -> List[str]:
        return self.get_sagemaker_resources_by_tags(
            resource_type_filters=[
                SageMakerRecourseFilter.SAGEMAKER_ENDPOINT_FILTER.value,
            ],
            tag_filters=self._tags_builder.get_tag_keys(
                SageMakerTag.DATAROBOT_PREDICTION_ENVIRONMENT_TAG,
                SageMakerTag.DATAROBOT_DEPLOYMENT_TAG,
            ),
        )

    def get_sagemaker_model_by_tag(self, model_replacement) -> List[str]:
        return self.get_sagemaker_resources_by_tags(
            resource_type_filters=[
                SageMakerRecourseFilter.SAGEMAKER_MODEL_FILTER.value,
            ],
            tag_filters=self._tags_builder.get_tag_keys(
                SageMakerTag.DATAROBOT_PREDICTION_ENVIRONMENT_TAG,
                SageMakerTag.DATAROBOT_DEPLOYMENT_TAG,
                (
                    SageMakerTag.DATAROBOT_NEW_MODEL_TAG
                    if model_replacement
                    else SageMakerTag.DATAROBOT_MODEL_TAG
                ),
            ),
        )

    def _process_aws_response(self, response: Dict[str, Any]) -> List[str]:

        if "ResourceTagMappingList" in response:
            resource_list = response.get("ResourceTagMappingList")

            sagemaker_endpoints_list = [
                AwsUtils.parse_aws_arn(item).get("resource") for item in resource_list
            ]

            return sagemaker_endpoints_list
        else:
            return []

    def get_sagemaker_endpoint_details(self, sagemaker_endpoint_name: str) -> Dict[str, Any]:
        endpoint_deployments_info = {}
        try:
            describe_endpoint_response = self._sagemaker_client.describe_endpoint(
                EndpointName=sagemaker_endpoint_name
            )
            endpoint_status = describe_endpoint_response.get("EndpointStatus")
            self._logger.debug(
                "Endpoint {} Status: {}".format(sagemaker_endpoint_name, endpoint_status)
            )
            deployment_state = SAGEMAKER_ENDPOINT_STATUS_MAPPING.get(
                SageMakerEndpointState(endpoint_status)
            )
            self._logger.debug("DataRobot deployment_state: {}".format(deployment_state))

            sagemaker_endpoint_config_name = describe_endpoint_response.get("EndpointConfigName")

            describe_endpoint_configuration_response = (
                self._sagemaker_client.describe_endpoint_config(
                    EndpointConfigName=sagemaker_endpoint_config_name
                )
            )

            endpoint_configuration_production_variants = (
                describe_endpoint_configuration_response.get("ProductionVariants")
            )
            for endpoint_production_variant in endpoint_configuration_production_variants:
                production_variant_name = endpoint_production_variant["VariantName"]
                if production_variant_name.startswith(DATAROBOT_PREFIX):
                    production_variant_model_name = endpoint_production_variant["ModelName"]
                    describe_model_response = self._sagemaker_client.describe_model(
                        ModelName=production_variant_model_name
                    )
                    model_id = describe_model_response["PrimaryContainer"]["Environment"][
                        "MODEL_ID"
                    ]
                    deployment_id = describe_model_response["PrimaryContainer"]["Environment"][
                        "DEPLOYMENT_ID"
                    ]
                    endpoint_deployments_info[deployment_id] = {
                        "model_id": model_id,
                        "endpoint_config_name": sagemaker_endpoint_config_name,
                        "variant_name": production_variant_name,
                        "sagemaker_model_name": production_variant_model_name,
                        "state": deployment_state,
                    }

            return endpoint_deployments_info

        except botocore.exceptions.ClientError as error:
            self._logger.error("Unexpected error: {}".format(error))
            raise error

        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))

    def upload_model_to_s3(self, sagemaker_model_artifact: str, s3_obj_name_model: str) -> str:
        """
        Upload model artifact to AWS S3
        """
        self._logger.info("Uploading to S3 Bucket: {}".format(self.config.bucket_name))
        aws_s3_path = "s3://" + self.config.bucket_name + "/" + s3_obj_name_model
        try:
            self._s3_client.upload_file(
                sagemaker_model_artifact, self.config.bucket_name, s3_obj_name_model
            )
            self._logger.info(f"Model uploaded to the S3 path: {aws_s3_path}")
            return aws_s3_path

        except ClientError as error:
            self._logger.info(f"Upload Failed to the S3 path: {aws_s3_path}")
            self._logger.error(error)
            raise error

        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))

    def create_sagemaker_model(
        self,
        sagemaker_model_name: str,
        ecr_repo_uri: str,
        s3_obj_name_model: str,
        model_env_variables: dict,
        model_replacement: bool = False,
    ) -> None:

        try:
            self._logger.info("Creating SageMaker Model: {}".format(sagemaker_model_name))

            response = self._sagemaker_client.create_model(
                ModelName=sagemaker_model_name,
                PrimaryContainer={
                    "Image": ecr_repo_uri,
                    "ImageConfig": {"RepositoryAccessMode": "Platform"},
                    "Mode": "SingleModel",
                    "ModelDataUrl": s3_obj_name_model,
                    "Environment": model_env_variables,
                },
                Tags=self._tags_builder.get_tags(
                    SageMakerTag.CUSTOM_TAGS,
                    SageMakerTag.DATAROBOT_PREDICTION_ENVIRONMENT_TAG,
                    SageMakerTag.DATAROBOT_DEPLOYMENT_TAG,
                    (
                        SageMakerTag.DATAROBOT_NEW_MODEL_TAG
                        if model_replacement
                        else SageMakerTag.DATAROBOT_MODEL_TAG
                    ),
                ),
                ExecutionRoleArn=self.config.aws_role_resource_arn,
            )

            if response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                self._logger.error(
                    "Error when creating Sagemaker Model {}".format(sagemaker_model_name)
                )
                raise ValueError(
                    "Error when creating Sagemaker Model {}".format(sagemaker_model_name)
                )
            else:
                self._logger.info("Created SageMaker model name: {}".format(sagemaker_model_name))
                self._logger.info(
                    "Created SageMaker model arn: {}".format(response.get("ModelArn"))
                )

        except botocore.exceptions.ClientError as error:
            self._logger.error("Unexpected error: {}".format(error))
            raise error

        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))

    def create_sagemaker_endpoint_configuration(
        self,
        sagemaker_endpoint_config_name: str,
        sagemaker_model_name: str,
        config_variant_name: str,
        instance_type: str,
        initial_instance_count: int,
        model_replacement: bool = False,
    ) -> None:

        self._logger.info(
            f"Creating Sagemaker Model Endpoint Configuration: {sagemaker_endpoint_config_name}"
        )

        try:
            ec_response = self._sagemaker_client.create_endpoint_config(
                EndpointConfigName=sagemaker_endpoint_config_name,
                ProductionVariants=[
                    {
                        "VariantName": config_variant_name,
                        "ModelName": sagemaker_model_name,
                        "InitialInstanceCount": initial_instance_count,
                        "InstanceType": instance_type,
                    }
                ],
                Tags=self._tags_builder.get_tags(
                    SageMakerTag.CUSTOM_TAGS,
                    SageMakerTag.DATAROBOT_PREDICTION_ENVIRONMENT_TAG,
                    SageMakerTag.DATAROBOT_DEPLOYMENT_TAG,
                    (
                        SageMakerTag.DATAROBOT_NEW_MODEL_TAG
                        if model_replacement
                        else SageMakerTag.DATAROBOT_MODEL_TAG
                    ),
                ),
            )

            if ec_response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                self._logger.error("Error when creating SageMaker endpoint configuration")
            else:
                self._logger.info(
                    "Sagemaker Endpoint Configuration {} Created!".format(
                        sagemaker_endpoint_config_name
                    )
                )
                self._logger.info(
                    "Sagemaker Endpoint Configuration arn: {}".format(
                        ec_response.get("EndpointConfigArn")
                    )
                )

        except botocore.exceptions.ClientError as error:
            self._logger.error("Unexpected error: {}".format(error))
            raise error

        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))

    def create_sagemaker_endpoint(
        self,
        sagemaker_endpoint_name: str,
        sagemaker_endpoint_config_name: str,
    ) -> None:

        try:
            # According to AWS docs:
            # Recommend that customers call DescribeEndpointConfig before calling CreateEndpoint
            # to minimize the potential impact of a DynamoDB eventually consistent read.
            self._logger.info("Checking that Sagemaker Endpoint Configuration exists...")
            describe_ep_config_response = self._sagemaker_client.describe_endpoint_config(
                EndpointConfigName=sagemaker_endpoint_config_name
            )
            if describe_ep_config_response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                self._logger.error(
                    "Error when submitting describe_endpoint_config request to Sagemaker"
                )
                self._logger.debug(str(describe_ep_config_response))
                raise ValueError(
                    "The parameters you provided are incorrect: "
                    "Sagemaker Endpoint Configuration name {}".format(
                        sagemaker_endpoint_config_name
                    )
                )

            self._logger.info(
                "Creating Sagemaker Model Endpoint... This process can take a few minutes"
            )

            create_endpoint_response = self._sagemaker_client.create_endpoint(
                EndpointName=sagemaker_endpoint_name,
                EndpointConfigName=sagemaker_endpoint_config_name,
                Tags=self._tags_builder.get_tags(
                    SageMakerTag.CUSTOM_TAGS,
                    SageMakerTag.DATAROBOT_PREDICTION_ENVIRONMENT_TAG,
                    SageMakerTag.DATAROBOT_DEPLOYMENT_TAG,
                ),
            )

            if create_endpoint_response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                self._logger.error("Error when sending endpoint creation request to Sagemaker")
                self._logger.debug(create_endpoint_response)
        except Exception as ex:
            self._logger.error("Error when sending endpoint creation request to Sagemaker")
            self._logger.debug(str(ex))

    def update_sagemaker_endpoint(
        self, sagemaker_endpoint_name: str, sagemaker_endpoint_new_config_name: str
    ) -> None:

        try:
            # According to AWS docs:
            # Recommend that customers call DescribeEndpointConfig before calling CreateEndpoint
            # to minimize the potential impact of a DynamoDB eventually consistent read.
            self._logger.info("Checking that Sagemaker Endpoint Configuration exists...")
            describe_ep_config_response = self._sagemaker_client.describe_endpoint_config(
                EndpointConfigName=sagemaker_endpoint_new_config_name
            )
            if describe_ep_config_response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                self._logger.error(
                    "Error when submitting describe_endpoint_config request to Sagemaker"
                )
                self._logger.debug(str(describe_ep_config_response))
                raise ValueError(
                    "The parameters you provided are incorrect: "
                    "Sagemaker Endpoint Configuration name {}".format(
                        sagemaker_endpoint_new_config_name
                    )
                )

            self._logger.info(
                "Updating Sagemaker Model Endpoint... This process can take a few minutes"
            )

            update_endpoint_response = self._sagemaker_client.update_endpoint(
                EndpointName=sagemaker_endpoint_name,
                EndpointConfigName=sagemaker_endpoint_new_config_name,
            )

            if update_endpoint_response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                self._logger.error("Error when sending endpoint update request to Sagemaker")
                self._logger.debug(update_endpoint_response)
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))
        except Exception as error:
            self._logger.error("Error when sending endpoint update request to Sagemaker")
            self._logger.debug(str(error))
            raise error

    def delete_sagemaker_endpoint(self, sagemaker_endpoint_name: str) -> None:
        """
        Deletes an endpoint.
        SageMaker frees up all the resources that were deployed when the endpoint was created.
        """
        try:
            self._logger.info(f"Deleting SageMaker Endpoint name={sagemaker_endpoint_name}")
            delete_endpoint_response = self._sagemaker_client.delete_endpoint(
                EndpointName=sagemaker_endpoint_name,
            )

            if delete_endpoint_response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                self._logger.error("Error when sending endpoint delete request to Sagemaker")
                self._logger.debug(delete_endpoint_response)
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))
        except Exception as error:
            self._logger.error("Error when sending endpoint delete request to Sagemaker")
            self._logger.debug(str(error))
            raise error

    def delete_sagemaker_endpoint_config(self, sagemaker_endpoint_config_name: str) -> None:
        """
        Deletes an Endpoint Configuration.
        """
        try:
            self._logger.info(
                f"Deleting SageMaker Endpoint Configuration name={sagemaker_endpoint_config_name}"
            )
            delete_endpoint_config_response = self._sagemaker_client.delete_endpoint_config(
                EndpointConfigName=sagemaker_endpoint_config_name,
            )

            if delete_endpoint_config_response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                self._logger.error("Error when sending endpoint config delete request to Sagemaker")
                self._logger.debug(delete_endpoint_config_response)
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))
        except Exception as error:
            self._logger.error("Error when sending endpoint config delete request to Sagemaker")
            self._logger.debug(str(error))
            raise error

    def delete_sagemaker_model_deployment(self, sagemaker_model_name: str) -> None:
        """
        Deletes a SageMaker model deployment.
        """
        try:
            self._logger.info(f"Deleting SageMaker model name={sagemaker_model_name}")
            delete_sagemaker_model_response = self._sagemaker_client.delete_model(
                ModelName=sagemaker_model_name,
            )

            if delete_sagemaker_model_response.get("ResponseMetadata").get("HTTPStatusCode") != 200:
                self._logger.error("Error when sending model delete request to Sagemaker")
                self._logger.debug(delete_sagemaker_model_response)
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))
        except Exception as error:
            self._logger.error("Error when sending model delete request to Sagemaker")
            self._logger.debug(str(error))
            raise error

    # TODO: probably better to incapsulate all required attributes into object
    def create_code_build_project(
        self,
        codebuild_project_name: str,
        s3_base_path: str,
        build_spec: str,
        model_replacement: bool,
    ) -> str:
        try:
            self._codebuild_client.create_project(
                name=codebuild_project_name,
                description="This Project automatically created by DataRobot",
                source={
                    "type": "S3",
                    "location": s3_base_path,
                    "insecureSsl": False,
                    "buildspec": build_spec,
                },
                secondarySources=[],
                artifacts={"type": "NO_ARTIFACTS"},
                secondaryArtifacts=[],
                cache={"type": "NO_CACHE"},
                environment={
                    "type": "LINUX_CONTAINER",
                    "image": "aws/codebuild/standard:5.0",
                    "computeType": "BUILD_GENERAL1_SMALL",
                    "privilegedMode": True,
                    "imagePullCredentialsType": "CODEBUILD",
                    "environmentVariables": [],
                },
                serviceRole=self.config.aws_codebuild_service_role,
                timeoutInMinutes=60,
                queuedTimeoutInMinutes=480,
                tags=self._tags_builder.get_tags_kv_lowercase(
                    SageMakerTag.CUSTOM_TAGS,
                    SageMakerTag.DATAROBOT_PREDICTION_ENVIRONMENT_TAG,
                    SageMakerTag.DATAROBOT_DEPLOYMENT_TAG,
                    (
                        SageMakerTag.DATAROBOT_NEW_MODEL_TAG
                        if model_replacement
                        else SageMakerTag.DATAROBOT_MODEL_TAG
                    ),
                ),
                badgeEnabled=False,
                logsConfig={
                    "cloudWatchLogs": {"status": "ENABLED"},
                    "s3Logs": {"status": "DISABLED", "encryptionDisabled": False},
                },
            )
            return codebuild_project_name
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))
        except Exception as error:
            self._logger.error("Error when sending create project request to CodeBuild")
            self._logger.debug(str(error))
            raise error

    @classmethod
    def _create_env_variables(cls, env_variables_dict: Dict[str, str]) -> List[Dict[str, str]]:
        env_variables = [
            {"name": variable_name, "value": variable_value, "type": "PLAINTEXT"}
            for variable_name, variable_value in env_variables_dict.items()
        ]
        return env_variables

    def start_code_build(
        self, codebuild_project_name: str, s3_base_path: str, env_variables_dict: Dict[str, str]
    ) -> str:
        try:
            env_variables_list = self._create_env_variables(env_variables_dict)
            codebuild_client_response = self._codebuild_client.start_build(
                projectName=codebuild_project_name,
                sourceLocationOverride=s3_base_path,
                environmentVariablesOverride=env_variables_list,
            )
            build_id = codebuild_client_response["build"]["id"]
            return build_id
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))
        except Exception as error:
            self._logger.error("Error when sending build request to CodeBuild")
            self._logger.debug(str(error))
            raise error

    def get_build_status(self, build_id: str) -> str:
        try:
            codebuild_client_response = self._codebuild_client.batch_get_builds(ids=[build_id])
            build_status = codebuild_client_response["builds"][0]["buildStatus"]
            return build_status
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))
        except Exception as error:
            self._logger.error("Error when sending create project request to CodeBuild")
            self._logger.debug(str(error))
            raise error

    def get_build_project(self, codebuild_project_name: str) -> str:
        try:
            codebuild_client_response = self._codebuild_client.batch_get_projects(
                names=[codebuild_project_name]
            )
            if (
                "projects" in codebuild_client_response
                and len(codebuild_client_response["projects"]) > 0
            ):
                build_project = codebuild_client_response["projects"][0]
                return build_project["arn"]
            else:
                return None
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))
        except Exception as error:
            self._logger.error("Error when sending create project request to CodeBuild")
            self._logger.debug(str(error))
            raise error

    # TODO: refactor this to reuse logic from create_code_build_project method
    def update_code_build_project(
        self,
        codebuild_project_name: str,
        s3_base_path: str,
        build_spec: str,
        model_replacement: bool,
    ) -> str:
        try:
            self._codebuild_client.update_project(
                name=codebuild_project_name,
                description="This Project automatically created by DataRobot",
                source={
                    "type": "S3",
                    "location": s3_base_path,
                    "insecureSsl": False,
                    "buildspec": build_spec,
                },
                secondarySources=[],
                artifacts={"type": "NO_ARTIFACTS"},
                secondaryArtifacts=[],
                cache={"type": "NO_CACHE"},
                environment={
                    "type": "LINUX_CONTAINER",
                    "image": "aws/codebuild/standard:5.0",
                    "computeType": "BUILD_GENERAL1_SMALL",
                    "privilegedMode": True,
                    "imagePullCredentialsType": "CODEBUILD",
                    "environmentVariables": [],
                },
                serviceRole=self.config.aws_codebuild_service_role,
                timeoutInMinutes=60,
                queuedTimeoutInMinutes=480,
                tags=self._tags_builder.get_tags_kv_lowercase(
                    SageMakerTag.CUSTOM_TAGS,
                    SageMakerTag.DATAROBOT_PREDICTION_ENVIRONMENT_TAG,
                    SageMakerTag.DATAROBOT_DEPLOYMENT_TAG,
                    (
                        SageMakerTag.DATAROBOT_NEW_MODEL_TAG
                        if model_replacement
                        else SageMakerTag.DATAROBOT_MODEL_TAG
                    ),
                ),
                badgeEnabled=False,
                logsConfig={
                    "cloudWatchLogs": {"status": "ENABLED"},
                    "s3Logs": {"status": "DISABLED", "encryptionDisabled": False},
                },
            )
            return codebuild_project_name
        except botocore.exceptions.ParamValidationError as error:
            raise ValueError("The parameters you provided are incorrect: {}".format(error))
        except Exception as error:
            self._logger.error("Error when sending create project request to CodeBuild")
            self._logger.debug(str(error))
            raise error
