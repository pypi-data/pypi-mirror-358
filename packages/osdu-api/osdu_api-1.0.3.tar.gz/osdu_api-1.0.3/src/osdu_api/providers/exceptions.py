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

"""Providers exceptions module."""


class RefreshSATokenError(Exception):
    """Raise when token is empty after attempt to get credentials from service account file."""
    pass


class RefreshDefaultCredentialsTokenError(Exception):
    """Raise when token is empty after attempt to get credentials from service account file."""


class SAFilePathError(Exception):
    """Raise when sa_file path is not specified in Env Variables."""
    pass


class GCSObjectURIError(Exception):
    """Raise when wrong Google Storage Object URI was given."""
    pass
