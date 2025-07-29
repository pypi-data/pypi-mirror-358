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
from osdu_api.model.unit.map_state import MapState
from osdu_api.model.unit.measurement_map_item import MeasurementMapItem
from osdu_api.model.unit.measurement import Measurement
from osdu_api.model.unit.unit_map_item import UnitMapItem
from osdu_api.model.unit.unit import Unit


class QueryResult(BaseNoNull):

    def __init__(
        self,
        count: Optional[int] = None,
        map_states: Optional[List[MapState]] = None,
        measurement_map_items: Optional[List[MeasurementMapItem]] = None,
        measurements: Optional[List[Measurement]] = None,
        offset: Optional[int] = None,
        total_count: Optional[int] = None,
        unit_map_items: Optional[List[UnitMapItem]] = None,
        units: Optional[List[Unit]] = None,
    ):
        self.count = count
        self.mapStates = map_states
        self.measurementMapItems = measurement_map_items
        self.measurements = measurements
        self.offset = offset
        self.totalCount = total_count
        self.unitMapItems = unit_map_items
        self.units = units
