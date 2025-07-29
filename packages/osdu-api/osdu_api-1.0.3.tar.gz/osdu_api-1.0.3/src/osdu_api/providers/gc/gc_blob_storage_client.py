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
"""Blob storage Google Cloud client module."""

import io
import logging
from typing import Tuple
from urllib.parse import urlparse

import google.auth
import tenacity
from google.cloud import storage

from osdu_api.providers.constants import GOOGLE_CLOUD_PROVIDER
from osdu_api.providers.exceptions import GCSObjectURIError
from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BlobStorageClient, FileLikeObject

logger = logging.getLogger(__name__)

RETRY_SETTINGS = {
    "stop": tenacity.stop_after_attempt(3),
    "wait": tenacity.wait_fixed(10),
    "reraise": True,
}


@ProvidersFactory.register(GOOGLE_CLOUD_PROVIDER)
class GoogleCloudStorageClient(BlobStorageClient):
    """Implementation of blob storage client for the Google provider."""

    def __init__(self):
        """Initialize storage client."""
        self._storage_client = storage.Client()

    @staticmethod
    def _parse_gcs_uri(gcs_uri: str) -> Tuple[str, str]:
        """Parse gcs compliant uri and return bucket_name and blob_name.

        :param gcs_uri: A GCS compliant URI.
        :type gcs_uri: str
        :raises GCSObjectURIError: When non GCS compliant URI is provided
        :return: A tuple (bucket_name, blob_name) obtained from the URI
        :rtype: Tuple[str, str]
        """
        parsed_path = urlparse(gcs_uri)
        if parsed_path.scheme == "gs":
            bucket_name = parsed_path.netloc
            source_blob_name = parsed_path.path[1:]  # delete the first slash

            if bucket_name and source_blob_name:
                return bucket_name, source_blob_name

        raise GCSObjectURIError(f"Wrong format path to GCS object. Object path is '{gcs_uri}'")

    @tenacity.retry(**RETRY_SETTINGS)
    def _get_file_from_bucket(self,
                             bucket_name: str,
                             source_blob_name: str,
                             file: FileLikeObject) -> Tuple[io.BytesIO, str]:
        """Get file from gcs bucket.

        :param bucket_name: The name of the bucket that holds the file
        :type bucket_name: str
        :param source_blob_name: The name of the file
        :type source_blob_name: str
        :param file: The file where to download the blob content
        :type file: FileLikeObject
        :return: A tuple containing file and its content-type
        :rtype: Tuple[io.BytesIO, str]
        """
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.get_blob(source_blob_name)

        blob.download_to_file(file)
        logger.debug(f"File {source_blob_name} got from bucket {bucket_name}.")

        return file, blob.content_type

    @tenacity.retry(**RETRY_SETTINGS)
    def _get_file_as_bytes_from_bucket(self,
                                       bucket_name: str,
                                       source_blob_name: str) -> Tuple[bytes, str]:
        """Get file as bytes from gcs bucket.

        :param bucket_name: The name of the bucket that holds the file
        :type bucket_name: str
        :param source_blob_name: The name of the file
        :type source_blob_name: str
        :return: A tuple containing file and its content-type
        :rtype: Tuple[bytes, str]
        """
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.get_blob(source_blob_name)

        file_as_bytes = blob.download_as_bytes()
        logger.debug(f"File {source_blob_name} got from bucket {bucket_name}.")

        return file_as_bytes, blob.content_type

    @tenacity.retry(**RETRY_SETTINGS)
    def _does_file_exist_in_bucket(self, bucket_name: str, source_blob_name: str) -> bool:
        """Use gcs client and verify a file exists in given bucket.

        :param bucket_name: The name of the bucket that holds the resoie
        :type bucket_name: str
        :param source_blob_name: The name of the file
        :type source_blob_name: str
        :return: A boolean indicating if the file exists
        :rtype: bool
        """
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(source_blob_name)
        return blob.exists()

    def does_file_exist(self, uri: str) -> bool:
        """Verify if a file exists in the given URI.

        :param uri: The GCS URI of the file.
        :type uri: str
        :return: A boolean indicating if the file exists
        :rtype: bool
        """
        bucket_name, source_blob_name = self._parse_gcs_uri(uri)
        try:
            return self._does_file_exist_in_bucket(bucket_name, source_blob_name)
        except google.auth.exceptions.DefaultCredentialsError:
            # TODO(python-team) Figure out a way to mock google endpoints in integration tests.
            logger.error("No default credentials found in env, is this integration-env?")

    def download_to_file(self, uri: str, file: FileLikeObject) -> Tuple[FileLikeObject, str]:
        """Download file from the given URI.

        :param uri: The GCS URI of the file.
        :type uri: str
        :param file: The file where to download the blob content
        :type file: FileLikeObject
        :return: A tuple containing the file and its content-type
        :rtype: Tuple[io.BytesIO, str]
        """
        bucket_name, blob_name = self._parse_gcs_uri(uri)
        return self._get_file_from_bucket(bucket_name, blob_name, file)

    def download_file_as_bytes(self, uri: str) -> Tuple[bytes, str]:
        """Download file as bytes from the given URI.

        :param uri: The GCS URI of the file
        :type uri: str
        :return: The file as bytes and its content-type
        :rtype: Tuple[bytes, str]
        """
        bucket_name, blob_name = self._parse_gcs_uri(uri)
        return self._get_file_as_bytes_from_bucket(bucket_name, blob_name)

    def upload_file(self, uri: str, blob_file: FileLikeObject, content_type: str):
        """Upload a file to the given uri.

        :param uri: The GCS URI of the file
        :type uri: str
        :param blob: The file
        :type blob: FileLikeObject
        :param content_type: [description]
        :type content_type: str
        """
        bucket_name, blob_name = self._parse_gcs_uri(uri)
        bucket = self._storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_file(blob_file, content_type=content_type)
        logger.debug(f"Uploaded file to {uri}.")
