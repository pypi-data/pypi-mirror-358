
"""Blob storage AWS client module"""

import tenacity
from osdu_api.providers.constants import AWS_CLOUD_PROVIDER
import logging
import boto3
from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BlobStorageClient, FileLikeObject
from typing import Tuple
import io

logger = logging.getLogger(__name__)

RETRY_SETTINGS = {
    "stop": tenacity.stop_after_attempt(3),
    "wait": tenacity.wait_fixed(10),
    "reraise": True,
}

@ProvidersFactory.register(AWS_CLOUD_PROVIDER)
class AwsCloudStorageClient(BlobStorageClient):
    """Implementation of blob storage client for the AWS provider."""
    def __init__(self):
        """Initialize storage client."""
        session = boto3.session.Session()
        self.s3_client =session.client('s3', region_name="us-east-1")

    def does_file_exist(self, uri: str) -> bool:
        """Verify if a file exists in the given URI.

        :param uri: The AWS URI of the file.
        :type uri: str
        :return: A boolean indicating if the file exists
        :rtype: bool
        """

        # assuming the URI here is an s3:// URI
        # get the bucket name and path to object
        bucket_name, object_name = self._split_s3_path(uri)
        try:
            # try to get the s3 metadata for the object, which is a 
            # fast operation no matter the size of the data object
            self.s3_client.head_object(bucket_name, object_name)
        except:
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
        # assuming the URI here is an s3:// URI
        # get the bucket name, path to object
        bucket_name, object_name = self._split_s3_path(uri)
        buffer = io.BytesIO()
        content_type = ""
        file_bytes = self.s3_client.download_fileobj(bucket_name, object_name, buffer)

        return file_bytes, content_type


    def download_file_as_bytes(self, uri: str) -> Tuple[bytes, str]:
        """Download file as bytes from the given URI.

        :param uri: The AWS URI of the file
        :type uri: str
        :return: The file as bytes and its content-type
        :rtype: Tuple[bytes, str]
        """
        # assuming the URI here is an s3:// URI
        # get the bucket name, path to object
        bucket_name, object_name = self._split_s3_path(uri)
        filename = object_name.split('/')[-1]
        file_handle = io.BytesIO
        return self.s3_client.download_fileobj(bucket_name, object_name, file_handle)

    def upload_file(self, uri: str, blob_file: FileLikeObject, content_type: str):
        """Upload a file to the given uri.

        :param uri: The AWS URI of the file
        :type uri: str
        :param blob: The file
        :type blob: FileLikeObject
        :param content_type: [description]
        :type content_type: str
        """
        # assuming the URI here is an s3:// URI
        # get the bucket name, path to object
        bucket_name, object_name = self._split_s3_path(uri)

        # Upload the file like object
        self.s3_client.upload_fileobj(blob_file, bucket_name, object_name)
        
    def _split_s3_path(self, s3_path:str):
        """split a s3:// path into bucket and key parts

        Args:
            s3_path (str): an s3:// uri

        Returns:
            tuple: bucket name, key name ( with path )
        """
        path_parts=s3_path.replace("s3://","").split("/")
        bucket=path_parts.pop(0)
        key="/".join(path_parts)
        return bucket, key
