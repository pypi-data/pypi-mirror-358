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


class Constants(Enum):
    LATEST_VERSION = "latest"
    AUTH_MODE_KEY = "key"
    USER_ASSIGNED_IDENTITY = "user_assigned"


class EndpointType(Enum):
    BATCH = "BATCH_ENDPOINT"
    ONLINE = "ONLINE_ENDPOINT"
    UNKNOWN = "default"

    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if member.value.lower() == value:
                return member
        return EndpointType.UNKNOWN


class ProvisioningState(Enum):
    CREATING = "Creating"
    DELETING = "Deleting"
    SCALING = "Scaling"
    UPDATING = "Updating"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    CANCELED = "Canceled"


class Key(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    # fields set from Bosun plugin configuration
    DATAROBOT_ENVIRONMENT_ID = auto()
    DATAROBOT_DEPLOYMENT_ID = auto()
    DATAROBOT_MODEL_ID = auto()
    DATAROBOT_MODEL_NAME = auto()
    DATAROBOT_MODEL_DESCRIPTION = auto()

    # TODO ask MS team to expose SystemData in Deployment and Endpoint objects
    # so we don't need to add workarounds
    DEPLOYMENT_CREATED_AT = auto()

    # fields set from Prediction Environment / additional metadata
    AZURE_SUBSCRIPTION_ID = auto()
    AZURE_RESOURCE_GROUP = auto()
    AZURE_WORKSPACE = auto()
    AZURE_LOCATION = auto()
    AZURE_ENVIRONMENT_TAGS = auto()
    AZURE_EVENTHUBS_NAMESPACE = auto()
    AZURE_EVENTHUBS_INSTANCE = auto()
    AZURE_MANAGED_IDENTITY_ID = auto()
    AZURE_MANAGED_IDENTITY_CLIENT_ID = auto()

    # fields set from Deployment additional metadata
    # configuration for endpoints [online, batch]

    # underscorized property name means it's some internal property and it's not rendered as
    # a list of key-values on UI. It may be rendered as a separate UI element (e.g. endpoint toggle)
    ENDPOINT_TYPE = auto()
    ENDPOINT_NAME = auto()
    DEPLOYMENT_NAME = auto()
    SCORING_TIMEOUT_SECONDS = auto()

    # online endpoint settings
    ENDPOINT_TRAFFIC = auto()
    # UTC datetime string in ISO 8601 format, e.g. 2020-01-01T12:34:56.999Z
    ENDPOINT_TRAFFIC_LAST_MODIFIED_AT = auto
    COMPUTE_VIRTUAL_MACHINE = auto()
    COMPUTE_INSTANCE_COUNT = auto()

    # batch endpoint settings
    OUTPUT_ACTION = auto()
    OUTPUT_FILE_NAME = auto()
    # Custom Output settings (CSV, Parquet)
    OUTPUT_FORMAT = auto()
    MINI_BATCH_SIZE = auto()
    MAX_RETRIES = auto()
    MAX_CONCURRENCY_PER_INSTANCE = auto()
    ERROR_THRESHOLD = auto()
    LOGGING_LEVEL = auto()
    COMPUTE_CLUSTER = auto()
    COMPUTE_CLUSTER_INSTANCE_COUNT = auto()

    # prediction explanations settings
    MAX_EXPLANATIONS = auto()
    THRESHOLD_HIGH = auto()
    THRESHOLD_LOW = auto()

    # Properties below are not exposed via UI
    ENDPOINT_CREATION_TIMEOUT = auto()
    ENDPOINT_DELETION_TIMEOUT = auto()
    ENDPOINT_DEPLOYMENT_TIMEOUT = auto()
    ENDPOINT_UPDATE_TIMEOUT = auto()
    DEPLOYMENT_DELETION_TIMEOUT = auto()
    DEPLOYMENT_LOG_LINES_COUNT = auto()
    ENVIRONMENT_VERSION = auto()

    AZURE_LOCAL_TESTING = auto()

    @classmethod
    def all(cls):
        return [e.name for e in cls]
