# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.​
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import json
import importlib
import requests
from typing import Any, Optional

from osdu_api.auth.authorization import TokenRefresher
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.clients.base_client import BaseClient
from osdu_api.providers.aws.service_principal_util import get_service_principal_token
from osdu_api.model.http_method import HttpMethod

class PartitionClient(BaseClient):
    """Mirrors the pattern laid out in os core common for the java services by
    getting a service principal token and passing that to partition service. It
    then will pass along the response to Cloud Service Provider (CSP) specific code
    for a transformation into the final response.
    """

    def __init__(
        self,
        partition_url: Optional[str] = None,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger=None,
        user_id: Optional[str] = None
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger,
                         user_id)
        self.partition_url = partition_url or self.config_manager.get('environment', 'partition_url')

    def get_partition(
        self,
        data_partition_id: str,
        bearer_token: Optional[str] = None
    ) -> dict:
        """[summary]

        Args:
            data_partition_id (str): standard OSDU data partition id (osdu, opendes, etc.)
            bearer_token (str, optional): will be used instead of service principal token

        Raises:
            Exception: only when data partition id arg is empty
            err: only when response from partition service is bad

        Returns:
            dict: CSP-specific partition info
        """

        if data_partition_id is None:
            raise Exception("data partition id cannot be empty")

        if bearer_token is None:
            # explicitly passing service principal token because this use case
            # requires it be used even when other use cases have it disabled
            self._refresh_service_principal_token()
            bearer_token = self.service_principal_token
            self.logger.info("Successfully retrieved token")

        partition_info_converter_module_name = self.config_manager.get('provider', 'partition_info_converter_module')
        self.logger.debug(f"Partition converter module name: {partition_info_converter_module_name}")

        partition_info_converter = importlib.import_module('osdu_api.providers.%s.%s' % (self.provider, partition_info_converter_module_name))

        csp_response = {}
        response = self.make_request(
            method=HttpMethod.GET,
            url='{}{}/{}'.format(self.partition_url, '/partitions', data_partition_id),
            bearer_token=bearer_token
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            self.logger.error(f"Received status code {response.status_code} from partition service") # type: ignore
            raise err

        content = json.loads(response.content)
        csp_response = partition_info_converter.convert(content)
        return csp_response
