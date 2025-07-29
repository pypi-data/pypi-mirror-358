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
import configparser
import importlib
import logging
import os

import httpx
import requests
from typing import Any, Optional

import tenacity
from httpx import Response

from osdu_api.auth.authorization import authorize, TokenRefresher
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.configuration.config_manager import DefaultConfigManager
from osdu_api.constants import RETRY_MIN_WAIT, RETRY_MAX_WAIT, RETRY_MULTIPLIER, \
    RETRY_STOP_AFTER_ATTEMPT
from osdu_api.exceptions.exceptions import MakeRequestError
from osdu_api.model.http_method import HttpMethod
from osdu_api.utils.request import response_not_ok


class BaseClient:
    """
    Base client that is meant to be extended by service specific clients
    """

    def __init__(
        self,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger: Optional[Any] = None,
        user_id: Optional[str] = None,
        async_client: httpx.AsyncClient = None
    ):
        """
        Base client gets initialized with configuration values and a bearer token
        based on provider-specific logic
        """
        self._ssl_verify = True

        self._parse_config(config_manager, provider, data_partition_id)
        self.user_id = user_id

        self.unauth_retries = 0
        if self.use_service_principal:
            self._refresh_service_principal_token()

        self.logger = logging.getLogger(__name__) if logger is None else logger

        self.token_refresher = token_refresher
        self.async_client = async_client

    def _parse_config(
        self,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None
    ):
        """
        Parse config.

        :param config_manager: ConfigManager to get configs, defaults to None
        :type config_manager: BaseConfigManager, optional
        """
        if os.getenv('OSDU_API_DISABLE_SSL_VERIFICAITON') == 'iknowthemaninthemiddle':
            self._ssl_verify = False

        self.config_manager = config_manager or DefaultConfigManager()

        # self.use_service_principal is used by AWS only, so other CSPs can set this attribute to False in any way.
        try:
            self.provider = provider or self.config_manager.get('provider', 'name')
            self.use_service_principal = self.config_manager.getbool('environment',
                                                                     'use_service_principal', False)
            if self.use_service_principal:
                self.service_principal_module_name = self.config_manager.get('provider',
                                                                             'service_principal_module_name')
        except configparser.Error:
            self.use_service_principal = False

        if data_partition_id is None:
            self.data_partition_id = self.config_manager.get(
                'environment', 'data_partition_id')
        else:
            self.data_partition_id = data_partition_id


    def _refresh_service_principal_token(self):
        """
        The path to the logic to get a valid bearer token is dynamically injected based on
        what provider and entitlements module name is provided in the configuration yaml
        """
        entitlements_client = importlib.import_module(
            'osdu_api.providers.%s.%s' % (self.provider, self.service_principal_module_name))
        self.service_principal_token = entitlements_client.get_service_principal_token()

    def _send_request(self, method: HttpMethod, url: str, data: str, headers: dict,
                      params: dict) -> requests.Response:
        """
        Send request to OSDU

        :param method: HTTP method
        :type method: HttpMethod
        :param url: service's URL
        :type url: str
        :param data: request's data
        :type data: str
        :param headers: request's headers
        :type headers: dict
        :param params: params
        :type params: dict
        :return: response from OSDU service
        :rtype: requests.Response
        """
        if method == HttpMethod.GET:
            response = requests.get(url=url, params=params, headers=headers,
                                    verify=self._ssl_verify)
        elif method == HttpMethod.DELETE:
            response = requests.delete(url=url, params=params, headers=headers,
                                       verify=self._ssl_verify)
        elif method == HttpMethod.POST:
            response = requests.post(url=url, params=params, data=data, headers=headers,
                                     verify=self._ssl_verify)
        elif method == HttpMethod.PUT:
            response = requests.put(url=url, params=params, data=data, headers=headers,
                                    verify=self._ssl_verify)
        return response

    async def _send_async_request(self, method: HttpMethod, url: str, data, headers: dict,
                                  params: dict) -> requests.Response:
        if method == HttpMethod.GET:
            response = await self.async_client.get(url=url, params=params, headers=headers)
        elif method == HttpMethod.DELETE:
            response = await self.async_client.delete(url=url, params=params, headers=headers)
        elif method == HttpMethod.POST:
            response = await self.async_client.post(url=url, params=params, data=data,
                                                    headers=headers)
        elif method == HttpMethod.PUT:
            response = await self.async_client.put(url=url, params=params, data=data,
                                                   headers=headers)
        return response

    def _send_request_with_principle_token(
        self,
        method: HttpMethod,
        url: str,
        data: str,
        headers: dict,
        params: dict,
    ) -> requests.Response:
        bearer_token = self.service_principal_token
        if bearer_token is not None and 'Bearer ' not in bearer_token:
            bearer_token = 'Bearer ' + bearer_token

        headers["Authorization"] = bearer_token

        response = self._send_request(method, url, data, headers, params)

        if (response.status_code == 401 or response.status_code == 403) and self.unauth_retries < 1:
            self.unauth_retries += 1
            self._refresh_service_principal_token()
            self._send_request_with_principle_token(method, url, data, headers, params)

        self.unauth_retries = 0
        return response

    async def _send_async_request_with_principle_token(
        self,
        method: HttpMethod,
        url: str,
        data: str,
        headers: dict,
        params: dict,
    ) -> requests.Response:
        bearer_token = self.service_principal_token
        if bearer_token is not None and 'Bearer ' not in bearer_token:
            bearer_token = 'Bearer ' + bearer_token

        headers["Authorization"] = bearer_token

        response = await self._send_async_request(method, url, data, headers, params)

        if (response.status_code == 401 or response.status_code == 403) and self.unauth_retries < 1:
            self.unauth_retries += 1
            self._refresh_service_principal_token()
            await self._send_async_request_with_principle_token(method, url, data, headers, params)

        self.unauth_retries = 0
        return response

    def _send_request_with_bearer_token(
        self,
        method: HttpMethod,
        url: str,
        data: str,
        headers: dict,
        params: dict,
        bearer_token: str
    ) -> requests.Response:
        """
        Send request with bearer_token provided by SDK user.

        :param method: HTTP method
        :type method: HttpMethod
        :param url: service's URL
        :type url: str
        :param data: request's data
        :type data: str
        :param headers: request's headers
        :type headers: dict
        :param params: params
        :type params: dict
        :param bearer_token: bearer_token
        :type params: str
        :return: response from OSDU service
        :rtype: requests.Response
        """

        if bearer_token is not None and 'Bearer ' not in bearer_token:
            bearer_token = 'Bearer ' + bearer_token
        headers["Authorization"] = bearer_token

        response = self._send_request(method, url, data, headers, params)

        if not response.ok:
            response.raise_for_status()

        return response

    async def _send_async_request_with_bearer_token(
        self,
        method: HttpMethod,
        url: str,
        data: str,
        headers: dict,
        params: dict,
        bearer_token: str
    ) -> Response:

        if bearer_token is not None and 'Bearer ' not in bearer_token:
            bearer_token = 'Bearer ' + bearer_token
        headers["Authorization"] = bearer_token

        response: Response = await self._send_async_request(method, url, data, headers, params)

        if response.status_code != 200:
            response.raise_for_status()

        return response

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(RETRY_STOP_AFTER_ATTEMPT),
        wait=tenacity.wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT,
                                       max=RETRY_MAX_WAIT),
        retry=(tenacity.retry_if_result(response_not_ok) | tenacity.retry_if_exception_type(
            Exception)),
        retry_error_callback=lambda retry_state: retry_state.outcome.result()
    )
    @authorize()
    def _send_request_with_token_refresher(
        self,
        headers: dict,
        method: HttpMethod,
        url: str,
        data: str,
        params: dict
    ) -> requests.Response:
        return self._send_request(method, url, data, headers, params)

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(RETRY_STOP_AFTER_ATTEMPT),
        wait=tenacity.wait_exponential(multiplier=RETRY_MULTIPLIER, min=RETRY_MIN_WAIT,
                                       max=RETRY_MAX_WAIT),
        retry=(tenacity.retry_if_result(response_not_ok) | tenacity.retry_if_exception_type(
            Exception)),
        retry_error_callback=lambda retry_state: retry_state.outcome.result()
    )
    @authorize()
    async def _send_async_request_with_token_refresher(
        self,
        headers: dict,
        method: HttpMethod,
        url: str,
        data: str,
        params: dict
    ) -> requests.Response:
        return await self._send_async_request(method, url, data, headers, params)

    def make_request(
        self,
        method: HttpMethod,
        url: str,
        data: Any = '',
        add_headers: Optional[dict] = None,
        params: Optional[dict] = None,
        bearer_token: Optional[str] = None,
        no_auth: bool = False
    ) -> requests.Response:
        """
        Makes a request using python's built in requests library. Takes additional headers if
        necessary
        """
        add_headers = add_headers or {}
        params = params or {}

        headers = self.prepare_headers(add_headers, self.data_partition_id, self.user_id)

        if no_auth:
            response = self._send_request(method, url, data, headers, params)
        elif bearer_token:
            response = self._send_request_with_bearer_token(method, url, data, headers, params,
                                                            bearer_token)
        elif self.token_refresher:
            # _send_request_with_token_refresher has other method signature to work with @authorize decorator
            response = self._send_request_with_token_refresher(headers, method, url, data, params)
        elif self.use_service_principal:
            response = self._send_request_with_principle_token(method, url, data, headers, params)
        else:
            raise MakeRequestError("There is no strategy to get Bearer token.")
        return response

    async def make_async_request(
        self,
        method: HttpMethod,
        url: str,
        data: Any = '',
        add_headers: Optional[dict] = None,
        params: Optional[dict] = None,
        bearer_token: Optional[str] = None,
        no_auth: bool = False
    ) -> requests.Response:

        add_headers = add_headers or {}
        params = params or {}

        headers = self.prepare_headers(add_headers, self.data_partition_id, self.user_id)

        if no_auth:
            response = await self._send_async_request(method, url, data, headers, params)
        elif bearer_token:
            response = await self._send_async_request_with_bearer_token(method, url, data, headers,
                                                                  params,
                                                                  bearer_token)
        elif self.token_refresher:
            response = await self._send_async_request_with_token_refresher(headers, method, url, data,
                                                                     params)
        elif self.use_service_principal:
            response = await self._send_async_request_with_principle_token(method, url, data, headers,
                                                                     params)
        else:
            raise MakeRequestError("There is no strategy to get Bearer token.")
        return response

    @staticmethod
    def prepare_headers(add_headers, data_partition, user_id):
        headers = {
            'content-type': 'application/json',
            'data-partition-id': data_partition,
        }
        if user_id is not None:
            # TODO: come up with the single header for all CSP
            if os.getenv("ENTITLEMENTS_IMPERSONATION") in ("True", "true"):
                # it's for GC and Baremetal implementations
                headers["on-behalf-of"] = user_id
            else:
                # it's for Azure implementation
                headers['x-on-behalf-of'] = user_id
        for key, value in add_headers.items():
            headers[key] = value
        return headers
