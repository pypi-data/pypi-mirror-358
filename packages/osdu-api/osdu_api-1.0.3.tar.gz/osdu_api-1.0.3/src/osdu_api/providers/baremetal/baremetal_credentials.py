#  Copyright 2022 Google LLC
#  Copyright 2022 EPAM Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""Keycloak Credentials module."""

import logging
import os

import requests
from tenacity import retry, stop_after_attempt

from osdu_api.providers.constants import BAREMETAL_PROVIDER
from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BaseCredentials

logger = logging.getLogger(__name__)

RETRIES = 3


@ProvidersFactory.register(BAREMETAL_PROVIDER)
class KeycloakCredentials(BaseCredentials):
    """Keycloak Credentials Provider."""

    DEFAULT_ACCESS_SCOPES = ["openid"]

    def __init__(
        self,
        auth_url: str = None,
        client_id: str = None,
        client_secret=None,
        access_scopes: list = None
    ):
        """
        :param auth_url: Auth url, defaults to None
        :type auth_url: str, optional
        :param client_id: ClientID, defaults to None
        :type client_id: str, optional
        :param client_secret: ClientSecret, defaults to None
        :type client_secret: str, optional
        :param access_scopes: Access Scopes, defaults to None
        :type access_scopes: list, optional
        """
        self._access_token = None
        self._access_scopes = access_scopes or self.DEFAULT_ACCESS_SCOPES
        try:
            self._auth_url = auth_url or os.environ["KEYCLOAK_AUTH_URL"]
            self._client_id = client_id or os.environ["KEYCLOAK_CLIENT_ID"]
            self._client_secret = client_secret or os.environ["KEYCLOAK_CLIENT_SECRET"]
        except KeyError:
            raise KeyError(
                "Set the following environmental vars: 'KEYCLOAK_AUTH_URL', 'KEYCLOAK_CLIENT_ID', 'KEYCLOAK_CLIENT_SECRET' "
                "or pass these values directly."
            )

    @retry(stop=stop_after_attempt(RETRIES))
    def refresh_token(self) -> str:
        """Refresh token.

        :return: Refreshed token
        :rtype: str
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'client_credentials',
            'scope': " ".join(self._access_scopes),
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }
        response = requests.post(
            self._auth_url,
            headers=headers,
            data=data
        )
        # we use idToken in Baremetal as access_token.
        access_token = response.json()["id_token"]

        self._access_token = access_token
        return self._access_token

    @property
    def access_token(self) -> str:
        """The access token.

        :return: Access token string.
        :rtype: str
        """
        return self._access_token
