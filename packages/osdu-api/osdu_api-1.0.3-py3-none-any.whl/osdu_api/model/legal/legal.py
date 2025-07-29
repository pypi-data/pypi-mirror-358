#  Copyright 2020 Google LLC
#  Copyright © 2020 Amazon Web Services
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Optional

from osdu_api.model.legal.legal_compliance import LegalCompliance


class Legal:
    """
    Legal model mirroring what's found in core common
    """

    def __init__(self, legaltags: list, other_relevant_data_countries: list, status: Optional[LegalCompliance] = None):
        self.legaltags = legaltags
        # have to preserve this camel case name, because the base class uses name attributes to jsonfy 
        # the class
        self.otherRelevantDataCountries = other_relevant_data_countries
        self.status = status

    def get_dict(self):
        legal_dict = {}
        legal_dict['legaltags'] = self.legaltags
        legal_dict['otherRelevantDataCountries'] = self.otherRelevantDataCountries
        if self.status:
            legal_dict['status'] = str(self.status)
        return legal_dict
        