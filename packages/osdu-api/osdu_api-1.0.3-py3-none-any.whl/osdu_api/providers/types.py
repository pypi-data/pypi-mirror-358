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
"""Types module."""

import abc
import io
from typing import Tuple, TypeVar

FileLikeObject = TypeVar("FileLikeObject", io.IOBase, io.RawIOBase, io.BytesIO)


class BlobStorageClient(abc.ABC):
    """Base interface for storage clients."""

    @abc.abstractmethod
    def download_to_file(self, uri: str, file: FileLikeObject) -> Tuple[FileLikeObject, str]:
        """Download file from the given URI.

        :param uri: The full URI of the file.
        :type uri: str
        :param file: The file where to download the blob content
        :type file: FileLikeObject
        :return: A tuple containing the file and its content-type
        :rtype: Tuple[FileLikeObject, str]
        """
        pass

    @abc.abstractmethod
    def download_file_as_bytes(self, uri: str) -> Tuple[bytes, str]:
        """Download file as bytes from the given URI.

        :param uri: The full URI of the file
        :type uri: str
        :return: The file as bytes and its content-type
        :rtype: Tuple[bytes, str]
        """
        pass

    @abc.abstractmethod
    def upload_file(self, uri: str, file: FileLikeObject, content_type: str):
        """Upload blob to given URI.

        :param uri: The full target URI of the resource to upload.
        :type uri: str
        :param file: The file to upload
        :type file: FileLikeObject
        :param content_type: The content-type of the file to uplaod
        :type content_type: str
        """
        pass

    @abc.abstractmethod
    def does_file_exist(self, uri: str) -> bool:
        """Verify if a file resource exists in the given URI.

        :param uri: The URI of the resource to verify
        :type uri: str
        :return: True if exists, False otherwise
        :rtype: bool
        """
        pass


class BaseCredentials(abc.ABC):
    """Base interface for credentials."""

    @abc.abstractmethod
    def refresh_token(self) -> str:
        """Refresh auth token.

        :return: refreshed token
        :rtype: str
        """
        pass

    @property
    @abc.abstractmethod
    def access_token(self) -> str:
        """Auth access token.

        :return: token string
        :rtype: str
        """
        pass
