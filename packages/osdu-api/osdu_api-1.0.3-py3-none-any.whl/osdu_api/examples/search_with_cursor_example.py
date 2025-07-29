from osdu_api.clients.search.search_client import SearchClient
from osdu_api.model.search.query_request import QueryRequest


search_client = SearchClient("osdu")
query_request = QueryRequest(kind='osdu:wks:*:*', query="*", cursor=None, limit=1000)
search_response = search_client.query_with_cursor(query_request, bearer_token=None)

print(search_response.status_code)
print("________________")
print(search_response.content)