"""
Relay Server commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any

from ..base import Command
from ..models.relay_server import (
    RebootTaskRequest, ShutdownTaskRequest, LogRetrievalTaskRequest, VersionUpdateTaskRequest,
    UpdateTagsRequest, UpdateLabelRequest, UpdateAddressRequest
)
from ..http_client import HTTPClient


class AssignRebootTaskCommand(Command[Dict[str, Any]]):
    """Command to assign reboot task to relay server."""
    
    def __init__(self, http_client: HTTPClient, relay_server_id: str, task_request: RebootTaskRequest):
        self.http_client = http_client
        self.relay_server_id = relay_server_id
        self.task_request = task_request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to assign reboot task."""
        response = self.http_client.post(
            f'/relay-servers/{self.relay_server_id}/tasks/reboot',
            json_data=self.task_request.model_dump(exclude_none=True)
        )
        return response


class AssignShutdownTaskCommand(Command[Dict[str, Any]]):
    """Command to assign shutdown task to relay server."""
    
    def __init__(self, http_client: HTTPClient, relay_server_id: str, task_request: ShutdownTaskRequest):
        self.http_client = http_client
        self.relay_server_id = relay_server_id
        self.task_request = task_request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to assign shutdown task."""
        response = self.http_client.post(
            f'/relay-servers/{self.relay_server_id}/tasks/shutdown',
            json_data=self.task_request.model_dump(exclude_none=True)
        )
        return response


class AssignLogRetrievalTaskCommand(Command[Dict[str, Any]]):
    """Command to assign log retrieval task to relay server."""
    
    def __init__(self, http_client: HTTPClient, relay_server_id: str, task_request: LogRetrievalTaskRequest):
        self.http_client = http_client
        self.relay_server_id = relay_server_id
        self.task_request = task_request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to assign log retrieval task."""
        response = self.http_client.post(
            f'/relay-servers/{self.relay_server_id}/tasks/log-retrieval',
            json_data=self.task_request.model_dump(exclude_none=True)
        )
        return response


class AssignVersionUpdateTaskCommand(Command[Dict[str, Any]]):
    """Command to assign version update task to relay server."""
    
    def __init__(self, http_client: HTTPClient, relay_server_id: str, task_request: VersionUpdateTaskRequest):
        self.http_client = http_client
        self.relay_server_id = relay_server_id
        self.task_request = task_request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to assign version update task."""
        response = self.http_client.post(
            f'/relay-servers/{self.relay_server_id}/tasks/version-update',
            json_data=self.task_request.model_dump(exclude_none=True)
        )
        return response


class DeleteRelayServerCommand(Command[Dict[str, Any]]):
    """Command to delete a relay server."""
    
    def __init__(self, http_client: HTTPClient, server_id: str):
        self.http_client = http_client
        self.server_id = server_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to delete a relay server."""
        response = self.http_client.delete(f'/relay-servers/remove', params={'id': self.server_id})
        return response


class UpdateTagsCommand(Command[Dict[str, Any]]):
    """Command to update tags for a relay server."""
    
    def __init__(self, http_client: HTTPClient, relay_server_id: str, tags_request: UpdateTagsRequest):
        self.http_client = http_client
        self.relay_server_id = relay_server_id
        self.tags_request = tags_request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to update tags."""
        response = self.http_client.patch(
            f'/relay-servers/{self.relay_server_id}/tag',
            json_data=self.tags_request.model_dump(exclude_none=True)
        )
        return response


class UpdateLabelCommand(Command[Dict[str, Any]]):
    """Command to update label for a relay server."""
    
    def __init__(self, http_client: HTTPClient, relay_server_id: str, label_request: UpdateLabelRequest):
        self.http_client = http_client
        self.relay_server_id = relay_server_id
        self.label_request = label_request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to update label."""
        response = self.http_client.patch(
            f'/relay-servers/{self.relay_server_id}/label',
            json_data=self.label_request.model_dump(exclude_none=True)
        )
        return response


class UpdateAddressCommand(Command[Dict[str, Any]]):
    """Command to update address for a relay server."""
    
    def __init__(self, http_client: HTTPClient, relay_server_id: str, address_request: UpdateAddressRequest):
        self.http_client = http_client
        self.relay_server_id = relay_server_id
        self.address_request = address_request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to update address."""
        response = self.http_client.patch(
            f'/relay-servers/{self.relay_server_id}/address',
            json_data=self.address_request.model_dump(exclude_none=True)
        )
        return response 