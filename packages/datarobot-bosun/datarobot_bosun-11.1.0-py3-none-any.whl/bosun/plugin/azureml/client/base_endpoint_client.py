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
import json
import logging
from abc import ABC
from abc import abstractmethod
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Dict
from typing import Iterable
from typing import Optional
from typing import Tuple
from typing import Union

from azure.ai.ml import MLClient
from azure.ai.ml._restclient.model_dataplane.models import ListViewType
from azure.ai.ml._restclient.v2022_05_01.models import BatchOutputAction
from azure.ai.ml._utils._arm_id_utils import AMLVersionedArmId
from azure.ai.ml.constants import AssetTypes
from azure.ai.ml.entities import BatchDeployment
from azure.ai.ml.entities import BatchEndpoint
from azure.ai.ml.entities import Deployment
from azure.ai.ml.entities import Endpoint
from azure.ai.ml.entities import Environment
from azure.ai.ml.entities import Model
from azure.ai.ml.entities import OnlineDeployment
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from dateutil.parser import parser

from bosun.plugin.azureml.config.azureml_client_config import AZURE_BASE_ENVIRONMENT
from bosun.plugin.azureml.config.azureml_client_config import CONDA_FILE_PATH
from bosun.plugin.azureml.config.azureml_client_config import EndpointConfig
from bosun.plugin.azureml.config.azureml_client_config import EndpointType
from bosun.plugin.azureml.config.config_keys import Key
from bosun.plugin.azureml.config.config_keys import ProvisioningState
from bosun.plugin.constants import DeploymentState
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.endpoint_info import EndpointInfo
from datarobot_mlops.common.version_util import DataRobotAppVersion
from datarobot_mlops.metric import AggregationHelper


class BaseEndpointClient(ABC):
    _EXTERNAL_TO_INTERNAL_STATE_MAP = {
        ProvisioningState.FAILED.value: DeploymentState.ERROR,
        ProvisioningState.SUCCEEDED.value: DeploymentState.READY,
        ProvisioningState.DELETING.value: DeploymentState.SHUTTING_DOWN,
        ProvisioningState.CANCELED.value: DeploymentState.STOPPED,
        ProvisioningState.CREATING.value: DeploymentState.LAUNCHING,
        ProvisioningState.SCALING.value: DeploymentState.LAUNCHING,
        ProvisioningState.UPDATING.value: DeploymentState.LAUNCHING,
    }

    ENDPOINT_TYPE = EndpointType.UNKNOWN

    FAIL_STATES = {
        ProvisioningState.FAILED,
        ProvisioningState.DELETING,
        ProvisioningState.CANCELED,
    }

    def __init__(self, config: EndpointConfig):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")

        self.config = config
        self.prediction_environment_tags = config[Key.AZURE_ENVIRONMENT_TAGS]
        self._client = MLClient(
            DefaultAzureCredential(),
            config[Key.AZURE_SUBSCRIPTION_ID],
            config[Key.AZURE_RESOURCE_GROUP],
            config[Key.AZURE_WORKSPACE],
        )
        self._local: bool = self.config[Key.AZURE_LOCAL_TESTING]

    def _get_local_parameter(self, endpoint_type):
        return {"local": self._local} if endpoint_type == EndpointType.ONLINE else {}

    @property
    def local_parameter(self):
        return self._get_local_parameter(self.ENDPOINT_TYPE)

    def get_deployment_name(
        self, endpoint_info: EndpointInfo, origin_deployment: DeploymentInfo
    ) -> str:
        """
        Returns either actual deployment name or original name as specified by user if
        deployment does not exist.

        Original deployment name specified by user may be modified with an unique prefix,
        which is possible after user executed the model_replacement action. This happens due to
        two deployments are created in the same endpoint (blue-green deployment) and AzureML
        requires a deployment name to be uniq.
        """
        endpoint_deployments = self.list_deployments_by_endpoint(endpoint_info.name)
        actual_deployment = endpoint_deployments.get(origin_deployment.id)

        return actual_deployment.name if actual_deployment else origin_deployment.name

    def find_environment(
        self, environment_name: str, environment_version: DataRobotAppVersion
    ) -> Optional[Environment]:
        try:
            self.logger.info(
                "Looking for environment %s (version %s)...", environment_name, environment_version
            )
            all_environment_versions: Iterable[Environment] = self._client.environments.list(
                name=environment_name,
                list_view_type=ListViewType.ACTIVE_ONLY,  # exclude archived environments
            )
            for environment in all_environment_versions:
                if environment.version == str(environment_version):
                    return environment

            self.logger.info(
                f"Environment version not found: {environment_version},"
                f"a new version will be built."
            )

        except HttpResponseError:
            self.logger.info(
                f"Environment {environment_name} does not exist,"
                f"a new environment will be built."
            )

    def get_latest_environment(self):
        environment: Environment = self.find_environment(
            self.config.environment_name,
            self.config.environment_version,
        )
        if environment:
            return environment

        self.logger.info(
            f"Building a new environment {self.config.environment_name} "
            f"(version {self.config.environment_version})..."
        )
        env_docker_image = Environment(
            image=AZURE_BASE_ENVIRONMENT,
            name=self.config.environment_name,
            description=(
                "DataRobot environment containing MLOPS library and wrappers to run scoring model."
            ),
            version=str(self.config.environment_version),
            conda_file=CONDA_FILE_PATH,
            tags=self.prediction_environment_tags,
        )
        return self._client.environments.create_or_update(env_docker_image)

    def copy_feature_types(self, source_dir, dest_dir):
        """
        Copies feature_types into the same directory as scoring code wrapper, so
        feature_types can be loaded before inference is started.
        """
        assert source_dir
        target_path = Path(dest_dir) / "feature_types.json"

        with open(source_dir, "r") as source_file:
            data = json.load(source_file)
        # MLOps monitoring library requires all feature data to be in a different format from what
        # the public API outputs.
        feature_types = [AggregationHelper.convert_feature_format(f) for f in data["data"]]

        with open(target_path, "w") as target_file:
            json.dump(feature_types, target_file)

    def register_model(self, deployment: DeploymentInfo):
        model_tags = {Key.DATAROBOT_MODEL_ID.value: deployment.id}
        model_tags.update(self.prediction_environment_tags)

        model = Model(
            name=f"dr-{deployment.current_model_id}",
            path=deployment.model_artifact,
            type=AssetTypes.CUSTOM_MODEL,
            tags={"name": deployment.model_name},
            description=deployment.description,
        )
        return self._client.models.create_or_update(model)

    def make_console_url(self, endpoint: Endpoint) -> Optional[str]:
        if self._local:
            return None  # Local endpoints don't have a console web address

        assert endpoint.id is not None
        workspace_id, etype, endpoint_name = endpoint.id.rsplit("/", 2)
        base = "realtime" if etype == "onlineEndpoints" else "batch"
        return f"https://ml.azure.com/endpoints/{base}/{endpoint_name}/detail?wsid={workspace_id}"

    def archive_model(self, model_name: str):
        self.logger.info("Deleting DataRobot model %s...", model_name)
        models = self._client.models.list(model_name)
        for model in models:
            self._client.models.archive(model.name, model.version)

    @classmethod
    def map_state(cls, provisioning_state):
        return cls._EXTERNAL_TO_INTERNAL_STATE_MAP.get(provisioning_state, DeploymentState.ERROR)

    def list_deployments(
        self, prediction_environment_id: str
    ) -> Dict[str, Tuple[str, str, DataRobotAppVersion]]:
        """
        :returns dict
            deployment ID to tuple(endpoint_name, deployment_state, environment_version)
        """
        self.logger.debug(
            "Retrieving list of deployments for prediction environment %s",
            prediction_environment_id,
        )
        prediction_environment_deployments = dict()
        for endpoint_type in (EndpointType.ONLINE, EndpointType.BATCH):
            if endpoint_type == EndpointType.BATCH and self._local:
                self.logger.info("Skipping listing batch endpoints when in local mode...")
                continue
            deployments = self.list_deployments_by_endpoint_type(
                prediction_environment_id, endpoint_type
            )
            self.logger.debug("Found deployments for %s: %s", endpoint_type, deployments)
            prediction_environment_deployments.update(deployments)
        return prediction_environment_deployments

    def get_environment_version(self, environment_id) -> Optional[DataRobotAppVersion]:
        if not environment_id:
            # environment does not exists
            return None

        if self._local:
            # in local mode, AML library returns Environment instead of ARM reference
            environment = environment_id
        else:
            # parse ARM reference and get Environment object
            arm_id = AMLVersionedArmId(environment_id)
            environment: Environment = self._client.environments.get(
                name=arm_id.asset_name, version=arm_id.asset_version
            )

        try:
            return DataRobotAppVersion(environment.version)
        except ValueError:
            # it's a manually created version, read semver from conda
            version_from_conda = environment.conda_file.get("version", "0.1.0")
            self.logger.info(
                f"Environment version was created manually {environment.name}:{environment.version}"
                f". Version from conda: {version_from_conda}."
            )
            return DataRobotAppVersion(version_from_conda)

    def list_deployments_by_endpoint_type(
        self, prediction_environment_id: str, endpoint_type: EndpointType
    ) -> Dict[str, Tuple[str, str, DataRobotAppVersion]]:
        """
        :returns dict
            deployment ID to tuple(endpoint_name, deployment_state)
        """
        result = dict()
        # Only OnlineEndpoint APIs support the local= kwarg
        endpoints_api_client, deployments_api_client = self._get_api_clients(endpoint_type)
        local_parameter = self._get_local_parameter(endpoint_type)

        endpoints = endpoints_api_client.list(**local_parameter)
        for endpoint in endpoints:
            # Multiple PEs can be mapped to a single AzureML workspace so make sure we are only
            # working on endpoints that _this_ PE actually owns.
            tag_value = endpoint.tags.get(Key.DATAROBOT_ENVIRONMENT_ID.value)
            if tag_value is None or tag_value != prediction_environment_id:
                continue

            datarobot_model_deployments = dict()
            deployments = deployments_api_client.list(
                endpoint_name=endpoint.name,
                **local_parameter,
            )
            for deployment in deployments:
                deployment_id = deployment.tags.get(Key.DATAROBOT_DEPLOYMENT_ID.value)
                if deployment_id is None:
                    self.logger.warning(
                        "Found deployment %s (endpoint %s) without the `datarobot_deployment_id` tag. "
                        "This deployment is not maintained by DataRobot.",
                        deployment.name,
                        endpoint.name,
                    )
                    continue  # skip non DR deployments

                # batch deployments don't have a provisioning state, thus use an endpoint state
                entity: Union[OnlineDeployment, BatchEndpoint] = (
                    deployment if endpoint_type == EndpointType.ONLINE else endpoint
                )
                deployment_state = self.map_state(entity.provisioning_state)
                deployment_env_version = self.get_environment_version(deployment.environment)
                datarobot_model_deployments[deployment_id] = (
                    endpoint.name,
                    deployment_state,
                    deployment_env_version,
                )
            result.update(datarobot_model_deployments)
        return result

    def find_endpoint_name_by_deployment_id(
        self, prediction_environment_id: str, deployment_id: str
    ) -> str:
        deployments = self.list_deployments(prediction_environment_id)
        deployment_info = deployments.get(deployment_id)
        if deployment_info:
            endpoint_name, _, _ = deployment_info
            return endpoint_name

    def list_deployments_by_endpoint(
        self, endpoint_name: str
    ) -> Dict[str, Union[BatchDeployment, OnlineDeployment]]:
        """
        :return:
            dictionary of DataRobot deployment ID and deployment
        """

        datarobot_model_deployments = dict()
        _, deployments_api_client = self._get_api_clients(self.ENDPOINT_TYPE)
        deployments = deployments_api_client.list(
            endpoint_name=endpoint_name, **self.local_parameter
        )

        for deployment in deployments:
            deployment_id = deployment.tags.get(Key.DATAROBOT_DEPLOYMENT_ID.value)
            if deployment_id is None:
                self.logger.warning(
                    "Found deployment %s (endpoint %s) without the `datarobot_deployment_id` tag. "
                    "This deployment is not maintained by DataRobot.",
                    deployment.name,
                    endpoint_name,
                )
                continue  # skip non DR deployments

            if self._local and (deployment.endpoint_name != endpoint_name):
                # filter deployments by the endpoint name
                # fix bug in the _local_deployment_helper.py::list
                # return only endpoint's deployments, instead of ALL the local deployments
                continue

            duplicate_deployment = datarobot_model_deployments.get(deployment_id)
            if duplicate_deployment:
                self.logger.warning(
                    "Found two deployments %s and %s (endpoint %s) with the same "
                    "`datarobot_deployment_id` tag value %s. Assuming it's a model replacement.",
                    deployment.name,
                    duplicate_deployment.name,
                    endpoint_name,
                    deployment_id,
                )
                # in a model replacement flow, two deployments may have the same deployment ID
                # return the latest deployment
                duplicated_deployments = {
                    self._created_at(deployment): deployment,
                    self._created_at(duplicate_deployment): duplicate_deployment,
                }
                latest_deployment_created_at = max(duplicated_deployments.keys())
                latest_deployment = duplicated_deployments.get(latest_deployment_created_at)
                deployment = latest_deployment
                self.logger.info("Only the latest deployment '%s' will be listed.", deployment.name)

            datarobot_model_deployments[deployment_id] = deployment

        return datarobot_model_deployments

    def _created_at(self, deployment: Deployment) -> datetime:
        utc_dt_str = deployment.environment_variables.get(Key.DEPLOYMENT_CREATED_AT.value)
        return parser().parse(utc_dt_str) if utc_dt_str else None

    def _get_api_clients(self, endpoint_type: EndpointType):
        endpoints_api_client = None
        deployments_api_client = None

        if endpoint_type == EndpointType.ONLINE:
            endpoints_api_client = self._client.online_endpoints
            deployments_api_client = self._client.online_deployments
        elif endpoint_type == EndpointType.BATCH:
            endpoints_api_client = self._client.batch_endpoints
            deployments_api_client = self._client.batch_deployments

        return endpoints_api_client, deployments_api_client

    def _get_env_vars(self, deployment: DeploymentInfo, model_filename) -> Dict[str, str]:
        """Generate env vars to use in deployments we create"""
        utc_dt = datetime.now(timezone.utc)
        utc_dt_str = utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        base_vars = {
            "DATAROBOT_MODEL_FILENAME": str(model_filename),
            "MONITORING_ENABLED": str(self.config.is_monitoring_enabled),
            # TODO ask MS team to expose SystemData in Deployment and Endpoint objects
            Key.DEPLOYMENT_CREATED_AT.value: utc_dt_str,
            # Our scoring script doesn't need Flask 1.x compatibility and just adds complexity
            "AML_FLASK_ONE_COMPATIBILITY": "False",
        }
        if deployment.is_prediction_explanations_supported:
            base_vars.update(
                {
                    "MAX_EXPLANATIONS": self.config[Key.MAX_EXPLANATIONS],
                    "THRESHOLD_HIGH": self.config[Key.THRESHOLD_HIGH],
                    "THRESHOLD_LOW": self.config[Key.THRESHOLD_LOW],
                }
            )
        # to enable custom output format, an output action should be "Summary Only"
        if self.config[Key.OUTPUT_ACTION] == BatchOutputAction.SUMMARY_ONLY.value:
            base_vars.update(
                {
                    "OUTPUT_FORMAT": self.config[Key.OUTPUT_FORMAT],
                    "OUTPUT_FILE_NAME": self.config[Key.OUTPUT_FILE_NAME],
                }
            )
        if self.config.is_monitoring_enabled:
            bootstrap_server = (
                f"{self.config[Key.AZURE_EVENTHUBS_NAMESPACE]}.servicebus.windows.net:9093"
            )
            association_id_column = None
            association_id_allow_missing = None
            if deployment.settings_path:
                with open(deployment.settings_path) as settings_file:
                    deployment_settings = json.load(settings_file)
                    association_id = deployment_settings.get("associationId")
                    if association_id:
                        association_id_column = association_id["columnNames"]
                        association_id_allow_missing = not association_id[
                            "requiredInPredictionRequests"
                        ]

                if association_id_column:
                    # composite association IDs are not supported
                    assert len(association_id_column) == 1
                    association_id_column = association_id_column[0]

            base_vars.update(
                {
                    "MLOPS_DEPLOYMENT_ID": deployment.id,
                    "MLOPS_MODEL_ID": deployment.current_model_id,
                    "MLOPS_ASSOCIATION_ID_COLUMN": association_id_column,
                    "MLOPS_ASSOCIATION_ID_ALLOW_MISSING_VALUES": association_id_allow_missing,
                    "MLOPS_SPOOLER_TYPE": "KAFKA",
                    "MLOPS_KAFKA_BOOTSTRAP_SERVERS": bootstrap_server,
                    "MLOPS_KAFKA_TOPIC_NAME": self.config[Key.AZURE_EVENTHUBS_INSTANCE],
                    # We are using a managed identity to authenticate with EventHubs, so we need to
                    # set the client_id of the user defined identity and turn on OAuth:
                    #   https://github.com/Azure/azure-sdk-for-python/blob/azure-identity_1.12.0/sdk/identity/azure-identity/azure/identity/_credentials/managed_identity.py#L70-L72
                    "MLOPS_KAFKA_SASL_MECHANISM": "OAUTHBEARER",
                    "MLOPS_KAFKA_SECURITY_PROTOCOL": "SASL_SSL",
                    "AZURE_CLIENT_ID": self.config[Key.AZURE_MANAGED_IDENTITY_CLIENT_ID],
                    # Recommended producer settings; see:
                    #   https://learn.microsoft.com/en-us/azure/event-hubs/apache-kafka-configurations
                    "MLOPS_KAFKA_METADATA_MAX_AGE_MS": "180000",
                    "MLOPS_KAFKA_REQUEST_TIMEOUT_MS": "60000",
                    "MLOPS_KAFKA_MAX_FLUSH_MS": "60000",
                }  # type: ignore
            )
        return base_vars

    def get_scoring_snippet(self, model_filename: str) -> str:
        scoring_template = self.SNIPPET_GENERATOR(model_filename=model_filename)
        return scoring_template.render()

    @property
    def SNIPPET_GENERATOR(self):
        raise NotImplementedError("Child classes should define this")

    @abstractmethod
    def create_endpoint(self, endpoint: EndpointInfo) -> str:
        pass

    @abstractmethod
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
        :param auth_mode: str, applicable only to Online endpoints
            mechanism used to authenticate HTTP inference requests [key, token]
        :param traffic_settings: dict, applicable only to Online endpoints
            containing the deployment name and its traffic value (int)
        :param default_deployment: str, applicable only to Batch endpoints
            default deployment used for batch predictions

        :returns DeploymentState
        """
        pass

    @abstractmethod
    def get_endpoint(self, endpoint_name: str) -> Endpoint:
        pass

    @abstractmethod
    def create_deployment(
        self,
        endpoint: EndpointInfo,
        deployment: DeploymentInfo,
        model,
        environment: Environment,
    ):
        pass

    @abstractmethod
    def delete_endpoint(self, endpoint_name: str):
        pass

    @abstractmethod
    def delete_deployment_by_id(self, endpoint: EndpointInfo, deployment: DeploymentInfo):
        """
        Deletes deployment by a deployment ID. If there are two or more deployments with the same ID,
        only the latest created deployment will be deleted.

        Used by the deployment stop action.
        """
        pass

    @abstractmethod
    def delete_deployment_by_name(self, endpoint: str, deployment_name: str):
        """
        Deletes deployment by its name. Deployment names are uniq, if there two or more deployments
        with the same Id, only the deployment with exact name match will be deleted.

        Used by the model replacement action.
        """
        pass

    @abstractmethod
    def deployment_status(
        self, endpoint: EndpointInfo, deployment: DeploymentInfo
    ) -> Union[None, Tuple[str, DataRobotAppVersion]]:
        pass

    def check_permissions(self):
        # TODO use active directory to check permissions
        raise NotImplementedError()

    def check_quota(self):
        # TODO use quota rest api
        raise NotImplementedError()


class ListOnlyEndpointClient(BaseEndpointClient):
    """
    When action does not provide a DeploymentInfo, specific endpoint client can't be configured,
    so this "generic" client will be used.

    Used by pe_status and deployments_list actions to get list of deployments in endpoint.
    """

    def create_endpoint(self, endpoint: EndpointInfo) -> str:
        raise NotImplementedError

    def update_endpoint(self, endpoint: EndpointInfo) -> str:
        raise NotImplementedError

    def get_endpoint(self, endpoint_name: str) -> Endpoint:
        raise NotImplementedError

    def create_deployment(
        self,
        endpoint: EndpointInfo,
        deployment: DeploymentInfo,
        model,
        environment: Environment,
    ):
        raise NotImplementedError

    def delete_endpoint(self, endpoint: EndpointInfo):
        raise NotImplementedError

    def delete_deployment_by_id(self, endpoint: EndpointInfo, deployment: DeploymentInfo):
        raise NotImplementedError

    def delete_deployment_by_name(self, endpoint: EndpointInfo, deployment_name: str):
        raise NotImplementedError

    def deployment_status(
        self, endpoint: EndpointInfo, deployment: DeploymentInfo
    ) -> Union[None, Tuple[str, DataRobotAppVersion]]:
        raise NotImplementedError
