from osdu_api.model.ingestion_workflow.create_workflow_request import CreateWorkflowRequest
from osdu_api.model.ingestion_workflow.trigger_workflow_request import TriggerWorkflowRequest
from osdu_api.model.ingestion_workflow.update_workflow_run_request import UpdateWorkflowRunRequest
from osdu_api.clients.ingestion_workflow.ingestion_workflow_client import IngestionWorkflowClient

ingestion_client = IngestionWorkflowClient()

create_workflow_request = CreateWorkflowRequest("test description", {}, "my_second_dag")
response = ingestion_client.create_workflow(create_workflow_request)
print(">>>>>>>")
print(response.status_code)
print(response.content)
if response.status_code == 200 or response.status_code == 409:
    response = ingestion_client.get_workflow("my_second_dag")
    print(">>>>>>>")
    print(response.status_code)
    print(response.content)

response = ingestion_client.get_all_workflows_in_partition()
print(">>>>>>>")
print(response.status_code)
print(response.content)

response = ingestion_client.delete_workflow("my_second_dag")
print(">>>>>>>")
print(response.status_code)
print(response.content)


create_workflow_request = CreateWorkflowRequest("test description", {}, "my_second_dag")
response = ingestion_client.create_workflow(create_workflow_request)
if response.status_code == 200 or response.status_code == 409:
    trigger_workflow_request = TriggerWorkflowRequest({})
    response = ingestion_client.trigger_workflow(trigger_workflow_request, "my_second_dag")
    print(">>>>>>>")
    print(response.status_code)
    print(response.content)
    response = ingestion_client.get_workflow_runs("my_second_dag")
    print(">>>>>>>")
    print(response.status_code)
    print(response.content)
