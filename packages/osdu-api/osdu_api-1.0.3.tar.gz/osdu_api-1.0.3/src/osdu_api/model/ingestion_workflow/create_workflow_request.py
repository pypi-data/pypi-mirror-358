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
from osdu_api.model.base import Base

class CreateWorkflowRequest(Base):
    """
    Request body to ingestion workflow's create workflow endpoint
    """
    
    def __init__(self, description: str, registration_instructions: dict, workflow_name: str):
        self.description = description
        self.registrationInstructions = registration_instructions
        self.workflowName = workflow_name
