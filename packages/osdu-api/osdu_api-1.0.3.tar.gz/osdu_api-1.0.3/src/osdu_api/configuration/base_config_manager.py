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

import abc
from typing import Optional


class BaseConfigManager(metaclass=abc.ABCMeta):

    
    @abc.abstractmethod
    def get(self, section: str, option: str, default: Optional[str] = None) -> str:
        """       
         Get config value.

        :param section: Section of ini file.
        :type section: str
        :param option: Param of the section.
        :type option: str
        :param default: Default value, defaults to None.
        :type default: str, optional
        :return: Config value.
        :rtype: str
        """

    @abc.abstractmethod
    def getint(self, section: str, option: str, default: Optional[int] = None) -> int:
        """
        Get config value. as int

        :param section: Section of ini file.
        :type section: str
        :param option: Param of the section.
        :type option: str
        :param default: Default value, defaults to None
        :type default: int, optional
        :return: Config value.
        :rtype: int
        """

    @abc.abstractmethod
    def getfloat(self, section: str, option: str, default: Optional[float] = None) -> float:
        """
        Get config value as float.

        :param section: Section of ini file.
        :type section: str
        :param option: Param of the section.
        :type option: str
        :param default: Default value, defaults to None
        :type default: float, optional
        :return: Config value.
        :rtype: float
        """

    @abc.abstractmethod
    def getbool(self, section: str, option: str, default: Optional[bool] = None) -> bool:
        """
        Get config value as bool.

        :param section: Section of ini file.
        :type section: str
        :param option: Param of the section.
        :type option: str
        :param default: Default value, defaults to None
        :type default: bool, optional
        :return: Config value
        :rtype: bool
        """
            