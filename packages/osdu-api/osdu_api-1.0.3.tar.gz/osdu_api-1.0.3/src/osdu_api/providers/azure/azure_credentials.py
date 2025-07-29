#  Copyright © Microsoft Corporation
#  Copyright 2021 EPAM Systems
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
"""Azure Credential Module."""

import logging

from azure.identity import DefaultAzureCredential, ClientSecretCredential, ManagedIdentityCredential, CertificateCredential
from azure.keyvault import secrets
from tenacity import retry, stop_after_attempt

from osdu_api.providers.constants import AZURE_CLOUD_PROVIDER
from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BaseCredentials
from osdu_api.utils.env import getenv_by_names, getenv
from osdu_api.providers.azure.azure_auth_enums import AzureAuthType, ClientSecretFetchType

logger = logging.getLogger(__name__)
RETRIES = 3


@ProvidersFactory.register(AZURE_CLOUD_PROVIDER)
class AzureCredentials(BaseCredentials):
    """Azure Credential Provider"""

    def __init__(self, auth_type=None, auth_properties=None):
        """Initialize Azure Credentials object"""
        logger.info(f"Initializing Azure credentials object with auth_type: {auth_type} and auth_properties: {auth_properties}")
        self._access_token = None
        self._client_id = None
        self._client_secret = None
        self._tenant_id = None
        self._resource_id = None
        self._credential_provider = None
        self._auth_type = auth_type
        self._auth_properties = auth_properties
        self._resolve_auth_type_if_none()
        self._resolve_auth_properties_if_none()
        self._set_auth_fields()
        logger.info(f"Auth type: {self._auth_type}")

    def _resolve_auth_type_if_none(self):
        logger.info("No auth type was provided. Resolving auth type...")
        if self._auth_type is None:
            if self._check_msi_enabled_in_env():
                self._auth_type = AzureAuthType.MSI
            else:
                self._auth_type = AzureAuthType.CLIENT_SECRET

    def _check_msi_enabled_in_env(self):
        env_value = getenv_by_names([
            "AZURE_ENABLE_MSI",
            "AIRFLOW_VAR_AZURE_ENABLE_MSI",
        ])
        if env_value:
            return env_value == "true"
        else:
            return None

    def _resolve_auth_properties_if_none(self):
        logger.info("No auth properties passed. Resolving auth properties..")
        if self._auth_properties is None:
            if self._auth_type == AzureAuthType.CLIENT_SECRET:
                keyvault_uri = getenv_by_names(["KEYVAULT_URI", "AZURE_KEYVAULT_URI",
                                                "AIRFLOW_VAR_KEYVAULT_URI"])
                use_aad_env_vars = getenv_by_names([
                    "AIRFLOW_VAR_ENV_VARS_ENABLED",
                    "ENV_VARS_ENABLED",
                ])
                if keyvault_uri and not use_aad_env_vars:
                    logger.info("Client secret fetch type set to Keyvault")
                    self._auth_properties = {
                        "fetch_type":  ClientSecretFetchType.KEYVAULT,
                        "config": {
                            "keyvault_uri": keyvault_uri,
                            "client_id_key": "app-dev-sp-username",
                            "client_secret_key": "app-dev-sp-password",
                            "tenant_id_key": "app-dev-sp-tenant-id",
                            "resource_id_key": "aad-client-id"
                        }
                    }
                else:
                    logger.info("Client secret fetch type set to Plain Text")
                    self._auth_properties = {
                        "fetch_type": ClientSecretFetchType.PLAIN_TEXT,
                        "config": {
                            "client_id": getenv_by_names(["AIRFLOW_VAR_AZURE_CLIENT_ID",
                                                          "AZURE_CLIENT_ID", "AZURE_PRINCIPAL_ID"]),
                            "client_secret": getenv_by_names(["AIRFLOW_VAR_AZURE_CLIENT_SECRET",
                                                              "AZURE_CLIENT_SECRET",
                                                              "AZURE_PRINCIPAL_SECRET"]),
                            "tenant_id": getenv_by_names(["AIRFLOW_VAR_AZURE_TENANT_ID",
                                                          "AZURE_TENANT_ID", "AZURE_AD_TENANT_ID"]),
                            "resource_id": getenv_by_names(["AIRFLOW_VAR_AAD_CLIENT_ID",
                                                            "AZURE_RESOURCE_ID", "AZURE_APP_ID",
                                                            "AZURE_AD_APP_RESOURCE_ID"])
                        }
                    }

    def _set_auth_fields(self):
        if self._auth_type == AzureAuthType.CLIENT_SECRET:
            if self._auth_properties["fetch_type"] == ClientSecretFetchType.PLAIN_TEXT:
                self._set_auth_fields_via_plain_text()
            elif self._auth_properties["fetch_type"] == ClientSecretFetchType.ENVIRONMENT_VARIABLE:
                self._set_auth_fields_via_env()
            elif self._auth_properties["fetch_type"] == ClientSecretFetchType.KEYVAULT:
                self._set_auth_fields_via_keyvault()
            else:
                raise ValueError("Unsupported Client Secret fetch type")
            self._validation_for_client_secret_auth_type()

    def _set_auth_fields_via_plain_text(self):
        self._client_id = self._auth_properties["config"]["client_id"]
        self._client_secret = self._auth_properties["config"]["client_secret"]
        self._tenant_id = self._auth_properties["config"]["tenant_id"]
        self._resource_id = self._auth_properties["config"]["resource_id"]

    def _set_auth_fields_via_env(self):
        self._client_id = getenv(self._auth_properties["config"]["client_id_key"])
        self._client_secret = getenv(self._auth_properties["config"]["client_secret_key"])
        self._tenant_id = getenv(self._auth_properties["config"]["tenant_id_key"])
        self._resource_id = getenv(self._auth_properties["config"]["resource_id_key"])

    def _set_auth_fields_via_keyvault(self):
        if "keyvault_uri" not in self._auth_properties["config"]:
            pass
        keyvault_client = secrets.SecretClient(
            vault_url=self._auth_properties["config"]["keyvault_uri"],
            credential=DefaultAzureCredential())
        self._client_id = keyvault_client.get_secret(
            self._auth_properties["config"]["client_id_key"]).value
        self._client_secret = keyvault_client.get_secret(
            self._auth_properties["config"]["client_secret_key"]).value
        self._tenant_id = keyvault_client.get_secret(
            self._auth_properties["config"]["tenant_id_key"]).value
        self._resource_id = keyvault_client.get_secret(
            self._auth_properties["config"]["resource_id_key"]).value

    def _validation_for_client_secret_auth_type(self):
        if self._client_id is None:
            logger.error('ClientId is not set properly')
            raise ValueError("ClientId is not set properly")
        if self._tenant_id is None:
            logger.error('TenantId is not set properly')
            raise ValueError("TenantId is not set properly")
        if self._resource_id is None:
            logger.error('ResourceId is not set properly')
            raise ValueError("ResourceId is not set properly")
        if self._client_id is None:
            logger.error('Please pass client Id to generate token')
            raise ValueError("Please pass client Id to generate token")
        if self._client_secret is None:
            logger.error('Please pass client secret to generate token')
            raise ValueError("Please pass client secret to generate token")

    @retry(stop=stop_after_attempt(RETRIES))
    def refresh_token(self) -> str:
        """Refresh token.

        :return: Refreshed token
        :rtype: str
        """
        logger.info("Refreshing token...")
        token = self._generate_token()
        self._access_token = token
        return self._access_token

    def _generate_token(self) -> str:
        logger.info("Generating new token")
        if self._auth_type == AzureAuthType.MSI:
            return self._generate_token_using_msi()
        elif self._auth_type == AzureAuthType.CLIENT_SECRET:
            return self._generate_token_using_client_secret()
        elif self._auth_type == AzureAuthType.CLIENT_CERTIFICATE:
            pass
        else:
            raise ValueError("Given auth type not supported")

    def _generate_token_using_msi(self) -> str:
        logger.info("Using MSI Token generation")
        if self._credential_provider is None:
            self._credential_provider = ManagedIdentityCredential()
        return self._credential_provider.get_token("https://management.azure.com/").token

    def _generate_token_using_client_secret(self) -> str:
        logger.info("Using Client Secret Token generation")
        if self._credential_provider is None:
            self._credential_provider = ClientSecretCredential(tenant_id=self._tenant_id,
                                                               client_id=self._client_id,
                                                               client_secret=self._client_secret)

        return self._credential_provider.get_token(self._resource_id + '/.default').token

    @property
    def access_token(self) -> str:
        """The access token.

        :return: Access token string.
        :rtype: str
        """
        return self._access_token

