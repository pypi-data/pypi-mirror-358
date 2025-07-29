#  Copyright 2021 Google LLC
#  Copyright 2021 EPAM Systems
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
"""Google Cloud Credentials module."""

import json
import logging
import os
from typing import Tuple
from urllib.parse import urlparse

import google
import google.auth
from google.auth.transport.requests import Request
from google.cloud import storage
from google.oauth2 import id_token as google_id_token, service_account
from tenacity import retry, stop_after_attempt

from osdu_api.providers.constants import GOOGLE_CLOUD_PROVIDER
from osdu_api.providers.exceptions import RefreshSATokenError, SAFilePathError, RefreshDefaultCredentialsTokenError
from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BaseCredentials

logger = logging.getLogger(__name__)

RETRIES = 3


@ProvidersFactory.register(GOOGLE_CLOUD_PROVIDER)
class GCCredentials(BaseCredentials):
    """Google Cloud Credentials Provider."""

    DEFAULT_ACCESS_SCOPES = ["openid", "email", "profile"]

    def __init__(self, access_scopes: list = None, sa_file_path: str = None):
        """Initialize Google Cloud Credentials object.
           If SA file is not provided, this object attempts to use default credentials

        :param access_scopes: Optional scopes, defaults to None
        :type access_scopes: list, optional
        :param sa_file_path: Path/URL to Service Account file
        :type sa_file_path: str, optional
        """
        self._access_token = None
        self._id_token = None
        self._is_id_token_auth = os.getenv("GC_ID_TOKEN", "").lower() in ("on", "y", "true", "yes")
        self._access_scopes = access_scopes
        self._sa_file_path = sa_file_path or os.environ.get("SA_FILE_PATH", None)

    @property
    def access_scopes(self) -> list:
        """
        Return access scopes.
        Use DEFAULT_ACCESS_SCOPES if user-defined ones weren't provided.
        """
        if not self._access_scopes:
            self._access_scopes = self.DEFAULT_ACCESS_SCOPES
        return self._access_scopes

    @retry(stop=stop_after_attempt(RETRIES))
    def _get_sa_info_from_google_storage(self, bucket_name: str, source_blob_name: str) -> dict:
        """Get sa_file content from Google Storage.

        :param bucket_name: The name of the bucket
        :type bucket_name: str
        :param source_blob_name: The name of the file
        :type source_blob_name: str
        :return: Service account info as dict
        :rtype: dict
        """
        storage_client = storage.Client()
        bucket = storage_client .bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        logger.info("Got SA_file.")
        sa_info = json.loads(blob.download_as_bytes())
        return sa_info

    @staticmethod
    def _get_sa_info_from_file(path: str) -> dict:
        """Return infor from file.

        :param path: The path of the file.
        :type path: str
        :return: Loaded file as dict
        :rtype: dict
        """
        with open(path) as f:
            return json.load(f)

    def _get_sa_info(self) -> dict:
        """Get file path from SA_FILE_PATH environmental variable.
        This path can be GCS object URI or local file path.
        Return content of sa path as dict.

        :raises SAFilePathError: When an error occurs with file path
        :return: Service account info
        :rtype: dict
        """
        parsed_path = urlparse(self._sa_file_path)
        if parsed_path.scheme == "gs":
            bucket_name = parsed_path.netloc
            source_blob_name = parsed_path.path[1:]  # delete the first slash
            sa_info = self._get_sa_info_from_google_storage(bucket_name, source_blob_name)
        elif not parsed_path.scheme and os.path.isfile(parsed_path.path):
            sa_info = self._get_sa_info_from_file(parsed_path.path)
        else:
            logger.error("SA file path error.")
            raise SAFilePathError(f"Got path {os.environ.get('SA_FILE_PATH', None)}")
        return sa_info

    @retry(stop=stop_after_attempt(RETRIES))
    def _get_credentials_from_sa_info(self, sa_info: dict) -> service_account.Credentials:
        """Build and get a credentials object using service account info.

        :param sa_info: Json loaded service account info
        :type sa_info: dict
        :raises e: If loaded file has bad format
        :return: Google credentials object obtained from service account
        :rtype: service_account.Credentials
        """
        try:
            credentials = service_account.Credentials.from_service_account_info(
                sa_info, scopes=self.access_scopes)
        except ValueError as e:
            logger.error("SA file has bad format.")
            raise e
        return credentials

    def _get_default_tokens(self) -> Tuple[str, str]:
        """Get token using default credentials from the environment

        :raises RefreshDefaultCredentialsTokenError: Error of getting default credentials
        :return: auth token
        :rtype: str
        """
        if self._sa_file_path:
            credentials = self._get_credentials_from_sa_info(self._get_sa_info())
        else:
            credentials, _  = google.auth.default(scopes=self.access_scopes)

        credentials.refresh(Request())
        token = credentials.token

        if hasattr(credentials, "id_token"):
            id_token = credentials.id_token
        else:
            id_token = google_id_token.fetch_id_token(Request(), audience="https://www.googleapis.com/oauth2/v4/token")

        if not all((token, id_token)):
            logger.error("Can't refresh token using default credentials from the environment")
            raise RefreshDefaultCredentialsTokenError
        
        return token, id_token

    @retry(stop=stop_after_attempt(RETRIES))
    def refresh_token(self) -> str:
        """Refresh token.

        :return: Refreshed token
        :rtype: str
        """
        token, id_token = self._get_default_tokens()
        self._access_token = token
        self._id_token = id_token
        return self._access_token

    @property
    def access_token(self) -> str:
        """If 'GC_ID_TOKEN' env variable is True, it returns id_token instead of the access

        :return: Access token string.
        :rtype: str
        """
        if not self._is_id_token_auth:
            return self._access_token
        else:
            return self._id_token
