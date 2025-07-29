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
from osdu_api.model.base import BaseNoNull

from osdu_api.model.crs_conversion.abcd_bin_grid_spatial_location import (
    ABCDBinGridSpatialLocation,
)


class InBinGrid(BaseNoNull):
    def __init__(
        self,
        abcd_bin_grid_spatial_location: Optional[ABCDBinGridSpatialLocation] = None,
        coverage_percent: Optional[float] = None,
        p6_scale_factor_of_bin_grid: Optional[float] = None,
        p6_bin_node_increment_on_iaxis: Optional[float] = None,
        p6_bin_node_increment_on_jaxis: Optional[float] = None,
    ):
        self.ABCDBinGridSpatialLocation = abcd_bin_grid_spatial_location
        self.CoveragePercent = coverage_percent
        self.P6ScaleFactorOfBinGrid = p6_scale_factor_of_bin_grid
        self.P6BinNodeIncrementOnIaxis = p6_bin_node_increment_on_iaxis
        self.P6BinNodeIncrementOnJaxis = p6_bin_node_increment_on_jaxis
