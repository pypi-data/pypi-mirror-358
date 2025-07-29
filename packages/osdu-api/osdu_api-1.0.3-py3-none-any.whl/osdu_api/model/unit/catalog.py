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
from osdu_api.model.unit.measurement_map import MeasurementMap
from osdu_api.model.unit.measurement import Measurement
from osdu_api.model.unit.unit_map import UnitMap
from osdu_api.model.unit.unit_system_info import UnitSystemInfo
from osdu_api.model.unit.unit import Unit


class Catalog(BaseNoNull):

    def __init__(
        self,
        last_modified: Optional[str] = None,
        map_states: Optional[List[MapState]] = None,
        measurement_maps: Optional[List[MeasurementMap]] = None,
        measurements: Optional[List[Measurement]] = None,
        total_map_state_count: Optional[int] = None,
        total_measurement_count: Optional[int] = None,
        total_measurement_map_count: Optional[int] = None,
        total_unit_count: Optional[int] = None,
        total_unit_map_count: Optional[int] = None,
        total_unit_system_count: Optional[int] = None,
        unit_maps: Optional[List[UnitMap]] = None,
        unit_system_infos: Optional[List[UnitSystemInfo]] = None,
        units: Optional[List[Unit]] = None,
    ):
        self.lastModified = last_modified
        self.mapStates = map_states
        self.measurementMaps = measurement_maps
        self.measurements = measurements
        self.totalMapStateCount = total_map_state_count
        self.totalMeasurementCount = total_measurement_count
        self.totalMeasurementMapCount = total_measurement_map_count
        self.totalUnitCount = total_unit_count
        self.totalUnitMapCount = total_unit_map_count
        self.totalUnitSystemCount = total_unit_system_count
        self.unitMaps = unit_maps
        self.unitSystemInfos = unit_system_infos
        self.units = units
