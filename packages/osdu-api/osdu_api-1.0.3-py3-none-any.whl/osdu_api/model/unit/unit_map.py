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
from osdu_api.model.unit.unit_map_item import UnitMapItem


class UnitMap(BaseNoNull):

    def __init__(
        self,
        from_namespace: Optional[str] = None,
        to_namespace: Optional[str] = None,
        unit_map_item_count: Optional[int] = None,
        unit_map_items: Optional[List[UnitMapItem]] = None,
    ):
        self.fromNamespace = from_namespace
        self.toNamespace = to_namespace
        self.unitMapItemCount = unit_map_item_count
        self.unitMapItems = unit_map_items
