
"""AWS Credential Module."""

import logging
from osdu_api.providers.constants import AWS_CLOUD_PROVIDER
from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BaseCredentials
from osdu_api.providers.aws.service_principal_util import get_service_principal_token
from tenacity import retry, stop_after_attempt
import os

logger = logging.getLogger(__name__)
RETRIES = 3

@ProvidersFactory.register(AWS_CLOUD_PROVIDER)
class AWSCredentials(BaseCredentials):
    """AWS Credential Provider"""

    def __init__(self):
        """Initialize AWS Credentials object"""
        self._access_token = None

    @retry(stop=stop_after_attempt(RETRIES))
    def refresh_token(self) -> str:
        """Refresh token.

        :return: Refreshed token
        :rtype: str
        """
        token = get_service_principal_token()
        self._access_token = token
        return self._access_token

    @property
    def access_token(self) -> str:
        """The access token.

        :return: Access token string.
        :rtype: str
        """
        return self._access_token

