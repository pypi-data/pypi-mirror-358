# Copyright 2023 Geosiris Systems
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
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
from osdu_api.model.http_method import HttpMethod

from osdu_api.model.crs_catalog.post_crs_catalog_coordinate_transformation import PostCRSCatalogCoordinateTransformation
from osdu_api.model.crs_catalog.post_crs_catalog_coordinate_reference_system import PostCRSCatalogCoordinateReferenceSystem


class CRSCatalogClient(BaseClient):
    """
    Holds the logic for interfacing with CRS catalog Service api
    """

    def __init__(
        self,
        crs_catalog_url: Optional[str] = None,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger=None,
        user_id: Optional[str] = None
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger,
                         user_id)
        self.crs_catalog_url = crs_catalog_url or self.config_manager.get('environment', 'crs_catalog_url')

    def get_coordinate_transformation(self, data_id: Optional[str] = None, record_id: Optional[str] = None, bearer_token=None) -> requests.Response:
        params = {}
        if data_id is not None:
            params["dataId"] = data_id
        if record_id is not None:
            params["recordId"] = record_id
        return self.make_request(method=HttpMethod.GET, url='{}{}'.format(self.crs_catalog_url, "coordinate-transformation"),
            params=params, bearer_token=bearer_token)

    def post_coordinate_transformation(self, data: PostCRSCatalogCoordinateTransformation, bearer_token=None) -> requests.Response:
        if not data:
            request_data = {}
        else:
            request_data = data.to_JSON()
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.crs_catalog_url, "coordinate-transformation"),
            data=request_data, bearer_token=bearer_token)

    def get_coordinate_reference_system(self, data_id: Optional[str] = None, record_id: Optional[str] = None, bearer_token=None) -> requests.Response:
        params = {}
        if data_id is not None:
            params["dataId"] = data_id
        if record_id is not None:
            params["recordId"] = record_id
        return self.make_request(method=HttpMethod.GET, url='{}{}'.format(self.crs_catalog_url, "coordinate-reference-system"),
            params=params, bearer_token=bearer_token)

    def post_coordinate_reference_system(self, data: PostCRSCatalogCoordinateReferenceSystem, bearer_token=None) -> requests.Response:
        if not data:
            request_data = {}
        else:
            request_data = data.to_JSON()
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.crs_catalog_url, "coordinate-reference-system"),
            data=request_data, bearer_token=bearer_token)
