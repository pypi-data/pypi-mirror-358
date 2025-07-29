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
from osdu_api.model.unit.unit_assignment import UnitAssignment


class UnitSystem(BaseNoNull):

    def __init__(
        self,
        ancestry: Optional[str] = None,
        description: Optional[str] = None,
        last_modified: Optional[str] = None,
        name: Optional[str] = None,
        offset: Optional[int] = None,
        persistable_reference: Optional[str] = None,
        reference_unit_system: Optional[str] = None,
        source: Optional[str] = None,
        unit_assignment_count: Optional[int] = None,
        unit_assignment_count_in_response: Optional[int] = None,
        unit_assignment_count_total: Optional[int] = None,
        unit_assignments: Optional[List[UnitAssignment]] = None,
    ):
        self.ancestry = ancestry
        self.description = description
        self.lastModified = last_modified
        self.name = name
        self.offset = offset
        self.persistableReference = persistable_reference
        self.referenceUnitSystem = reference_unit_system
        self.source = source
        self.unitAssignmentCount = unit_assignment_count
        self.unitAssignmentCountInResponse = unit_assignment_count_in_response
        self.unitAssignmentCountTotal = unit_assignment_count_total
        self.unitAssignments = unit_assignments
