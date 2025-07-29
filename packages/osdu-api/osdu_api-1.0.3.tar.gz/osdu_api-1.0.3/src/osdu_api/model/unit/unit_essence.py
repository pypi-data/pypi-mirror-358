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
from osdu_api.model.unit.abcd import ABCD
from osdu_api.model.unit.measurement_essence import MeasurementEssence
from osdu_api.model.unit.scale_offset import ScaleOffset


class UnitEssence(BaseNoNull):

    def __init__(
        self,
        abcd: Optional[ABCD] = None,
        base_measurement: Optional[MeasurementEssence] = None,
        scale_offset: Optional[ScaleOffset] = None,
        symbol: Optional[str] = None,
        type: Optional[str] = None,
    ):
        self.abcd = abcd
        self.baseMeasurement = base_measurement
        self.scaleOffset = scale_offset
        self.symbol = symbol
        self.type = type
