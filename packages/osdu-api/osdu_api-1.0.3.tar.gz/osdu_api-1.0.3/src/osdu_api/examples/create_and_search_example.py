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
'''
Basic example on creating a record and searching on it to get it back
'''

import os
import time

from osdu_api.clients.search.search_client import SearchClient
from osdu_api.clients.storage.record_client import RecordClient
from osdu_api.model.search.query_request import QueryRequest
from osdu_api.model.storage.acl import Acl
from osdu_api.model.storage.legal import Legal
from osdu_api.model.storage.record import Record
from osdu_api.model.storage.record_ancestry import RecordAncestry

record_client = RecordClient("opendes")
search_client = SearchClient("opendes")

kind = 'opendes:osdu:dataset-registry:0.0.1'
viewers = ['data.default.viewers@opendes.testing.com']
owners = ['data.default.owners@opendes.testing.com']
acl = Acl(viewers, owners)
legal = Legal(['opendes-public-usa-dataset-1'], ['US'], "compliant")
data = {
		"ResourceID": "srn:osdu:file:dc556e0e3a554105a80cfcb19372a62d:",
		"ResourceTypeID": "srn:type:file/json:",
		"ResourceSecurityClassification": "srn:reference-data/ResourceSecurityClassification:RESTRICTED:",
		"ResourceSource": "Some Company App",
		"ResourceName": "trajectories - 1000.json",
        "ResourceDescription": "Trajectory For Wellbore xyz",
		"DatasetProperties": {
			"FileSourceInfo": {
				"FileSource": "",
				"PreLoadFilePath": "s3://default_bucket/r1/data/provided/trajectories/1000.json"
			}
		}
	}
record = Record(kind, acl, legal, data)

query_request = QueryRequest(kind, "data.ResourceName = \"trajectories - 1000.json\"")

create_record_resp = record_client.create_update_records([record], bearer_token="eyJraWQiOiJrWmpnYTR5ZXJyWVwvdVByT29wSXBTNnVFWmZLRGVoTUt3d3VIRjAxZUlmOD0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5MDE3NDdmOS1jMzRkLTQ5MjktYTczYi0zMzY5ZmU2NDNmYTYiLCJldmVudF9pZCI6ImNjYjg1MzY2LTNlZDMtNGMxZC04NDk2LTNjZjhmYzFjNTIyOSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoib3BlbmlkIGVtYWlsIiwiYXV0aF90aW1lIjoxNjA5NzczODQ1LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV8yOE8wMXlFN00iLCJleHAiOjE2MTEyNDU5NTEsImlhdCI6MTYxMTE1OTU1MSwidmVyc2lvbiI6MiwianRpIjoiODFkYjBlN2ItNTkxNy00ODZmLWIwMGUtZWYzNThmODM1ZGM3IiwiY2xpZW50X2lkIjoiNWxrcjZ2OGRrOHU2dnN1ZGVlZGluYW10OGEiLCJ1c2VybmFtZSI6ImphY29icm91Z2VhdUB0ZXN0aW5nLmNvbSJ9.Z_8lvjj3jCmXx2w0fG2IXK3Wsd1GVSufgWdOhEyXMqzOXIqWZNMrAOtXwng6oX5z0n2c3fXQEUC5QAjAXvrDx_elpqd9Gnpiauzu9t5sVthKYw6OOWzR3Ny_iR-V5zG-eXCXTnrvZJsibcEI7ouH5RyRe_zcUhfaDbixb1uKWUGbD2hUCyEr30FawkKOB5E-_PXQQdK0pJn_eAwj-Z_-8IFOETBI6xsYG9-QjQoyVcK1KYqHfMzP0moANP1T3PZSsXnpTZqDlPif8jD2hVpKCDF-rXa8eI45WE5XWBMh5gUUcgT5AiEXKMFll19-RSg0jnu3a3PZ1YnxkyFaaumCFg")

print(create_record_resp.status_code)
print(create_record_resp.content)

if create_record_resp.status_code != 201:
    print("Record failed to create")
    exit

# give the system 10 seconds to index the record
time.sleep(10)

search_record_resp = search_client.query_records(query_request, bearer_token="eyJraWQiOiJrWmpnYTR5ZXJyWVwvdVByT29wSXBTNnVFWmZLRGVoTUt3d3VIRjAxZUlmOD0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI5MDE3NDdmOS1jMzRkLTQ5MjktYTczYi0zMzY5ZmU2NDNmYTYiLCJldmVudF9pZCI6ImNjYjg1MzY2LTNlZDMtNGMxZC04NDk2LTNjZjhmYzFjNTIyOSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoib3BlbmlkIGVtYWlsIiwiYXV0aF90aW1lIjoxNjA5NzczODQ1LCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV8yOE8wMXlFN00iLCJleHAiOjE2MTEyNDU5NTEsImlhdCI6MTYxMTE1OTU1MSwidmVyc2lvbiI6MiwianRpIjoiODFkYjBlN2ItNTkxNy00ODZmLWIwMGUtZWYzNThmODM1ZGM3IiwiY2xpZW50X2lkIjoiNWxrcjZ2OGRrOHU2dnN1ZGVlZGluYW10OGEiLCJ1c2VybmFtZSI6ImphY29icm91Z2VhdUB0ZXN0aW5nLmNvbSJ9.Z_8lvjj3jCmXx2w0fG2IXK3Wsd1GVSufgWdOhEyXMqzOXIqWZNMrAOtXwng6oX5z0n2c3fXQEUC5QAjAXvrDx_elpqd9Gnpiauzu9t5sVthKYw6OOWzR3Ny_iR-V5zG-eXCXTnrvZJsibcEI7ouH5RyRe_zcUhfaDbixb1uKWUGbD2hUCyEr30FawkKOB5E-_PXQQdK0pJn_eAwj-Z_-8IFOETBI6xsYG9-QjQoyVcK1KYqHfMzP0moANP1T3PZSsXnpTZqDlPif8jD2hVpKCDF-rXa8eI45WE5XWBMh5gUUcgT5AiEXKMFll19-RSg0jnu3a3PZ1YnxkyFaaumCFg")

print(search_record_resp.results)