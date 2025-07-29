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

from osdu_api.model.crs_catalog.base_crs import BaseCRS
from osdu_api.model.crs_catalog.datum import Datum
from osdu_api.model.crs_catalog.extent import Extent

class PostCRSCatalogCoordinateReferenceSystem(BaseNoNull):

    def __init__(self, 
                base_crs: Optional[BaseCRS] = None,
                code: Optional[str] = None,
                code_space: Optional[str] = None,
                coordinate_reference_system_type: Optional[str] = None,
                datum: Optional[Datum] = None,
                extent: Optional[Extent] = None,
                horizontal_axis_unit_id: Optional[str] = None,
                ref_id: Optional[str] = None,
                include_deprecated: Optional[bool] = None,
                kind: Optional[str] = None,
                latitude: Optional[float] = None,
                limit: Optional[float] = None,
                longitude: Optional[float] = None,
                name: Optional[str] = None,
                offset: Optional[float] = None,
                return_all_fields: Optional[bool] = None,
                return_bound_geographic2d_and_wgs84: Optional[bool] = None,
                return_bound_projected_and_projected_based_on_wgs84: Optional[bool] = None,
                vertical_axis_unit_id: Optional[str] = None,
        ):
        self.baseCRS = base_crs
        self.code = code
        self.codeSpace = code_space
        self.coordinateReferenceSystemType = coordinate_reference_system_type
        self.datum = datum
        self.extent = extent
        self.horizontalAxisUnitId = horizontal_axis_unit_id
        self.id = ref_id
        self.includeDeprecated = include_deprecated
        self.kind = kind
        self.latitude = latitude
        self.limit = limit
        self.longitude = longitude
        self.name = name
        self.offset = offset
        self.returnAllFields = return_all_fields
        self.returnBoundGeographic2DAndWgs84 = return_bound_geographic2d_and_wgs84
        self.returnBoundProjectedAndProjectedBasedOnWgs84 = return_bound_projected_and_projected_based_on_wgs84
        self.verticalAxisUnitId = vertical_axis_unit_id
