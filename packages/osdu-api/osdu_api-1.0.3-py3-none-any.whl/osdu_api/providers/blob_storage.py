#  Copyright 2021 Google LLC
#  Copyright 2021 EPAM Systems
#  Copyright © Microsoft Corporation
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
"""Blob storage init module."""
import importlib
import logging
import os

from typing import Optional

from osdu_api.providers.factory import ProvidersFactory
from osdu_api.providers.types import BlobStorageClient


logger = logging.getLogger()


def _import_provider_specific_storage_client_module(provider: str) -> str:
    """
    Import provider specific blob storage client module for correct registering it
    """
    module_name = f"osdu_api.providers.{provider.lower()}.{provider.lower()}_blob_storage_client"
    importlib.import_module(module_name)
    return module_name


def get_client(
    cloud_env: Optional[str] = None, 
    *args, 
    **kwargs
) -> BlobStorageClient:
    """Get specific blob storage client according to cloud environment.

    :param cloud_env: Name of the provided cloud env, if not given,
        `CLOUD_PROVIDER` env var should be set.
    :type cloud_env: str, optional
    :return: An instance of BlobStorageClient
    :rtype: BlobStorageClient
    """
    cloud_env = cloud_env or os.environ.get("CLOUD_PROVIDER")
    # import section needed to register cloud specific clients
    try:
        _import_provider_specific_storage_client_module(cloud_env)
    except ModuleNotFoundError as exc:
        logger.critical(f"Error occurred while importing blob storage client module for {cloud_env}")
        logger.critical(f"Exception: {exc}")
    return ProvidersFactory.get_blob_storage_client(cloud_env, *args, **kwargs)
