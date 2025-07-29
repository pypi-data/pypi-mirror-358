# Copyright 2023 Geosiris
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional
from typing import List

from osdu_api.model.base import BaseNoNull
from osdu_api.model.crs_conversion.point import Point
from osdu_api.model.crs_conversion.station import Station


class ConvertTrajectory(BaseNoNull):
    def __init__(
        self,
        trajectory_crs: Optional[str] = None,
        azimuth_reference: Optional[str] = None,
        unit_xy: Optional[str] = None,
        unit_z: Optional[str] = None,
        reference_point: Optional[Point] = None,
        input_kind: Optional[str] = None,
        interpolate: Optional[bool] = None,
        input_stations: Optional[List[Station]] = None,
        method: Optional[str] = None,
    ):
        self.trajectoryCRS = trajectory_crs
        self.azimuthReference = azimuth_reference
        self.unitXY = unit_xy
        self.unitZ = unit_z
        self.referencePoint = reference_point
        self.inputKind = input_kind
        self.interpolate = interpolate
        self.inputStations = input_stations
        self.method = method
