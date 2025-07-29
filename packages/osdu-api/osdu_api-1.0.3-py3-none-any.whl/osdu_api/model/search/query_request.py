# Copyright © 2020 Amazon Web Services
# Copyright 2022 Google LLC
# Copyright 2022 EPAM Systems
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

from typing import Optional

from osdu_api.model.base import Base
from osdu_api.model.search.sort_query import SortQuery
from osdu_api.model.search.spatial_filter import SpatialFilter


class QueryRequest(Base):

    def __init__(
        self,
        kind: str,
        query: str,
        limit: Optional[int] = None,
        return_highlighted_fields: Optional[bool] = None,
        returned_fields: Optional[list] = None,
        sort: Optional[SortQuery] = None,
        query_as_owner: Optional[bool] = None,
        track_total_count: Optional[bool] = False,
        spatial_filter: Optional[SpatialFilter] = None,
        from_num: Optional[int] = None,
        aggregate_by: Optional[str] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None
    ):
        self.kind = kind
        self.limit = limit
        self.query = query
        self.returnHighlightedFields = return_highlighted_fields
        self.returnedFields = returned_fields
        self.sort = sort
        self.queryAsOwner = query_as_owner
        self.spatialFilter = spatial_filter
        self.from_num = from_num
        self.aggregateBy = aggregate_by
        self.offset = offset
        self.cursor = cursor
        self.trackTotalCount = track_total_count

    def jsonify(self, o):
        d = o.__dict__
        if 'from_num' in d:
            d['from'] = d['from_num']
            del d['from_num']
        return d
