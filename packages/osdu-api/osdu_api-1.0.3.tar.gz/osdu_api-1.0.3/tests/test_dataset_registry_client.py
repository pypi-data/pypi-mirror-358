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
from osdu_api.clients.dataset.dataset_registry_client import DatasetRegistryClient
from osdu_api.model.dataset.create_dataset_registries_request import CreateDatasetRegistriesRequest
from osdu_api.model.http_method import HttpMethod
from osdu_api.model.storage.acl import Acl
from osdu_api.model.storage.legal import Legal
from osdu_api.model.storage.record import Record
from osdu_api.model.storage.record_ancestry import RecordAncestry
from osdu_api.configuration.config_manager import DefaultConfigManager


class TestDatasetRegistryClient(unittest.TestCase):

    @mock.patch.object(BaseClient, 'make_request', return_value="response")
    @mock.patch.object(BaseClient, '_refresh_service_principal_token', return_value="stubbed")
    def test_make_request(self, get_bearer_token_mock, make_request_mock):
        # Arrange
        client = DatasetRegistryClient(config_manager=DefaultConfigManager(os.getcwd() + '/tests/osdu_api.ini'), data_partition_id="opendes")
        client.service_principal_token = 'stubbed'
        client.dataset_registry_url = 'stubbed url'
        client.headers = {}

        acl = Acl(['data.test1@opendes.testing.com'], ['data.test1@opendes.testing.com'])
        legal = Legal(['opendes-storage-1579034803194'], ['US'], 'compliant')
        ancestry = RecordAncestry([])
        id = 'opendes:welldb:123456'
        kind = 'opendes:welldb:wellbore:1.0.0'
        meta = [{}]
        version = 0
        data = {'id': 'test'}
        test_record = Record(kind, acl, legal, data, id, version, ancestry, meta)

        create_dataset_registries = CreateDatasetRegistriesRequest([test_record])

        # Act
        response = client.register_dataset(create_dataset_registries)

        # Assert
        assert response == make_request_mock.return_value
