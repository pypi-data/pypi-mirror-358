"""
Webhook Executions commands for the Binalyze AIR SDK.
"""

from ..base import Command
from ..models.webhook_executions import WebhookExecutionResponse, WebhookPostRequest
from ..http_client import HTTPClient
from typing import Dict, Any


class ExecuteWebhookGetCommand(Command[WebhookExecutionResponse]):
    """Command to execute webhook via GET request."""
    
    def __init__(self, http_client: HTTPClient, slug: str, data: str, token: str):
        self.http_client = http_client
        self.slug = slug
        self.data = data
        self.token = token
    
    def execute(self) -> WebhookExecutionResponse:
        """Execute the webhook GET command."""
        params = {'token': self.token}
        
        response = self.http_client.get(f'/api/webhook/{self.slug}/{self.data}', params=params)
        
        # Parse the response into our model
        return WebhookExecutionResponse(
            task_details_view_url=response.get('taskDetailsViewUrl', ''),
            task_details_data_url=response.get('taskDetailsDataUrl', ''),
            task_id=response.get('taskId', ''),
            status_code=response.get('statusCode', 200)
        )


class ExecuteWebhookPostCommand(Command[WebhookExecutionResponse]):
    """Command to execute webhook via POST request."""
    
    def __init__(self, http_client: HTTPClient, slug: str, token: str, request_data: WebhookPostRequest):
        self.http_client = http_client
        self.slug = slug
        self.token = token
        self.request_data = request_data
    
    def execute(self) -> WebhookExecutionResponse:
        """Execute the webhook POST command."""
        params = {'token': self.token}
        
        response = self.http_client.post(
            f'/api/webhook/{self.slug}',
            params=params,
            json_data=self.request_data.model_dump(exclude_none=True)
        )
        
        # Parse the response into our model
        return WebhookExecutionResponse(
            task_details_view_url=response.get('taskDetailsViewUrl', ''),
            task_details_data_url=response.get('taskDetailsDataUrl', ''),
            task_id=response.get('taskId', ''),
            status_code=response.get('statusCode', 200)
        )


# ---------------------------------------------------------------------------
# Retry Webhook Execution Command
# ---------------------------------------------------------------------------


class RetryWebhookExecutionCommand(Command[Dict[str, Any]]):
    """Command to retry a failed webhook execution."""

    def __init__(self, http_client: HTTPClient, execution_id: str):
        self.http_client = http_client
        self.execution_id = execution_id

    def execute(self) -> Dict[str, Any]:
        """Retry the webhook execution via POST."""
        return self.http_client.post(f"webhook-executions/{self.execution_id}/retry", json_data={}) 