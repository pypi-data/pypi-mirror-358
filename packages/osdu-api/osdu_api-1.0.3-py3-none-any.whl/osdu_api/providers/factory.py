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

"""Providers factory module."""

from typing import Any, Callable

from osdu_api.providers.types import BaseCredentials, BlobStorageClient


class ProvidersFactory:
    """The factory class for creating cloud specific clients."""

    blob_storage_registry = {} # type: dict
    credentials_registry = {} # type: dict

    @classmethod
    def register(cls, cloud_provider: str) -> Callable:
        """Class method to register BlogStorage class to the internal registry.

        :param cloud_provider: The name of the implementation to register
        :type cloud_provider: str
        :raises ValueError: If the type of registered class does not match any
            registry
        :return: The class
        :rtype: Callable
        """
        def inner_wrapper(wrapped_class: Any) -> Callable:
            if issubclass(wrapped_class, BlobStorageClient):
                cls.blob_storage_registry.setdefault(cloud_provider, wrapped_class)
            elif issubclass(wrapped_class, BaseCredentials):
                cls.credentials_registry.setdefault(cloud_provider, wrapped_class)
            else:
                raise ValueError(f"Not recognized type for this registry: {type(wrapped_class)}.")
            return wrapped_class

        return inner_wrapper

    @classmethod
    def get_blob_storage_client(cls, cloud_provider: str, *args, **kwargs) -> BlobStorageClient:
        """Get BlobStorageClient instance given a cloud provider.

        :param cloud_provider: The name of the cloud provider
        :type cloud_provider: str
        :raises NotImplementedError: When a class for this provided hasn't
            been registered yet
        :return: A cloud specific instance of BlobStorageClient
        :rtype: BlobStorageClient
        """
        if cloud_provider not in cls.blob_storage_registry:
            raise NotImplementedError(
                f"BlobStorageClient for {cloud_provider} does not exist in the registry.")

        registered_class = cls.blob_storage_registry[cloud_provider]
        return registered_class(*args, **kwargs)

    @classmethod
    def get_credentials(cls, cloud_provider: str, *args, **kwargs) -> BaseCredentials:
        """Get credentials instance given a cloud provider.

        :param cloud_provider: The name of the cloud provider
        :type cloud_provider: str
        :raises NotImplementedError: When a class for this provided hasn't
            been registered yet
        :return: A cloud especific instance of Credentials
        :rtype: BaseCredentials
        """
        if cloud_provider not in cls.credentials_registry:
            raise NotImplementedError(
                f"Credential for {cloud_provider} does not exist in the registry.")

        registered_class = cls.credentials_registry[cloud_provider]
        return registered_class(*args, **kwargs)
