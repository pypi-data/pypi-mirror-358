#  Copyright © Microsoft Corporation
#  Copyright 2022 Google LLC
#  Copyright 2022 EPAM Systems
#
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
"""Utils for request managment library."""

import logging
from http import HTTPStatus
from typing import Callable

import requests

logger = logging.getLogger()

def request_raiser(request_function: Callable) -> Callable:
    """
    Wrap a request function and check response. If response is not ok 
    then raises HTTPError
    request_function(*args, **kwargs) -> requests.Response
    """

    def _wrapper(*args, **kwargs) -> requests.Response:
        response = request_function(*args, **kwargs)

        if not response.ok:
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                logger.error(f"{response.text}")
                raise e

        return response

    return _wrapper

def response_not_ok(response: requests.Response):
    """Callback to retry OSDU requests if they are not OK, UNAUTHORIZED or FORBIDDEN.

    :param value: response from OSDU API
    :type value: requests.Response
    """
    if  response.status_code not in (
        HTTPStatus.OK,
        HTTPStatus.CREATED,
        HTTPStatus.ACCEPTED,
        HTTPStatus.NO_CONTENT,
        HTTPStatus.FORBIDDEN,
        HTTPStatus.UNAUTHORIZED
    ):
        return True
    else:
        return False
