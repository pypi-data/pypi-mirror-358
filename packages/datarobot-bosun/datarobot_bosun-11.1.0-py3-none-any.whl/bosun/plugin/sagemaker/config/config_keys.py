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
from enum import Enum
from enum import auto


class SageMakerEndpointType(Enum):
    REALTIME = "REALTIME_INFERENCE"
    BATCH = "BATCH_TRANSFORM"
    SERVERLESS = "SERVERLESS_INFERENCE"
    ASYNC = "ASYNCHRONOUS_INFERENCE"
    UNKNOWN = "default"


class SageMakerModelDeploymentType(Enum):
    SINGLE = "SingleModel"
    MULTI = "MultiModel"


class SageMakerEndpointState(Enum):
    CREATING = "Creating"
    DELETING = "Deleting"
    UPDATING = "Updating"
    FAILED = "Failed"
    IN_SERVICE = "InService"
    OUT_OF_SERVICE = "OutOfService"
    SYSTEM_UPDATING = "SystemUpdating"
    ROLLING_BACK = "RollingBack"
    UPDATE_ROLLBACK_FAILED = "UpdateRollbackFailed"


class Key(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    # fields set from Bosun plugin configuration
    DATAROBOT_ENVIRONMENT_ID = auto()
    DATAROBOT_DEPLOYMENT_ID = auto()
    DATAROBOT_MODEL_ID = auto()
    DATAROBOT_MODEL_NAME = auto()
    DATAROBOT_MODEL_DESCRIPTION = auto()

    # so we don't need to add workarounds
    DEPLOYMENT_CREATED_AT = auto()

    # fields set from Prediction Environment / additional metadata
    AWS_REGION = auto()
    AWS_ECR_REPOSITORY = auto()
    AWS_ECR_CACHE = auto()
    AWS_S3_BUCKET = auto()

    AWS_ROLE_RESOURCE_ARN = auto()

    AWS_ROLE_SAGEMAKER_ARN = auto()
    AWS_ROLE_CODEBUILD_ARN = auto()

    MLOPS_SQS_VISIBILITY_TIMEOUT = auto()
    MLOPS_SQS_QUEUE_URL = auto()

    COMPUTE_VIRTUAL_MACHINE = auto()
    COMPUTE_INSTANCE_COUNT = auto()

    AWS_ENVIRONMENT_TAGS = auto()

    ENDPOINT_NAME = auto()
    ENDPOINT_TYPE = auto()

    @classmethod
    def all(cls):
        return [e.name for e in cls]
