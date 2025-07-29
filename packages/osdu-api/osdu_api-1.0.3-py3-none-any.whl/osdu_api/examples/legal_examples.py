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
from osdu_api.clients.legal.legal_client import LegalClient
from osdu_api.model.legal.legal_tag import LegalTag
from osdu_api.model.legal.legal_tag_properties import LegalTagProperties
from osdu_api.configuration.config_manager import DefaultConfigManager
import os

os.environ['BASE_URL'] = 'https://suttonsp.dev.osdu.aws'
legal_client = LegalClient(DefaultConfigManager(), "opendes")


legal_tag_properties = LegalTagProperties(['US'], 'A1234', 2222222222222, 'default', 'Public Domain Data', 'Public', 'No Personal Data', 'EAR99')
legal_tag = LegalTag('public-usa-dataset-3', legal_tag_properties, 'a default legal tag')

response = legal_client.create_legal_tag(legal_tag)
print(response.status_code)

response = legal_client.get_legal_tag('opendes-public-usa-dataset-3')
print(response.content)
