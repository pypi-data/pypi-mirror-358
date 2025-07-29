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
import unittest

import mock
import os
from osdu_api.clients.base_client import BaseClient
from osdu_api.clients.data_workflow.data_workflow_client import DataWorkflowClient
from osdu_api.model.data_workflow.start_workflow import StartWorkflow
from osdu_api.model.http_method import HttpMethod
from osdu_api.configuration.config_manager import DefaultConfigManager


class TestDataWorkflowClient(unittest.TestCase):

    @mock.patch.object(BaseClient, 'make_request', return_value="response")
    @mock.patch.object(BaseClient, '_refresh_service_principal_token', return_value="stubbed")
    def test_make_request(self, get_bearer_token_mock, make_request_mock):
        # Arrange
        client = DataWorkflowClient(config_manager=DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini'), data_partition_id="opendes")
        client.service_principal_token = 'stubbed'
        client.data_workflow_url = 'stubbed url'
        client.headers = {}

        start_workflow = StartWorkflow('test-dag-name', {})

        # Act
        response = client.start_workflow(start_workflow)

        # Assert
        assert response == make_request_mock.return_value
