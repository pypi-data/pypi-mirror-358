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

from osdu_api.model.crs_conversion.convert_points import ConvertPoints
from osdu_api.model.crs_conversion.convert_geo_json import ConvertGeoJson
from osdu_api.model.crs_conversion.convert_bin_grid import ConvertBinGrid
from osdu_api.model.crs_conversion.convert_trajectory import ConvertTrajectory


class CRSConversionClient(BaseClient):
    """
    Holds the logic for interfacing with CRS conversion Service api
    """

    def __init__(
        self,
        crs_conversion_url: Optional[str] = None,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger=None,
        user_id: Optional[str] = None
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger,
                         user_id)
        self.crs_conversion_url = crs_conversion_url or self.config_manager.get('environment', 'crs_conversion_url')

    def info(self, bearer_token=None) -> requests.Response:
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.crs_conversion_url, "info"),
            params={"data-partition-id": self.data_partition_id}, bearer_token=bearer_token)

    def convert_point(self, data: ConvertPoints, bearer_token=None) -> requests.Response:
        if not data:
            request_data = {}
        else:
            request_data = data.to_JSON()
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.crs_conversion_url, "convert"),
            data=request_data, bearer_token=bearer_token)

    def convert_bin_grid(self, data: ConvertBinGrid, bearer_token=None) -> requests.Response:
        if not data:
            request_data = {}
        else:
            request_data = data.to_JSON()
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.crs_conversion_url, "convertBinGrid"),
            data=request_data, bearer_token=bearer_token)

    def convert_trajectory(self, data: ConvertTrajectory, bearer_token=None) -> requests.Response:
        if not data:
            request_data = {}
        else:
            request_data = data.to_JSON()
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.crs_conversion_url, "convertTrajectory"),
            data=request_data, bearer_token=bearer_token)

    def convert_geo_json(self, data: ConvertGeoJson, bearer_token=None) -> requests.Response:
        if not data:
            request_data = {}
        else:
            request_data = data.to_JSON()
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.crs_conversion_url, "convertGeoJson"),
            data=request_data, bearer_token=bearer_token)
