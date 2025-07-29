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
from osdu_api.model.unit.measurement import Measurement


class MeasurementMapItem(BaseNoNull):

    def __init__(
        self,
        from_measurement: Optional[Measurement] = None,
        from_namespace: Optional[str] = None,
        note: Optional[str] = None,
        state: Optional[str] = None,
        to_measurement: Optional[Measurement] = None,
        to_namespace: Optional[str] = None,
    ):
        self.fromMeasurement = from_measurement
        self.fromNamespace = from_namespace
        self.note = note
        self.state = state
        self.toMeasurement = to_measurement
        self.toNamespace = to_namespace
