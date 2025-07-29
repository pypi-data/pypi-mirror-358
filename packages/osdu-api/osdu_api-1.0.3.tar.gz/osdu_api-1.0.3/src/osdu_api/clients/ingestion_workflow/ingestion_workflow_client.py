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

import json
from typing import Optional

from osdu_api.auth.authorization import TokenRefresher
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.clients.base_client import BaseClient
from osdu_api.model.ingestion_workflow.create_workflow_request import CreateWorkflowRequest
from osdu_api.model.ingestion_workflow.trigger_workflow_request import TriggerWorkflowRequest
from osdu_api.model.ingestion_workflow.update_workflow_run_request import UpdateWorkflowRunRequest
from osdu_api.model.http_method import HttpMethod

class IngestionWorkflowClient(BaseClient):
    """
    Holds the logic for interfacing with Ingestion Workflow's api
    """

    def __init__(
        self,
        ingestion_workflow_url: Optional[str] = None,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger=None,
        user_id: Optional[str] = None
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger,
                         user_id)
        self.ingestion_workflow_url = ingestion_workflow_url or self.config_manager.get('environment', 'ingestion_workflow_url')

    def get_workflow(self, workflow_name: str, bearer_token=None):
        params = {'workflowName': workflow_name}
        return self.make_request(method=HttpMethod.GET, url='{}{}'.format(self.ingestion_workflow_url, '/workflow'),
            params=params, bearer_token=bearer_token)

    def create_workflow(self, create_workflow_request: CreateWorkflowRequest, bearer_token=None):
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.ingestion_workflow_url, '/workflow'),
            data=create_workflow_request.to_JSON(), bearer_token=bearer_token)

    def get_all_workflows_in_partition(self, bearer_token=None):
        return self.make_request(method=HttpMethod.GET, url='{}{}'.format(self.ingestion_workflow_url, '/workflow'),
            bearer_token=bearer_token)

    def delete_workflow(self, workflow_name: str, bearer_token=None):
        params = {'workflowName': workflow_name}
        return self.make_request(method=HttpMethod.DELETE, url='{}{}'.format(self.ingestion_workflow_url, '/workflow'),
            params=params, bearer_token=bearer_token)

    def trigger_workflow(self, trigger_workflow_request: TriggerWorkflowRequest, workflow_name: str, bearer_token=None):
        return self.make_request(method=HttpMethod.POST, url='{}{}{}{}'.format(self.ingestion_workflow_url, '/workflow/', workflow_name, '/workflowRun'),
            data=trigger_workflow_request.to_JSON(), bearer_token=bearer_token)

    def get_workflow_runs(self, workflow_name: str, bearer_token=None):
        return self.make_request(method=HttpMethod.GET, url='{}{}{}{}'.format(self.ingestion_workflow_url, '/workflow/', workflow_name, '/workflowRun'),
            bearer_token=bearer_token)

    def get_workflow_run_by_id(self, workflow_name: str, run_id: str, bearer_token=None):
        return self.make_request(method=HttpMethod.GET, url='{}{}{}{}{}'.format(self.ingestion_workflow_url, '/workflow/', workflow_name, '/workflowRun/', run_id),
            bearer_token=bearer_token)

    def update_workflow_run(self, update_workflow_run_request: UpdateWorkflowRunRequest, workflow_name: str, run_id: str, bearer_token=None):
        return self.make_request(method=HttpMethod.PUT, url='{}{}{}{}{}'.format(self.ingestion_workflow_url, '/workflow/', workflow_name, '/workflowRun/', run_id),
             data=update_workflow_run_request.to_JSON(), bearer_token=bearer_token)
