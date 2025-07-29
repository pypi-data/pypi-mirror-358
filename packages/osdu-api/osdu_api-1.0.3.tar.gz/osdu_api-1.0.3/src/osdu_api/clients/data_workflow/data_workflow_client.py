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
from typing import List, Optional

from osdu_api.auth.authorization import TokenRefresher
from osdu_api.configuration.base_config_manager import BaseConfigManager
from osdu_api.clients.base_client import BaseClient
from osdu_api.model.data_workflow.start_workflow import StartWorkflow
from osdu_api.model.data_workflow.update_status_request import UpdateStatusRequest
from osdu_api.model.http_method import HttpMethod


class DataWorkflowClient(BaseClient):
    """
    Holds the logic for interfacing with Data Workflow's api
    """

    def __init__(
        self,
        data_workflow_url: Optional[str] = None,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger=None,
        user_id: Optional[str] = None
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger,
                         user_id)
        self.data_workflow_url = data_workflow_url or self.config_manager.get('environment', 'data_workflow_url')

    def start_workflow(self, start_workflow: StartWorkflow, bearer_token=None):
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.data_workflow_url, '/startWorkflow'),
            data=start_workflow.to_JSON(), bearer_token=bearer_token)

    def update_status(self, update_status_request: UpdateStatusRequest, bearer_token=None):
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.data_workflow_url, '/updateStatus'),
            data=update_status_request.to_JSON(), bearer_token=bearer_token)
