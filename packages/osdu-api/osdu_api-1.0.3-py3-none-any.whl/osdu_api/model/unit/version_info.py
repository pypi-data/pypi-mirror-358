# Copyright 2023 Geosiris
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
from osdu_api.model.base import BaseNoNull
from typing import Optional, List
from osdu_api.model.unit.connected_outer_service import ConnectedOuterService


class VersionInfo(BaseNoNull):

    def __init__(
        self,
        artifact_id: Optional[str] = None,
        branch: Optional[str] = None,
        build_time: Optional[str] = None,
        commit_id: Optional[str] = None,
        commit_message: Optional[str] = None,
        connected_outer_services: Optional[List[ConnectedOuterService]] = None,
        group_id: Optional[str] = None,
        version: Optional[str] = None,
    ):
        self.artifactId = artifact_id
        self.branch = branch
        self.buildTime = build_time
        self.commitId = commit_id
        self.commitMessage = commit_message
        self.connectedOuterServices = connected_outer_services
        self.groupId = group_id
        self.version = version
