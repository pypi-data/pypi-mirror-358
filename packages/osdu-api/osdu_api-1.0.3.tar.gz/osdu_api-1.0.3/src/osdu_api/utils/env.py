#  Copyright © Microsoft Corporation
#  Copyright 2021 EPAM Systems
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
"""Utils for env management."""

import os
from typing import Any, List, Optional


def getenv_by_names(names: List[str], safe: bool = False, default_value: Any  = 'None') -> Optional[str]:
    """
    Checking several env variables and return result value by priority.

    :param names: Env variables names for checking
    :type names: List[str]
    :param safe: Safe mode
    :type safe: bool
    :param default_value: Default safe value
    :type default_value: Any
    :return: Env variable result
    :rtype: Optional[str]
    """
    for env_name in names:
        env_value = os.getenv(env_name)
        if env_value:
            return env_value

    return default_value if safe else None


def getenv(key: str) -> str:
    """

    """
    env_value = os.getenv(key)
    if env_value:
        return env_value
    else:
        raise ValueError("Given environment variable not found")
