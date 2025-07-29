#  Copyright © Microsoft Corporation
#  Copyright 2023 EPAM Systems
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
"""Blob storage Azure client module"""

import tenacity
from osdu_api.providers.constants import AZURE_CLOUD_PROVIDER
import logging
from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BlobStorageClient, FileLikeObject
from typing import Tuple
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)

RETRY_SETTINGS = {
    "stop": tenacity.stop_after_attempt(3),
    "wait": tenacity.wait_fixed(10),
    "reraise": True,
}

@ProvidersFactory.register(AZURE_CLOUD_PROVIDER)
class AzureCloudStorageClient(BlobStorageClient):
    """Implementation of blob storage client for the Azure provider."""
    def __init__(self):
        """Initialize storage client."""
        credential = DefaultAzureCredential()
        self.credential = credential

    def does_file_exist(self, uri: str) -> bool:
        """Verify if a file exists in the given URI.
        :param uri: The GCS URI of the file.
        :type uri: str
        :return: A boolean indicating if the file exists
        :rtype: bool
        """
        account_name, container_name, blob_name = self._get_container_and_blob_names_from_uri(uri)
        account_url = f"https://{account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=self.credential)
        try:
            blob_service_client.get_blob_client(container=container_name,
                                                blob=blob_name).get_blob_properties()
            return True
        except Exception as e:
            print(f"An error occurred while checking if the file exists: {str(e)}")
            return False

    def _get_container_and_blob_names_from_uri(self, uri: str) -> Tuple[str, str, str]:
        """Extract container and blob names from the given URI.

        :param uri: The Azure Blob Storage URI of the file.
        :type uri: str
        :return: A tuple containing the account name, container name, and the blob name
        :rtype: Tuple[str, str, str]
        """
        uri_parts = uri.split('/', 3)
        if len(uri_parts) != 4:
            raise ValueError(f"Invalid Azure Blob Storage URI: {uri}")
        account_name, container_name, blob_path = uri_parts[2], uri_parts[3].split('/', 1)[0], \
                                                  uri_parts[3].split('/', 1)[-1]
        blob_name = f"{blob_path}"
        container_name = f"{container_name}".lower()
        return account_name, container_name, blob_name

    def download_to_file(self, uri: str, file: FileLikeObject) -> Tuple[FileLikeObject, str]:
        """Download file from the given URI.
            :param uri: The Azure Blob Storage URI of the file.
            :type uri: str
            :param file: The file where to download the blob content
            :type file: FileLikeObject
            :return: A tuple containing the file and its content-type
            :rtype: Tuple[io.BytesIO, str]
            """
        account_name, container_name, blob_name = self._get_container_and_blob_names_from_uri(uri)
        account_url = f"https://{account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=self.credential)
        blob_client = blob_service_client.get_blob_client(container=container_name,
                                                          blob=blob_name)
        download_stream = blob_client.download_blob()
        file.write(download_stream.readall())
        content_type = download_stream.properties.content_settings.content_type
        return file, content_type

    def download_file_as_bytes(self, uri: str) -> Tuple[bytes, str]:
        """Download file as bytes from the given URI.
        :param uri: The GCS URI of the file
        :type uri: str
        :return: The file as bytes and its content-type
        :rtype: Tuple[bytes, str]
        """
        account_name, container_name, blob_name = self._get_container_and_blob_names_from_uri(uri)
        account_url = f"https://{account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=self.credential)
        blob_client = blob_service_client.get_blob_client(container=container_name,
                                                          blob=blob_name)
        download_stream = blob_client.download_blob()
        return (download_stream.readall(), container_name)

    def upload_file(self, uri: str, blob_file: FileLikeObject, content_type: str):
        """Upload a file to the given uri.
        :param uri: The GCS URI of the file
        :type uri: str
        :param blob: The file
        :type blob: FileLikeObject
        :param content_type: [description]
        :type content_type: str
        """
        account_name, container_name, blob_name = self._get_container_and_blob_names_from_uri(uri)
        account_url = f"https://{account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=self.credential)
        try:
            blob_client = blob_service_client.get_blob_client(container=container_name,
                                                              blob=blob_name)
            blob_client.upload_blob(blob_file, blob_type="BlockBlob",
                                    content_settings=ContentSettings(content_type=content_type,
                                                                     cache_control=''))
            logger.debug(f"Uploaded file to {uri}. The Url is {blob_client.url}")
        except Exception as e:
            print("Failed to upload files to container. Error:" + str(e))
