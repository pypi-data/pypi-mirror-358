# Copyright © 2020 Amazon Web Services
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
import asyncio
import unittest

import mock
import os
from osdu_api.clients.base_client import BaseClient
from osdu_api.clients.search.search_client import SearchClient
from osdu_api.model.search.query_request import QueryRequest
from osdu_api.configuration.config_manager import DefaultConfigManager


class TestSeachClient(unittest.TestCase):

    @mock.patch.object(BaseClient, '_refresh_service_principal_token', return_value="stubbed")
    def setUp(self, get_bearer_token_mock):
        config_path = os.path.dirname(os.path.abspath(__file__))
        self.client = SearchClient(
            config_manager=DefaultConfigManager(
                os.path.join(config_path, 'osdu_api.ini')),
            data_partition_id="opendes"
        )
        self.client.service_principal_token = 'stubbed'
        self.client.data_workflow_url = 'stubbed url'
        self.client.headers = {}

    @mock.patch.object(BaseClient, 'make_request', return_value="response")
    def test_make_request(self, make_request_mock):
        query_request = QueryRequest('kind', "data.ResourceName = \"trajectories - 1000.json\"")
        # Act
        response = self.client.query_records(query_request)
        # Assert
        assert response == make_request_mock.return_value

    @mock.patch.object(BaseClient, 'make_async_request', return_value="response")
    def test_make_async_request(self, make_request_mock):
        query_request = QueryRequest('kind', "data.ResourceName = \"trajectories - 2000.json\"")
        # Act
        response = asyncio.run(self.client.async_query_records(query_request))
        # Assert
        assert response == make_request_mock.return_value
