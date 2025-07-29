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


class PostCRSCatalogCoordinateTransformation(BaseNoNull):

    def __init__(self, 
                source_crs: Optional[str] = None,
                target_crs: Optional[str] = None,
                code_space: Optional[str] = None,
                name: Optional[str] = None,
                rec_id: Optional[str] = None,
                code: Optional[str] = None,
                kind: Optional[str] = None,
                latitude: Optional[float] = None,
                longitude: Optional[float] = None,
                include_deprecated: Optional[bool] = None,
                offset: Optional[float] = None,
                limit: Optional[float] = None,
                return_all_fields: Optional[bool] = None,
        ):
        self.codeSpace = code_space
        self.name = name
        self.id = rec_id
        self.code = code
        self.kind = kind
        self.sourceCRS = source_crs
        self.targetCRS = target_crs
        self.latitude = latitude
        self.longitude = longitude
        self.includeDeprecated = include_deprecated
        self.offset = offset
        self.limit = limit
        self.returnAllFields = return_all_fields
