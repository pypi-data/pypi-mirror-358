# Copyright © 2020 Amazon Web Services
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
import json
from types import MappingProxyType


class Base:
    def to_JSON(self):
        return json.dumps(self, default=lambda o: self.jsonify(o), 
            sort_keys=True, indent=4)

    def jsonify(self, o):
        return o.__dict__ if type(o) is not dict else self

class BaseNoNull(Base):
    def jsonify(self, o):
        if type(o) is not dict:
            d = {}
            for a in o.__dict__:
                if o.__dict__[a] is not None:
                    d[a] = o.__dict__[a]
            return d
        return self