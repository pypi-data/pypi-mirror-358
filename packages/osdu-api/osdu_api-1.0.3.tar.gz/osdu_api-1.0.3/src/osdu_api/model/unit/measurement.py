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
from osdu_api.model.unit.measurement_deprecation_info import MeasurementDeprecationInfo
from osdu_api.model.unit.measurement_essence import MeasurementEssence


class Measurement(BaseNoNull):

    def __init__(
        self,
        base_measurement: Optional[bool] = None,
        base_measurement_essence_json: Optional[str] = None,
        child_measurement_essence_jsons: Optional[List[str]] = None,
        code: Optional[str] = None,
        deprecation_info: Optional[MeasurementDeprecationInfo] = None,
        description: Optional[str] = None,
        dimension_analysis: Optional[str] = None,
        dimension_code: Optional[str] = None,
        essence: Optional[MeasurementEssence] = None,
        essence_json: Optional[str] = None,
        last_modified: Optional[str] = None,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        parent_essence_json: Optional[str] = None,
        preferred_unit_essence_jsons: Optional[List[str]] = None,
        unit_essence_jsons: Optional[List[str]] = None,
        unit_quantity_code: Optional[str] = None,
    ):
        self.baseMeasurement = base_measurement
        self.baseMeasurementEssenceJson = base_measurement_essence_json
        self.childMeasurementEssenceJsons = child_measurement_essence_jsons
        self.code = code
        self.deprecationInfo = deprecation_info
        self.description = description
        self.dimensionAnalysis = dimension_analysis
        self.dimensionCode = dimension_code
        self.essence = essence
        self.essenceJson = essence_json
        self.lastModified = last_modified
        self.name = name
        self.namespace = namespace
        self.parentEssenceJson = parent_essence_json
        self.preferredUnitEssenceJsons = preferred_unit_essence_jsons
        self.unitEssenceJsons = unit_essence_jsons
        self.unitQuantityCode = unit_quantity_code
