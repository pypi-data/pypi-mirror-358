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

from osdu_api.model.crs_conversion.convert_base import ConvertBase
from osdu_api.model.crs_conversion.feature_collection import FeatureCollection


class ConvertGeoJson(ConvertBase):
    def __init__(
        self, to_crs: str, to_unit_z: str, feature_collection: FeatureCollection
    ):
        super(ConvertGeoJson, self).__init__(to_crs=to_crs)
        self.toUnitZ = to_unit_z
        self.featureCollection = feature_collection
