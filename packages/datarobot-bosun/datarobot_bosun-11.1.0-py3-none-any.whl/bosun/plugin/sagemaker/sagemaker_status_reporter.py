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
import logging
import os
from datetime import datetime
from datetime import timezone
from typing import Dict

import requests
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

from bosun.plugin.constants import BosunPluginConfigConstants
from bosun.plugin.deployment_info import DeploymentInfo
from bosun.plugin.sagemaker.config.config_keys import SageMakerEndpointType
from datarobot_mlops.common.config import ConfigConstants

logger = logging.getLogger(__name__)


class MLOpsSageMakerStatusReporter:
    def __init__(
        self,
        plugin_config: Dict,
        deployment: DeploymentInfo,
        endpoint_type: SageMakerEndpointType = SageMakerEndpointType.REALTIME,
        model_replacement: bool = False,
    ):
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        self.mlops_api_token = os.environ.get(ConfigConstants.MLOPS_API_TOKEN.name)
        self.mlops_service_url = plugin_config.get(BosunPluginConfigConstants.MLOPS_URL_KEY)
        self.verify_ssl = plugin_config.get(BosunPluginConfigConstants.MLOPS_AGENT_VERIFY_SSL, True)
        self.deployment = deployment
        self.endpoint_type = endpoint_type
        self.model_replacement = model_replacement
        self.auth_header = {"Authorization": f"Bearer {self.mlops_api_token}"}
        self.current_stage = 1
        self.is_logged_at_most_once = False

    def report_deployment(self, message: str):
        self.logger.info(message)
        remote_events_url = f"{self.mlops_service_url}/api/v2/remoteEvents/"
        total_stages = self._total_deployment_stages_count()
        event_payload = {
            "eventType": "deploymentInfo",
            "title": f"Deployment stage {self.current_stage} out of {total_stages}",
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "deploymentId": self.deployment.id,
        }
        self.current_stage += 1

        try:
            response = requests.post(
                url=remote_events_url,
                json=event_payload,
                headers=self.auth_header,
                verify=self.verify_ssl,
            )
            response.raise_for_status()
        except (ConnectionError, HTTPError, MaxRetryError):
            if not self.is_logged_at_most_once:
                logger.warning("Deployment event can not be reported to MLOPS", exc_info=True)
                self.is_logged_at_most_once = True

    def _total_deployment_stages_count(self):

        # [(Uploading model package), (Uploading model metadata), (Building model image),
        # (Creating SageMaker model), (Creating SageMaker endpoint configuration),
        # (Creating SageMaker Endpoint)]
        total_endpoint_creation_stages = 6

        # [(Get SageMaker endpoint), (Uploading model package), (Uploading model metadata),
        # (Building model image), (Creating SageMaker model), (Creating SageMaker endpoint configuration),
        # (Updating SageMaker Endpoint)]
        total_endpoint_updating_stages = 7

        return (
            total_endpoint_updating_stages
            if self.model_replacement
            else total_endpoint_creation_stages
        )
