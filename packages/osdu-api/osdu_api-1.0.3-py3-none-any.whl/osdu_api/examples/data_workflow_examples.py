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

from osdu_api.clients.data_workflow.data_workflow_client import DataWorkflowClient
from osdu_api.clients.data_workflow.data_workflow_scheduling_client import \
    DataWorkflowSchedulingClient
from osdu_api.clients.dataset_registry.dataset_registry_client import DatasetRegistryClient
from osdu_api.clients.file_dms.file_dms_client import FileDMSClient
from osdu_api.model.data_workflow.get_workflow_schedules_request import GetWorkflowSchedulesRequest
from osdu_api.model.data_workflow.workflow_schedule import WorkflowSchedule
from osdu_api.model.dataset_registry.create_dataset_registries import CreateDatasetRegistries
from osdu_api.model.file_dms.file import File
from osdu_api.model.file_dms.register_files import RegisterFiles
from osdu_api.model.storage.acl import Acl
from osdu_api.model.storage.legal import Legal
from osdu_api.model.storage.record import Record
from osdu_api.model.storage.record_ancestry import RecordAncestry

data_workflow_client = DataWorkflowClient("opendes")
data_workflow_scheduling_client = DataWorkflowSchedulingClient("opendes")
dataset_registry_client = DatasetRegistryClient("opendes")
file_dms_client = FileDMSClient("opendes")

# cd ../.. && pip3 uninstall osdu_api && python3 setup.py sdist bdist_wheel && python3 -m pip install ./dist/osdu_api-0.0.2-py3-none-any.whl && cd osdu_api/examples

def data_workflow_scheduling_example():
    workflow_schedule = WorkflowSchedule("test-name", "test-desc", "0 12 * * ? *", "my_first_dag", {})
    data_workflow_scheduling_client.create_workflow_schedule(workflow_schedule)

    get_workflow_schedules_request = GetWorkflowSchedulesRequest(["test-name"])
    response = data_workflow_scheduling_client.get_workflow_schedules(get_workflow_schedules_request)

    print(response.content)


def file_dms_example():
    location = file_dms_client.get_file_upload_location()

    print(location.content)

    unsigned_url = json.loads(location.content)['uploadLocation']['unsignedUrl'] + '/example.json'

    cust_file = File(unsigned_url, 'example.json', 'An example file')

    register_files = RegisterFiles([cust_file])

    register_files_resp = file_dms_client.register_files(register_files)

    print(register_files_resp.status_code)
    print(register_files_resp.content)

def dataset_registry_example():
    # def __init__(self, id: str, version: int, kind: str, acl: Acl, legal: Legal, data: dict, ancestry: RecordAncestry,

    kind = 'opendes:osdu:dataset-registry:0.0.1'
    viewers = ['data.default.viewers@opendes.testing.com']
    owners = ['data.default.owners@opendes.testing.com']
    acl = Acl(viewers, owners)
    # legal_compliance = LegalCompliance.compliant
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
    ancestry = RecordAncestry([])
    record = Record(None, None, kind, acl, legal, data, ancestry, None)

    create_request = CreateDatasetRegistries(record)

    response = dataset_registry_client.create_registries(create_request)

    print(response.status_code)
    print(response.content)

data_workflow_scheduling_example()
# dataset_registry_example()
# file_dms_example()
