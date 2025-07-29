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
from osdu_api.model.unit.unit_system_info import UnitSystemInfo


class UnitSystemInfoResponse(BaseNoNull):

    def __init__(
        self,
        count: Optional[int] = None,
        offset: Optional[int] = None,
        total_count: Optional[int] = None,
        unit_system_info_list: Optional[List[UnitSystemInfo]] = None,
    ):
        self.count = count
        self.offset = offset
        self.totalCount = total_count
        self.unitSystemInfoList = unit_system_info_list
