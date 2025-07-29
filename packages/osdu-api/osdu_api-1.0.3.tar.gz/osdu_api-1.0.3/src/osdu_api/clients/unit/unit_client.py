# Copyright 2023 Geosiris
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
import re
from typing import Optional

from osdu_api.auth.authorization import TokenRefresher
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.clients.base_client import BaseClient
from osdu_api.model.http_method import HttpMethod

from osdu_api.model.unit.search_request import SearchRequest
from osdu_api.model.unit.conversion_abcd_request import ConversionABCDRequest
from osdu_api.model.unit.conversion_scale_offset_request import ConversionScaleOffsetRequest
from osdu_api.model.unit.measurement_request import MeasurementRequest
from osdu_api.model.unit.unit_request import UnitRequest
from osdu_api.model.unit.unit_system_request import UnitSystemRequest


# Unit API V3
# version 3.0
# Base path /api/unit
class UnitClient(BaseClient):

    def __init__(
        self,
        unit_client_url: Optional[str] = None,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger=None,
        user_id: Optional[str] = None
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger, user_id)
        self.unit_client_url = unit_client_url or self.config_manager.get('environment', 'unit_client_url')

    # ============
    # Health Check
    # ============

    # Enpoint: /_ah/liveness_check
    def get_liveness_check(
        self,
        bearer_token: Optional[str] = None):
        # As self.unit_client_url should ends with "/v3" we have to remove it for this request
        url = self.unit_client_url
        version_rgx = r"[/\\]v[\d]+[/\\]?$"
        search_version = re.search(version_rgx, self.unit_client_url)
        if search_version is not None:
            url = url[:url.rindex(search_version.group())]
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(url, '_ah/liveness_check'),
            params={},  bearer_token=bearer_token)

    # Enpoint: /_ah/readiness_check
    def get_readiness_check(
        self,
        bearer_token: Optional[str] = None):
        # As self.unit_client_url should ends with "/v3" we have to remove it for this request
        url = self.unit_client_url
        version_rgx = r"[/\\]v[\d]+[/\\]?$"
        search_version = re.search(version_rgx, self.unit_client_url)
        if search_version is not None:
            url = url[:url.rindex(search_version.group())]
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(url, '_ah/readiness_check'),
            params={},  bearer_token=bearer_token)

    # ========
    # Info Api
    # ========

    # Enpoint: v3/info
    def get_info(
        self,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'info'),
            params={},  bearer_token=bearer_token)

    # ============
    # Unit Api V 3
    # ============

    # Enpoint: v3/catalog
    def get_catalog(
        self,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'catalog'),
            params={},  bearer_token=bearer_token)

    # Enpoint: v3/catalog/lastmodified
    def get_last_modified(
        self,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'catalog/lastmodified'),
            params={},  bearer_token=bearer_token)

    # Enpoint: v3/catalog/mapstates
    def get_map_states(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'catalog/mapstates'),
            params={"offset": offset, "limit": limit, },  bearer_token=bearer_token)

    # Enpoint: v3/catalog/search
    def post_search(
        self,
        request: SearchRequest,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'catalog/search'),
            params={"offset": offset, "limit": limit, }, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: conversion/abcd
    def post_conversion_abcd(
        self,
        request: ConversionABCDRequest,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'conversion/abcd'),
            params={}, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: conversion/scale
    def post_conversion_scale_offset(
        self,
        request: ConversionScaleOffsetRequest,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'conversion/scale'),
            params={}, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: measurement
    def post_measurement(
        self,
        request: MeasurementRequest,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'measurement'),
            params={}, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: v3/measurement/list
    def get_measurements(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'measurement/list'),
            params={"offset": offset, "limit": limit, },  bearer_token=bearer_token)

    # Enpoint: v3/measurement/maps
    def get_measurement_maps(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'measurement/maps'),
            params={"offset": offset, "limit": limit, },  bearer_token=bearer_token)

    # Enpoint: v3/measurement/search
    def post_search_measurements(
        self,
        request: SearchRequest,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'measurement/search'),
            params={"offset": offset, "limit": limit, }, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: unit
    def post_unit(
        self,
        request: UnitRequest,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'unit'),
            params={}, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: v3/unit/maps
    def get_unit_maps(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'unit/maps'),
            params={"offset": offset, "limit": limit, },  bearer_token=bearer_token)

    # Enpoint: unit/measurement
    def post_units_by_measurement(
        self,
        request: MeasurementRequest,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'unit/measurement'),
            params={}, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: unit/measurement/preferred
    def post_preferred_units_by_measurement(
        self,
        request: MeasurementRequest,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'unit/measurement/preferred'),
            params={}, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: v3/unit/search
    def post_search_units(
        self,
        request: SearchRequest,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'unit/search'),
            params={"offset": offset, "limit": limit, }, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: v3/unit/symbol
    def get_unit_by_symbol(
        self,
        namespaces: str,
        symbol: str,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'unit/symbol'),
            params={"namespaces": namespaces, "symbol": symbol, },  bearer_token=bearer_token)

    # Enpoint: v3/unit/symbols
    def get_units_by_symbol(
        self,
        symbol: str,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'unit/symbols'),
            params={"symbol": symbol, },  bearer_token=bearer_token)

    # Enpoint: unit/unitsystem
    def post_unit_by_system_and_measurement(
        self,
        unit_system_name: str,
        request: MeasurementRequest,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'unit/unitsystem'),
            params={"unitSystemName": unit_system_name, }, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: unitsystem
    def post_unit_system(
        self,
        request: UnitSystemRequest,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.POST, url='{}/{}'.format(self.unit_client_url, 'unitsystem'),
            params={"offset": offset, "limit": limit, }, data=request.to_JSON(), bearer_token=bearer_token)

    # Enpoint: v3/unitsystem/list
    def get_unit_system_info_list(
        self,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
        bearer_token: Optional[str] = None):
        return self.make_request(method=HttpMethod.GET, url='{}/{}'.format(self.unit_client_url, 'unitsystem/list'),
            params={"offset": offset, "limit": limit, },  bearer_token=bearer_token)
