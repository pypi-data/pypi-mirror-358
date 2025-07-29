#  Copyright © 2020 Amazon Web Services
#  Copyright 2020 Google LLC
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
import pytest

from osdu_api.auth.authorization import TokenRefresher
from osdu_api.clients.storage.record_client import RecordClient
from osdu_api.model.http_method import HttpMethod
from osdu_api.model.storage.acl import Acl
from osdu_api.model.storage.legal import Legal
from osdu_api.model.storage.record import Record
from osdu_api.model.storage.record_ancestry import RecordAncestry


class MockTokenRefresher(TokenRefresher):
    def refresh_token(self):
        return 'stubbed'


class TestRecordClient:
    @pytest.fixture
    def record_client(self, mocker) -> RecordClient:
        mocker.patch(
            'osdu_api.clients.base_client.BaseClient.make_request', return_value='response')
        mocker.patch(
            'osdu_api.clients.base_client.BaseClient.make_async_request', return_value='response')
        record_client = RecordClient(
            token_refresher=MockTokenRefresher(),
            data_partition_id='opendes',
            storage_url='https://host/api/storage')

        return record_client

    @pytest.fixture
    def test_record(self):
        acl = Acl(['data.test1@opendes.testing.com'],
                  ['data.test1@opendes.testing.com'])
        legal = Legal(['opendes-storage-1579034803194'], ['US'], 'compliant')
        ancestry = RecordAncestry([])
        id = 'opendes:welldb:123456'
        kind = 'opendes:welldb:wellbore:1.0.0'
        meta = [{}]
        tags = {'key': 'value'}
        version = 1234
        data = {'id': 'test'}

        return Record(kind, acl, legal, data, id, version, ancestry, meta, tags)

    def test_create_update_records_model_record(self, record_client, mocker, test_record):
        # Arrange
        target_url = f'{record_client.storage_url}/records'
        request_data = f'[{test_record.to_JSON()}]'
        # Act
        response = record_client.create_update_records([test_record])
        # Assert
        assert response == 'response'
        record_client.make_request.assert_called_with(
            method=HttpMethod.PUT, url=target_url, bearer_token=None, data=request_data)

    def test_async_create_update_records(self, record_client, test_record):
        target_url = f'{record_client.storage_url}/records'
        request_data = f'[{test_record.to_JSON()}]'

        response = asyncio.run(record_client.async_create_update_records([test_record]))
        assert response == 'response'
        record_client.make_async_request.assert_called_with(
            method=HttpMethod.PUT, url=target_url, bearer_token=None, data=request_data)

    def test_get_latest_record_version(self, record_client, test_record):
        record_id = test_record.id
        request_params = {'attribute': []}
        record_client.get_latest_record(record_id)
        target_url = f'{record_client.storage_url}/records/{record_id}'

        # Assert
        record_client.make_request.assert_called_with(
            method=HttpMethod.GET, params=request_params, url=target_url, bearer_token=None)

    def test_get_latest_record_version_async(self, record_client, test_record):
        record_id = test_record.id
        request_params = {'attribute': []}
        record_client.get_latest_record(record_id)
        target_url = f'{record_client.storage_url}/records/{record_id}'

        asyncio.run(record_client.async_get_latest_record(record_id))

        # Assert
        record_client.make_async_request.assert_called_with(
            method=HttpMethod.GET,
            params=request_params,
            url=target_url,
            bearer_token=None)

    def test_get_specific_record_version(self, record_client, test_record):
        record_id = test_record.id
        request_params = {'attribute': []}
        record_version = test_record.version
        target_url = f'{record_client.storage_url}/records/{record_id}/{record_version}'

        record_client.get_specific_record(record_id, record_version)

        # Assert
        record_client.make_request.assert_called_with(
            method=HttpMethod.GET, params=request_params, url=target_url, bearer_token=None)

    def test_get_async_specific_record_version(self, record_client, test_record):
        record_id = test_record.id
        request_params = {'attribute': []}
        record_version = test_record.version
        target_url = f'{record_client.storage_url}/records/{record_id}/{record_version}'

        # Act
        asyncio.run(record_client.async_get_specific_record(
            record_id, record_version))

        # Assert
        record_client.make_async_request.assert_called_with(method=HttpMethod.GET, params=request_params,
                                                            url=target_url,
                                                            bearer_token=None)

    def test_get_record_versions(self, record_client, test_record):
        record_id = test_record.id
        target_url = f'{record_client.storage_url}/records/versions/{record_id}'

        # Act
        record_client.get_record_versions(record_id)

        # Assert
        record_client.make_request.assert_called_with(method=HttpMethod.GET,
                                                      url=target_url, bearer_token=None)

    def test_get_async_record_versions(self, record_client, test_record):
        record_id = test_record.id
        target_url = f'{record_client.storage_url}/records/versions/{record_id}'

        # Act
        asyncio.run(record_client.async_get_record_versions(record_id))

        # Assert
        record_client.make_async_request.assert_called_with(
            method=HttpMethod.GET, url=target_url, bearer_token=None)

    def test_delete_record(self, record_client, test_record):
        # Arrange
        record_id = test_record.id
        target_url = f'{record_client.storage_url}/records/{test_record.id}:delete'

        # Act
        record_client.delete_record(record_id)

        # Assert
        record_client.make_request.assert_called_with(
            method=HttpMethod.POST,
            url=target_url,
            bearer_token=None)

    def test_purge_record(self, record_client, test_record):
        # Arrange
        record_id = test_record.id
        target_url = f'{record_client.storage_url}/records/{test_record.id}'

        # Act
        response = record_client.purge_record(record_id)

        # Assert
        record_client.make_request.assert_called_with(
            method=HttpMethod.DELETE,
            url=target_url,
            bearer_token=None)

    def test_purge_record_versions(self, record_client, test_record):
        # Arrange
        record_id = test_record.id
        target_url = f'{record_client.storage_url}/records/{test_record.id}/versions'

        # Act
        response = record_client.purge_record(record_id, keep_latest=True)

        # Assert
        record_client.make_request.assert_called_with(
            method=HttpMethod.DELETE,
            url=target_url,
            bearer_token=None)
