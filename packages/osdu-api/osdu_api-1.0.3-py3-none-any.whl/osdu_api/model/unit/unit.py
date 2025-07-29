# Copyright 2023 Geosiris
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from osdu_api.model.base import BaseNoNull
from typing import Optional, List
from osdu_api.model.unit.unit_deprecation_info import UnitDeprecationInfo
from osdu_api.model.unit.unit_essence import UnitEssence


class Unit(BaseNoNull):

    def __init__(
        self,
        deprecation_info: Optional[UnitDeprecationInfo] = None,
        description: Optional[str] = None,
        display_symbol: Optional[str] = None,
        essence: Optional[UnitEssence] = None,
        essence_json: Optional[str] = None,
        last_modified: Optional[str] = None,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        source: Optional[str] = None,
    ):
        self.deprecationInfo = deprecation_info
        self.description = description
        self.displaySymbol = display_symbol
        self.essence = essence
        self.essenceJson = essence_json
        self.lastModified = last_modified
        self.name = name
        self.namespace = namespace
        self.source = source
