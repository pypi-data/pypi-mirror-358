#  Copyright 2020 Google LLC
#  Copyright 2020 EPAM Systems
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

import logging
from abc import ABC, abstractmethod
from functools import partial
from http import HTTPStatus
from typing import Any, Callable, Optional, Union

import requests

from osdu_api.exceptions.exceptions import TokenRefresherNotPresentError

logger = logging.getLogger()


class TokenRefresher(ABC):

    def __init__(self):
        self._access_token = ""

    @abstractmethod
    def refresh_token(self) -> str:
        """
        Implement logics of refreshing token here.
        """
        pass

    def authorize(self):
        self._access_token = self.refresh_token()

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def authorization_header(self) -> dict:
        """
        Must return  authorization header for updating headers dict.
        E.g. return {"Authorization": "Bearer <access_token>"}
        """
        return {"Authorization": f"Bearer {self.access_token}"}


def make_callable_request(obj: Union[object, None], request_function: Callable, headers: dict,
                          *args, **kwargs) -> Callable:
    """
    Create send_request_with_auth function.
    """
    if obj:  # if wrapped function is an object's method
        callable_request = partial(
            request_function, obj, headers, *args, **kwargs)
    else:
        callable_request = partial(request_function, headers, *args, **kwargs)
    return callable_request


def _validate_headers_type(headers: Any):
    if not isinstance(headers, dict):
        logger.error(f"Got headers {headers}")
        raise TypeError(
            f"Request's headers type expected to be 'dict'. Got {dict}")


def _validate_response_type(response: requests.Response, request_function: Callable):
    if not isinstance(response, requests.Response):
        logger.error(f"Function or method {request_function}"
                     f" must return values of type 'requests.Response'. "
                     f"Got {type(response)} instead")
        raise TypeError


def _validate_token_refresher_type(token_refresher: TokenRefresher):
    if not isinstance(token_refresher, TokenRefresher):
        raise TypeError(
            f"Token refresher must be of type {TokenRefresher}. Got {type(token_refresher)}"
        )


def _get_object_token_refresher(
        obj: object
) -> TokenRefresher:
    """
    Check if token refresher passed into decorator or specified in object's as 'token_refresher'
    property.
    """
    try:
        obj.__getattribute__("token_refresher")
    except AttributeError:
        raise TokenRefresherNotPresentError("Token refresher must be passed into decorator or "
                                            "set as object's 'refresh_token' attribute.")
    else:
        token_refresher = obj.token_refresher # type: ignore
        return token_refresher


def send_request_with_auth_header(token_refresher: TokenRefresher, *args,
                                  **kwargs) -> requests.Response:
    """
    Send request with authorization token. If response status is in HTTPStatus.UNAUTHORIZED or
    HTTPStatus.FORBIDDEN, then refresh token and send request once again.
    """
    obj = kwargs.pop("obj", None)
    request_function = kwargs.pop("request_function")
    headers = kwargs.pop("headers")
    _validate_headers_type(headers)
    headers.update(token_refresher.authorization_header) # type: ignore

    send_request_with_auth = make_callable_request(
        obj, request_function, headers, *args, **kwargs)
    response = send_request_with_auth()
    _validate_response_type(response, request_function)

    if not response.ok:
        if response.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            token_refresher.authorize()
            headers.update(token_refresher.authorization_header) # type: ignore
            send_request_with_auth = make_callable_request(obj,
                                                           request_function,
                                                           headers,
                                                           *args, **kwargs)
            response = send_request_with_auth()
    return response


def authorize(token_refresher: Optional[TokenRefresher] = None) -> Callable:
    """
    Wrap a request function and check response. If response's error status code
    is about Authorization, refresh token and invoke this function once again.
    Expects function:
    If response is not ok and not about Authorization, then raises HTTPError
    request_func(header: dict, *args, **kwargs) -> requests.Response
    Or method:
    request_method(self, header: dict, *args, **kwargs) -> requests.Response
    """

    def refresh_token_wrapper(request_function: Callable) -> Callable:
        is_method = len(request_function.__qualname__.split(".")) > 1
        if is_method:
            def _wrapper(obj: object, headers: dict, *args, **kwargs) -> requests.Response:
                _token_refresher = _get_object_token_refresher(obj)
                _validate_token_refresher_type(_token_refresher)
                return send_request_with_auth_header(_token_refresher,
                                                     request_function=request_function,
                                                     obj=obj,
                                                     headers=headers,
                                                     *args,
                                                     **kwargs)
        else:
            def _wrapper(headers: dict, *args, **kwargs) -> requests.Response:
                if not isinstance(token_refresher, TokenRefresher):
                    raise TokenRefresherNotPresentError(
                        "Token refresher isn't provided or has wrong type in 'authorize' decorator."
                    )
                _validate_token_refresher_type(token_refresher)
                return send_request_with_auth_header(token_refresher,
                                                     request_function=request_function,
                                                     headers=headers,
                                                     *args, **kwargs)
        return _wrapper

    return refresh_token_wrapper
