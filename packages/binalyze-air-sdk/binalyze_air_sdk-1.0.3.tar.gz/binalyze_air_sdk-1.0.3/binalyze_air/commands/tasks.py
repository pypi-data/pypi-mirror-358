"""
Task-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..http_client import HTTPClient
from ..models.tasks import CancelTaskByFilterRequest, GenerateOffNetworkZipPasswordRequest


class CancelTaskCommand(Command[Dict[str, Any]]):
    """Command to cancel a task."""
    
    def __init__(self, http_client: HTTPClient, task_id: str):
        self.http_client = http_client
        self.task_id = task_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the cancel task command."""
        return self.http_client.post(f"tasks/{self.task_id}/cancel", json_data={})


class CancelTaskAssignmentCommand(Command[Dict[str, Any]]):
    """Command to cancel a task assignment."""
    
    def __init__(self, http_client: HTTPClient, assignment_id: str):
        self.http_client = http_client
        self.assignment_id = assignment_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the cancel task assignment command."""
        return self.http_client.post(f"tasks/assignments/{self.assignment_id}/cancel", json_data={})


class DeleteTaskAssignmentCommand(Command[Dict[str, Any]]):
    """Command to delete a task assignment."""
    
    def __init__(self, http_client: HTTPClient, assignment_id: str):
        self.http_client = http_client
        self.assignment_id = assignment_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete task assignment command."""
        return self.http_client.delete(f"tasks/assignments/{self.assignment_id}")


class DeleteTaskCommand(Command[Dict[str, Any]]):
    """Command to delete a task."""
    
    def __init__(self, http_client: HTTPClient, task_id: str):
        self.http_client = http_client
        self.task_id = task_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete task command."""
        return self.http_client.delete(f"tasks/{self.task_id}")


class CancelTaskByFilterCommand(Command[Dict[str, Any]]):
    """Command to cancel tasks by filter."""
    
    def __init__(self, http_client: HTTPClient, request_data: Union[CancelTaskByFilterRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request_data = request_data
    
    def execute(self) -> Dict[str, Any]:
        """Execute the cancel task by filter command."""
        if isinstance(self.request_data, CancelTaskByFilterRequest):
            payload = self.request_data.model_dump(by_alias=True)
        else:
            payload = self.request_data
        
        # Ensure organizationIds are string values (API expects UUID strings)
        if 'organizationIds' in payload and isinstance(payload['organizationIds'], list):
            payload['organizationIds'] = [str(x) for x in payload['organizationIds']]
        
        return self.http_client.post("tasks/cancel-by-filter", json_data=payload)


class GenerateOffNetworkZipPasswordCommand(Command[Dict[str, Any]]):
    """Command to generate off-network zip password."""
    
    def __init__(self, http_client: HTTPClient, request_data: Union[GenerateOffNetworkZipPasswordRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request_data = request_data
    
    def execute(self) -> Dict[str, Any]:
        """Execute the generate off-network zip password command."""
        if isinstance(self.request_data, GenerateOffNetworkZipPasswordRequest):
            payload = self.request_data.model_dump(by_alias=True)
        else:
            payload = self.request_data
        
        return self.http_client.post("tasks/off-network/generate-zip-password", json_data=payload) 