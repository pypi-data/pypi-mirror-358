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

from typing import List, Optional

import httpx

from osdu_api.auth.authorization import TokenRefresher
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.clients.base_client import BaseClient
from osdu_api.model.http_method import HttpMethod
from osdu_api.model.storage.query_records_request import QueryRecordsRequest
from osdu_api.model.storage.record import Record

URL_PLACEHOLDER: str = "{}{}/{}"
RECORDS_ENDPOINT: str = "/records"


class RecordClient(BaseClient):
    """
    Holds the logic for interfacing with Storage's record api
    """

    def __init__(
        self,
        storage_url: Optional[str] = None,
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
        self.storage_url = storage_url or self.config_manager.get(
            'environment', 'storage_url')

    def create_update_records(self, records: List[Record], bearer_token=None):
        """
        Calls storage's api endpoint createOrUpdateRecords taking a list of record objects and constructing
        the body of the request
        Returns the response object for the call

        Example of code to new up a record:
        acl = Acl(['data.test1@opendes.testing.com'], ['data.test1@opendes.testing.com'])
        legal = Legal(['opendes-storage-1579034803194'], ['US'], LegalCompliance.compliant)
        ancestry = RecordAncestry([])
        id = 'opendes:welldb:123456'
        kind = 'opendes:welldb:wellbore:1.0.0'
        meta = [{}]
        version = 0
        data = {'id': 'test'}
        record = Record(id, version, kind, acl, legal, data, ancestry, meta)
        """
        records_data = self.prepare_records_data(records)
        return self.make_request(method=HttpMethod.PUT,
                                 url='{}{}'.format(self.storage_url, RECORDS_ENDPOINT),
                                 data=records_data,
                                 bearer_token=bearer_token)

    async def async_create_update_records(self, records: List[Record], bearer_token=None):
        records_data = self.prepare_records_data(records)
        return await self.make_async_request(method=HttpMethod.PUT,
                                             url='{}{}'.format(
                                                 self.storage_url, RECORDS_ENDPOINT),
                                             data=records_data, bearer_token=bearer_token)

    def get_latest_record(self, record_id: str, attributes: List[str] = [], bearer_token=None):
        """
        Calls storage's api endpoint getLatestRecordVersion taking the required attributes
        Returns the content for the response object
        """
        request_params = {'attribute': attributes}
        return self.make_request(method=HttpMethod.GET, params=request_params,
                                 url=(URL_PLACEHOLDER.format(
                                     self.storage_url, RECORDS_ENDPOINT, record_id)),
                                 bearer_token=bearer_token)

    async def async_get_latest_record(self, record_id: str, attributes: List[str] = [],
                                      bearer_token=None):
        request_params = {'attribute': attributes}
        return await self.make_async_request(method=HttpMethod.GET, params=request_params,
                                             url=(URL_PLACEHOLDER.format(self.storage_url, 
                                                                         RECORDS_ENDPOINT,
                                                                         record_id)),
                                             bearer_token=bearer_token)

    def get_specific_record(self, record_id: str, version: str, attributes: List[str] = [],
                            bearer_token=None):
        """
        Calls storage's api endpoint getSpecificRecordVersion taking the required attributes
        Returns the content for the response object
        """
        request_params = {'attribute': attributes}
        return self.make_request(method=HttpMethod.GET, params=request_params, url=(
            '{}{}/{}/{}'.format(self.storage_url, RECORDS_ENDPOINT, record_id, version)),
            bearer_token=bearer_token)

    async def async_get_specific_record(self, record_id: str, version: str,
                                        attributes: List[str] = [],
                                        bearer_token=None):
        request_params = {'attribute': attributes}
        return await self.make_async_request(method=HttpMethod.GET, params=request_params, url=(
            '{}{}/{}/{}'.format(self.storage_url, RECORDS_ENDPOINT, record_id, version)),
            bearer_token=bearer_token)

    def get_record_versions(self, record_id: str, bearer_token=None):
        """
        Calls storage's api endpoint getRecordVersions taking the one required parameter record id
        Returns the content for the response object for the call containing the list of versions.
        Find the versions in the response.content attribute
        """
        return self.make_request(method=HttpMethod.GET, url=(
            URL_PLACEHOLDER.format(self.storage_url, '/records/versions', record_id)),
            bearer_token=bearer_token)

    async def async_get_record_versions(self, record_id: str, bearer_token=None):
        return await self.make_async_request(method=HttpMethod.GET, url=(
            URL_PLACEHOLDER.format(self.storage_url, '/records/versions', record_id)),
            bearer_token=bearer_token)

    def delete_record(self, record_id: str, bearer_token=None):
        """
        Perform logical deletion of provided record ID. The record can be recovered.
        """
        return self.make_request(method=HttpMethod.POST,
                                 url=(URL_PLACEHOLDER.format(self.storage_url, RECORDS_ENDPOINT,
                                                             record_id)+':delete'),
                                 bearer_token=bearer_token)

    async def async_delete_record(self, record_id: str, bearer_token=None):
        return await self.make_async_request(method=HttpMethod.POST,
                                             url=(URL_PLACEHOLDER.format(self.storage_url,
                                                                         RECORDS_ENDPOINT,
                                                                         record_id)+':delete'),
                                             bearer_token=bearer_token)

    def purge_record(self, record_id: str, bearer_token=None, keep_latest=False):
        """
        Permanently delete a record from storage. The record cannot be recovered.
        If keep_latest is True the latest version will be kept and active, while older
        versions are permanently deleted from storage.
        """
        versions = ""
        if keep_latest:
            versions = "/versions"
        return self.make_request(method=HttpMethod.DELETE,
                                 url=(URL_PLACEHOLDER.format(self.storage_url, RECORDS_ENDPOINT,
                                                             record_id) + versions),
                                 bearer_token=bearer_token)

    async def async_purge_record(self, record_id: str, bearer_token=None, keep_latest=False):
        versions = ""
        if keep_latest:
            versions = "/versions"
        return await self.make_async_request(method=HttpMethod.DELETE,
                                             url=(URL_PLACEHOLDER.format(self.storage_url,
                                                                         RECORDS_ENDPOINT,
                                                                         record_id) + versions),
                                             bearer_token=bearer_token)

    def purge_record_versions(self, record_id: str, limit: int, bearer_token=None):
        return self.make_request(method=HttpMethod.DELETE,
                                 url=('{}{}/{}/versions?limit={}'.format(
                                     self.storage_url,
                                     '/records/',
                                     record_id,
                                     limit)),
                                 bearer_token=bearer_token)

    async def async_purge_record_versions(self, record_id: str, limit: int, bearer_token=None):
        return await self.make_async_request(method=HttpMethod.DELETE,
                                             url=('{}{}/{}/versions?limit={}'.format(
                                                 self.storage_url,
                                                 '/records/',
                                                 record_id, limit)),
                                             bearer_token=bearer_token)

    def query_records(self, query_records_request: QueryRecordsRequest, bearer_token=None):
        return self.make_request(method=HttpMethod.POST,
                                 url='{}{}'.format(
                                     self.storage_url, '/query/records'),
                                 data=query_records_request.to_JSON(), bearer_token=bearer_token)

    def query_record(self, record_id: str, bearer_token=None):
        return self.make_request(method=HttpMethod.GET,
                                 url=(URL_PLACEHOLDER.format(
                                     self.storage_url, RECORDS_ENDPOINT, record_id)),
                                 bearer_token=bearer_token)

    async def async_query_records(self, query_records_request: QueryRecordsRequest,
                                  bearer_token=None):
        return await self.make_async_request(method=HttpMethod.POST,
                                             url='{}{}'.format(
                                                 self.storage_url, '/query/records'),
                                             data=query_records_request.to_JSON(),
                                             bearer_token=bearer_token)

    async def async_query_record(self, record_id: str, bearer_token=None):
        return await self.make_async_request(method=HttpMethod.GET,
                                             url=(URL_PLACEHOLDER.format(self.storage_url,
                                                                         RECORDS_ENDPOINT,
                                                                         record_id)),
                                             bearer_token=bearer_token)

    @staticmethod
    def prepare_records_data(records):
        records_data = '['
        for record in records:
            records_data = '{}{}{}'.format(records_data, record.to_JSON(), ',')
        records_data = records_data[:-1]
        records_data = '{}{}'.format(records_data, ']')
        return records_data
