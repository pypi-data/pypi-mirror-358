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
from osdu_api.model.unit.unit_essence import UnitEssence


class ConversionABCDRequest(BaseNoNull):

    def __init__(
        self,
        from_unit: Optional[UnitEssence] = None,
        from_unit_persistable_reference: Optional[str] = None,
        to_unit: Optional[UnitEssence] = None,
        to_unit_persistable_reference: Optional[str] = None,
    ):
        self.fromUnit = from_unit
        self.fromUnitPersistableReference = from_unit_persistable_reference
        self.toUnit = to_unit
        self.toUnitPersistableReference = to_unit_persistable_reference
