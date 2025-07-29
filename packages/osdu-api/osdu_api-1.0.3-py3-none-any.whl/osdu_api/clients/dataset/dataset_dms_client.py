# Copyright © 2020 Amazon Web Services
# Copyright 2022 Google LLC
# Copyright 2022 EPAM Systems
#
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
import requests
from typing import Optional

from osdu_api.auth.authorization import TokenRefresher
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.clients.base_client import BaseClient
from osdu_api.model.dataset.get_dataset_registry_request import GetDatasetRegistryRequest
from osdu_api.model.http_method import HttpMethod
from typing import Any, Optional
import os

class DatasetDmsClient(BaseClient):
    """
    Holds the logic for interfacing with Data Registry Service's DMS api
    """

    def __init__(
        self,
        dataset_url: Optional[str] = None,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger=None,
        user_id: Optional[str] = None
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger,
                         user_id)
        self.dataset_url = dataset_url or self.config_manager.get('environment', 'dataset_url')

    def _get_instructions(self, slug: str, params: dict, bearer_token=None) -> requests.Response:
        return self.make_request(method=HttpMethod.GET, url='{}{}'.format(self.dataset_url, slug),
            params=params, bearer_token=bearer_token)

    def _post_instructions(self, slug: str, data: Optional[GetDatasetRegistryRequest], bearer_token=None) -> requests.Response:
        if not data:
            request_data = {}
        else:
            request_data = data.to_JSON()
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.dataset_url, slug),
            data=request_data, bearer_token=bearer_token)

    def get_storage_instructions(self, kind_sub_type: str, bearer_token=None) -> requests.Response:
        return self._get_instructions('/getStorageInstructions', {'kindSubType': kind_sub_type}, bearer_token)

    def get_retrieval_instructions(self, record_id: str, bearer_token=None) -> requests.Response:
        return self._get_instructions('/getRetrievalInstructions', {'id': record_id}, bearer_token)

    def get_multiple_retrieval_instructions(
        self,
        get_dataset_registry_request: GetDatasetRegistryRequest,
        bearer_token=None
    ) -> requests.Response:
        return self._post_instructions('/getRetrievalInstructions', get_dataset_registry_request, bearer_token)

    def retrieval_instructions(self, record_id: str, bearer_token=None) -> requests.Response:
        return self._get_instructions('/retrievalInstructions', {'id': record_id}, bearer_token)

    def multiple_retrieval_instructions(
        self,
        get_dataset_registry_request: GetDatasetRegistryRequest,
        bearer_token=None
    ) -> requests.Response:
        return self._post_instructions('/retrievalInstructions', get_dataset_registry_request, bearer_token)

    def storage_instructions(self, kind_sub_type: str, bearer_token=None) -> requests.Response:
        return self._post_instructions(f'/storageInstructions?kindSubType={kind_sub_type}', None, bearer_token)

    def put_file(self, url: str, data: Any = '',
                 no_auth: bool = False) -> requests.Response:
        headers = {}
        if os.getenv("CLOUD_PROVIDER") == "azure":
            headers["x-ms-blob-type"] = "BlockBlob"
        return self.make_request(method=HttpMethod.PUT, add_headers=headers, url=url, data=data,
                                 no_auth=no_auth)
