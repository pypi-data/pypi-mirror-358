#  Copyright © IBM Corporation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""IBM Credential Module."""

import json
import logging
import os

from keycloak import KeycloakOpenID
from osdu_api.providers.constants import IBM_CLOUD_PROVIDER
from osdu_api.providers.exceptions import RefreshSATokenError, SAFilePathError
from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BaseCredentials
from tenacity import retry, stop_after_attempt

logger = logging.getLogger(__name__)
RETRIES = 3

@ProvidersFactory.register(IBM_CLOUD_PROVIDER)
class IBMCredentials(BaseCredentials):
    """IBM Credential Provider"""

    def __init__(self):
        """Initialize IBM Credentials object"""
        self._access_token = None
        self._client_id = None
        self._client_secret = None
        self._username = None
        self._password = None
        self._scope = None
        self._tenant_id = None

    def _populate_ad_credentials(self) -> None:
        uri = os.getenv("KEYCLOACK_URI")
        realm = os.getenv("REALM_NAME")
        self._client_id = os.getenv("client_id")
        self._client_secret = os.getenv("client_secret")
        self._username = os.getenv("username")
        self._password = os.getenv("password")
        self._verifyVal = os.getenv('IBM_KEYCLOAK_VERIFY_VALUE')
        if self._verifyVal=="False":
           self._verify_Val=False 
        else:
           self._verify_Val=True



    def _generate_token(self) -> str:

        if self._client_id is None:
            self._populate_ad_credentials()

        keycloak_openid = KeycloakOpenID(server_url=os.getenv("KEYCLOACK_URI"),
                    client_id=self._client_id,
                    realm_name=os.getenv("REALM_NAME"),
                    client_secret_key=self._client_secret,
                    verify=self._verify_Val)

        token = keycloak_openid.token(self._username, self._password)
        refresh_token = keycloak_openid.refresh_token(token['refresh_token'])
        access_token = refresh_token['access_token']
        return access_token


    @retry(stop=stop_after_attempt(RETRIES))
    def refresh_token(self) -> str:

        token = self._generate_token()
        self._access_token = token
        return self._access_token

    @property
    def access_token(self) -> str:

        return self._access_token

