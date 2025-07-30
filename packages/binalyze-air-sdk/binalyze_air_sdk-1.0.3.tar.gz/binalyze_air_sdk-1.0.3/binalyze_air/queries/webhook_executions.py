"""
Webhook Executions queries for the Binalyze AIR SDK.
"""

from ..base import Query
from ..models.webhook_executions import TaskDetailsData
from ..http_client import HTTPClient


class GetTaskDetailsQuery(Query[TaskDetailsData]):
    """Query to get task details data for a webhook execution."""
    
    def __init__(self, http_client: HTTPClient, slug: str, task_id: str, token: str):
        self.http_client = http_client
        self.slug = slug
        self.task_id = task_id
        self.token = token
    
    def execute(self) -> TaskDetailsData:
        """Execute the query to get task details."""
        params = {
            'token': self.token,
            'taskId': self.task_id
        }
        
        response = self.http_client.get(f'/api/webhook/{self.slug}/assignments', params=params)
        
        # The response structure may vary, so we'll create a TaskDetailsData object
        # with the available information
        result_data = response.get('result', response)
        
        return TaskDetailsData(
            task_id=self.task_id,
            task_name=result_data.get('taskName'),
            task_status=result_data.get('taskStatus'),
            task_type=result_data.get('taskType'),
            created_at=result_data.get('createdAt'),
            assignments=result_data.get('assignments', result_data)
        ) 