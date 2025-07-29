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
from typing import List

from osdu_api.model.crs_conversion.feature import Feature


class FeatureCollection(BaseNoNull):
    def __init__(
        self,
        collection_type: Optional[str] = None,
        coordinate_reference_system_id: Optional[str] = None,
        persistable_reference_crs: Optional[str] = None,
        persistable_reference_unit_z: Optional[str] = None,
        features: Optional[List[Feature]] = None,
        bbox: Optional[list] = None,
        properties: Optional[dict] = None,
    ):
        self.type = collection_type
        self.CoordinateReferenceSystemID = coordinate_reference_system_id
        self.persistableReferenceCrs = persistable_reference_crs
        self.persistableReferenceUnitZ = persistable_reference_unit_z
        self.features = features
        self.bbox = bbox
        self.properties = properties
