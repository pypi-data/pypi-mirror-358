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
from osdu_api.model.storage.acl import Acl
from osdu_api.model.storage.legal import Legal
from osdu_api.model.legal.legal_compliance import LegalCompliance
from osdu_api.model.storage.record_ancestry import RecordAncestry


class Record(Base):
    """
    A record model mirroring what's found in core common
    """

    def __init__(
        self, 
        kind: str, 
        acl: Acl, 
        legal: Legal, 
        data: dict, 
        id: Optional[str] = None, 
        version: Optional[int] = None, 
        ancestry: Optional[RecordAncestry] = None,
        meta: Optional[dict] = None,
        tags: Optional[dict] = None
    ):
        self.id = id
        self.version = version
        self.kind = kind
        self.acl = acl
        self.legal = legal
        self.data = data
        self.ancestry = ancestry
        self.meta = meta
        self.tags = tags

    @classmethod
    def from_dict(cls, record_dict: dict):
        id = record_dict.get('id')
        version = record_dict.get('version')
        kind = record_dict['kind']
        acl = Acl(record_dict['acl']['viewers'], record_dict['acl']['owners'])
        legal = Legal(
            record_dict['legal']['legaltags'], 
            record_dict['legal']['otherRelevantDataCountries'], 
            record_dict['legal']['status'] if record_dict["legal"].get("status") else None
        )
        data = record_dict['data']
        meta = record_dict.get('meta')
        tags = record_dict.get('tags')

        parents = []
        try:
            parents = record_dict['ancestry']['parents']
        except KeyError:
            # warn the user that ancestry wasn't found, not essential attribute
            print('Attribute "ancestry" is missing from dict being converted to record')

        ancestry = RecordAncestry(parents)

        return cls(kind, acl, legal, data, id, version, ancestry, meta, tags)

    def convert_to_dict(self):
        record_converted = self.__dict__
        record_converted['acl'] = self.acl.__dict__
        record_converted['legal'] = self.legal.get_dict()
        record_converted['ancestry'] = self.ancestry.__dict__
        return record_converted
