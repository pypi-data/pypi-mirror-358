"""
Webhook Executions API for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any

from ..http_client import HTTPClient
from ..models.webhook_executions import WebhookExecutionResponse, WebhookPostRequest, TaskDetailsData
from ..queries.webhook_executions import GetTaskDetailsQuery
from ..commands.webhook_executions import ExecuteWebhookGetCommand, ExecuteWebhookPostCommand, RetryWebhookExecutionCommand


class WebhookExecutionsAPI:
    """Webhook Executions API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def get_task_details(self, slug: str, task_id: str, token: str) -> TaskDetailsData:
        """Get task details data for a webhook execution."""
        query = GetTaskDetailsQuery(self.http_client, slug, task_id, token)
        return query.execute()
    
    # COMMANDS (Write operations)
    def execute_webhook_get(self, slug: str, data: str, token: str) -> WebhookExecutionResponse:
        """Execute webhook via GET request."""
        command = ExecuteWebhookGetCommand(self.http_client, slug, data, token)
        return command.execute()
    
    def execute_webhook_post(self, slug: str, token: str, request_data: WebhookPostRequest) -> WebhookExecutionResponse:
        """Execute webhook via POST request."""
        command = ExecuteWebhookPostCommand(self.http_client, slug, token, request_data)
        return command.execute()
    
    def retry_execution(self, execution_id: str) -> Dict[str, Any]:
        """Retry a failed webhook execution."""
        command = RetryWebhookExecutionCommand(self.http_client, execution_id)
        return command.execute()
    
    # Convenience methods
    def execute_webhook_with_hostnames(self, slug: str, hostnames: list, token: str) -> WebhookExecutionResponse:
        """Execute webhook with comma-separated hostnames."""
        data = ",".join(hostnames)
        return self.execute_webhook_get(slug, data, token)
    
    def execute_webhook_with_ips(self, slug: str, ip_addresses: list, token: str) -> WebhookExecutionResponse:
        """Execute webhook with comma-separated IP addresses."""
        data = ",".join(ip_addresses)
        return self.execute_webhook_get(slug, data, token) 