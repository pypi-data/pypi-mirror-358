

from osdu_api.clients.dataset.dataset_dms_client import DatasetDmsClient

dataset_dms_client = DatasetDmsClient("opendes")
retrieval_instructions_response = dataset_dms_client.get_retrieval_instructions(record_id="opendes:dataset--File.Generic:6358621f99b64dc9bab5aeb82b0ed3ab")
print(retrieval_instructions_response.content)
print(retrieval_instructions_response.status_code)