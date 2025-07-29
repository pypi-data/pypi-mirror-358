#  Copyright 2022 Google LLC
#  Copyright 2022 EPAM Systems
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from osdu_api.providers.baremetal.partition_info_baremetal import PartitionInfoBaremetal

# Example response from partition service:
# {
#        ...
#         "obm.minio.accessKey": {
#         "sensitive": False,
#         "value": "<access>"
#     },
#         "obm.minio.secretKey": {
#         "sensitive": True,
#         "value": "<secret>"
#     },
#         "obm.minio.endpoint": {
#         "sensitive": True,
#         "value": "<url>"
#     },
#      ...
# }

def convert(content: dict) -> PartitionInfoBaremetal:
    """Convert response from partition service to python object

    Args:
        content (dict): json response from partition service

    Returns:
        PartitionInfoBaremetal: has attributes defining partition info
    """
    return PartitionInfoBaremetal(
        content["obm.minio.accessKey"]["value"],
        content["obm.minio.secretKey"]["value"],
        content["obm.minio.endpoint"]["value"]
    )
    
