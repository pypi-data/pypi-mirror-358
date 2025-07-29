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

from typing import Optional

import httpx

from osdu_api.auth.authorization import TokenRefresher
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.clients.base_client import BaseClient
from osdu_api.model.http_method import HttpMethod
from osdu_api.model.search.query_request import QueryRequest


class SearchClient(BaseClient):
    """
    Holds the logic for interfacing with Search's query api
    """

    def __init__(
        self,
        search_url: Optional[str] = None,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger=None,
        user_id: Optional[str] = None,
        async_client: httpx.AsyncClient = httpx.AsyncClient()
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger,
                         user_id, async_client)
        self.search_url = search_url or self.config_manager.get('environment', 'search_url')

    def query_records(self, query_request: QueryRequest, bearer_token=None):
        return self.make_request(method=HttpMethod.POST,
                                 url='{}{}'.format(self.search_url, '/query'),
                                 data=query_request.to_JSON(), bearer_token=bearer_token)

    def query_with_cursor(self, query_request: QueryRequest, bearer_token=None):
        return self.make_request(method=HttpMethod.POST,
                                 url='{}{}'.format(self.search_url, '/query_with_cursor'),
                                 data=query_request.to_JSON(), bearer_token=bearer_token)

    def async_query_records(self, query_request: QueryRequest, bearer_token=None):
        return self.make_async_request(method=HttpMethod.POST,
                                       url='{}{}'.format(self.search_url, '/query'),
                                       data=query_request.to_JSON(), bearer_token=bearer_token)

    def async_query_with_cursor(self, query_request: QueryRequest, bearer_token=None):
        return self.make_async_request(method=HttpMethod.POST,
                                       url='{}{}'.format(self.search_url, '/query_with_cursor'),
                                       data=query_request.to_JSON(), bearer_token=bearer_token)
