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
"""Blob storage MinIO client module."""

import dataclasses
import io
import logging
import os
from dataclasses import astuple
from typing import Tuple, Optional

import boto3
import botocore
import tenacity

from osdu_api.exceptions.exceptions import MinIOConfigurationError
from osdu_api.providers.constants import BAREMETAL_PROVIDER
from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BlobStorageClient, FileLikeObject

logger = logging.getLogger(__name__)

RETRY_SETTINGS = {
    "stop": tenacity.stop_after_attempt(3),
    "wait": tenacity.wait_fixed(10),
    "reraise": True,
}

@dataclasses.dataclass(frozen=True)
class MinIOConfig:
    minio_endpoint_url: Optional[str]
    access_key_id: Optional[str]
    secret_access_key: Optional[str]


@ProvidersFactory.register(BAREMETAL_PROVIDER)
class MinIOStorageClient(BlobStorageClient):
    """Implementation of blob storage client for the MinIO provider."""

    def __init__(
        self, 
        minio_endpoint_url: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None
    ):
        """Initialize storage client. 
        
        If some arguments aren't passed directly then their values are supposed to be taken from environment variable:
        argument: minio_endpoint_url - environment variable: MINIO_ENDPOINT
        argument: access_key_id - environment variable: MINIO_ACCESS_KEY
        argument: secret_access_key - environment variable: MINIO_SECRET_KEY


        :param minio_endpoint_url: MinIO Endpoint URL, defaults to None
        :type minio_endpoint_url: Optional[str], optional
        :param access_key_id: access key id, defaults to None
        :type access_key_id: Optional[str], optional
        :param secret_access_key: secret access key, defaults to None
        :type secret_access_key: Optional[str], optional
        """
        minio_config = self._init_minio_config(
            minio_endpoint_url,
            access_key_id,
            secret_access_key
        )
        self._s3_client = boto3.client('s3', 
            endpoint_url=minio_config.minio_endpoint_url,
            aws_access_key_id=minio_config.access_key_id,
            aws_secret_access_key=minio_config.secret_access_key,
            config=boto3.session.Config(signature_version='s3v4'),
            verify=False
        )

    @staticmethod
    def _init_minio_config(
        minio_endpoint_url: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None
    ) -> MinIOConfig:

        minio_endpoint_url = minio_endpoint_url or os.getenv("MINIO_ENDPOINT")
        access_key_id = access_key_id or os.getenv("MINIO_ACCESS_KEY")
        secret_access_key = secret_access_key or os.getenv("MINIO_SECRET_KEY")

        minio_config = MinIOConfig(
            access_key_id=access_key_id, 
            secret_access_key=secret_access_key, 
            minio_endpoint_url=minio_endpoint_url
        )

        if not all(astuple(minio_config)):
            raise MinIOConfigurationError(
                "At least one argument is missing from the following ones: "
                "minio_endpoint_url, secret_access_key, access_key_id.\n"
                "Pass them directly or specify with the following environment variables: "
                "MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY"
            )

        return  minio_config

    def does_file_exist(self, uri: str) -> bool:
        """Verify if a file exists in the given URI.

        :param uri: The AWS URI of the file.
        :type uri: str
        :return: A boolean indicating if the file exists
        :rtype: bool
        """

        bucket_name, object_name = self._split_s3_path(uri)
        try:
            self._s3_client.head_object(Bucket=bucket_name, Key=object_name)
        except botocore.exceptions.ClientError as err:
            # The error is too general if the file is absent, so we need to check the error's message
            if not "Not Found" in str(err):
                raise err
            
            return False
        return True

    def download_to_file(self, uri: str, file: FileLikeObject) -> Tuple[FileLikeObject, str]:
        """Download file from the given URI.

        :param uri: The AWS URI of the file.
        :type uri: str
        :param file: The file where to download the blob content
        :type file: FileLikeObject
        :return: A tuple containing the file and its content-type
        :rtype: Tuple[io.BytesIO, str]
        """
        bucket_name, object_name = self._split_s3_path(uri)
        content_type = ""
        self._s3_client.download_fileobj(bucket_name, object_name, file)

        return file, content_type

    def download_file_as_bytes(self, uri: str) -> Tuple[bytes, str]:
        """Download file as bytes from the given URI.

        :param uri: The AWS URI of the file
        :type uri: str
        :return: The file as bytes and its content-type
        :rtype: Tuple[bytes, str]
        """
        bucket_name, object_name = self._split_s3_path(uri)
        filename = object_name.split('/')[-1]
        file_handle = io.BytesIO
        return self._s3_client.download_fileobj(bucket_name, object_name, file_handle)

    def upload_file(
        self, 
        uri: str, 
        blob_file: FileLikeObject, 
        content_type: str = "application/octet-stream"
    ):
        """Upload a file to the given uri.

        :param uri: S# URI of the file
        :type uri: str
        :param blob: The file
        :type blob: FileLikeObject
        :param content_type: [description]
        :type content_type: str
        """
        bucket_name, object_name = self._split_s3_path(uri)
        self._s3_client.upload_fileobj(
            blob_file, 
            bucket_name, 
            object_name, 
            ExtraArgs = {"ContentType": content_type}
        )
        
    @staticmethod
    def _split_s3_path(s3_path: str) -> Tuple[str, str]:
        """Splits S3 path into bucket and object name

        :param s3_path: s3 URI starting with 
        :type s3_path: str
        :return: bucket and ovject key_name
        :rtype: Tuple[str, str]
        """
        path_parts = s3_path.replace("s3://", "").split("/")
        bucket = path_parts.pop(0)
        key = "/".join(path_parts)
        return bucket, key
