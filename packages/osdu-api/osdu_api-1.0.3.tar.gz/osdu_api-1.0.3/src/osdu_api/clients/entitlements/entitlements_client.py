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
from osdu_api.model.entitlements.group import Group
from osdu_api.model.entitlements.group_member import GroupMember
from osdu_api.model.http_method import HttpMethod


class EntitlementsClient(BaseClient):
    """
    Holds the logic for interfacing with Entitlement's api
    """

    def __init__(
        self,
        entitlements_url: Optional[str] = None,
        config_manager: Optional[BaseConfigManager] = None,
        provider: Optional[str] = None,
        data_partition_id: Optional[str] = None,
        token_refresher: Optional[TokenRefresher] = None,
        logger=None,
        user_id: Optional[str] = None
    ):
        super().__init__(config_manager, provider, data_partition_id, token_refresher, logger,
                         user_id)
        self.entitlements_url = entitlements_url or self.config_manager.get('environment', 'entitlements_url')

    def get_groups_for_user(self, bearer_token=None):
        return self.make_request(method=HttpMethod.GET, url='{}{}'.format(self.entitlements_url, '/groups'), bearer_token=bearer_token)

    def get_groups_all(self, limit: int, group_type: str, bearer_token=None):
        """
        Fetches all groups with a specified type and limit.

        Args:
            limit (int): The maximum number of groups to retrieve.
            group_type (str): The type of groups to retrieve. Must be one of: "NONE", "DATA", "SERVICE", "USER".
            bearer_token (Optional[str]): The authentication token. Defaults to None.

        Returns:
            Response object from self.make_request.
        """
        params = {"type": group_type, "limit": limit}
        return self.make_request(
            method=HttpMethod.GET,
            url=f"{self.entitlements_url}/groups/all",
            params=params,
            bearer_token=bearer_token
        )

    def get_group_members(self, group_email: str, limit: int, role: str, bearer_token=None):
        params = {} # type: dict
        params['limit'] = limit
        params['role'] = role
        return self.make_request(method=HttpMethod.GET, url='{}{}{}{}'.format(self.entitlements_url, '/groups/', group_email, '/members'), params=params, bearer_token=bearer_token)

    def delete_group_member(self, group_email: str, member_email: str, bearer_token=None):
        return self.make_request(method=HttpMethod.DELETE, url='{}{}{}{}{}'.format(self.entitlements_url, '/groups/', group_email, '/members/', member_email), bearer_token=bearer_token)

    def create_group(self, group: Group, bearer_token=None):
        return self.make_request(method=HttpMethod.POST, url='{}{}'.format(self.entitlements_url, '/groups'),
            data=group.to_JSON(), bearer_token=bearer_token)

    def create_group_member(self, group_email:str, group_member: GroupMember, bearer_token=None):
        return self.make_request(method=HttpMethod.POST, url='{}{}{}{}'.format(self.entitlements_url, '/groups/', group_email, '/members'),
            data=group_member.to_JSON(), bearer_token=bearer_token)
