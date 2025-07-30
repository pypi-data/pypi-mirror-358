"""
Interact commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union, List, Optional
import json

from ..base import Command
from ..models.interact import (
    InteractiveShellTaskResponse, AssignInteractiveShellTaskRequest,
    ExecuteCommandRequest, ExecuteCommandResponse, LibraryFile,
    InterruptCommandRequest, CloseSessionRequest, FileExistsResponse
)
from ..http_client import HTTPClient


class AssignInteractiveShellTaskCommand(Command[InteractiveShellTaskResponse]):
    """Command to assign an interactive shell task."""
    
    def __init__(self, http_client: HTTPClient, request: Union[AssignInteractiveShellTaskRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> InteractiveShellTaskResponse:
        """Execute the command to assign an interactive shell task."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.post("interact/shell/assign-task", json_data=payload)
        
        if response.get("success"):
            result_data = response.get("result", {})
            # Use Pydantic parsing with proper field aliasing
            return InteractiveShellTaskResponse.model_validate(result_data)
        
        raise Exception(f"Failed to assign interactive shell task: {response.get('errors', [])}")


# LIBRARY FILE COMMANDS

class UploadFileToLibraryCommand(Command[Optional[LibraryFile]]):
    """Command to upload a file to the library."""
    
    def __init__(self, http_client: HTTPClient, file_content: bytes, filename: str, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.file_content = file_content
        self.filename = filename
        self.organization_ids = organization_ids
    
    def execute(self) -> Optional[LibraryFile]:
        """Execute the command to upload a file to the library."""
        # Prepare multipart form data
        files = {"file": (self.filename, self.file_content)}
        data = {}
        
        if self.organization_ids:
            # API expects organizationIds as JSON string array, not comma-separated
            data["organizationIds"] = json.dumps(self.organization_ids)
        
        response = self.http_client.upload_multipart("interact/library/upload", files=files, data=data)
        
        result_data = response.get("result")
        # Handle null result properly - API may return null on success
        if result_data is None:
            return None
        
        return LibraryFile.model_validate(result_data)


class DeleteFileFromLibraryCommand(Command[Dict[str, Any]]):
    """Command to delete a file from the library."""
    
    def __init__(self, http_client: HTTPClient, filename: str):
        self.http_client = http_client
        self.filename = filename
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to delete a file from the library."""
        params = {"filename": self.filename}
        response = self.http_client.delete("interact/library/delete", params=params)
        
        return response


# SHELL SESSION COMMANDS

class ExecuteCommandCommand(Command[ExecuteCommandResponse]):
    """Command to execute a command in a shell session."""
    
    def __init__(self, http_client: HTTPClient, session_id: str, request: Union[ExecuteCommandRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.session_id = session_id
        self.request = request
    
    def execute(self) -> ExecuteCommandResponse:
        """Execute the command in the shell session."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.post(
            f"interact/shell/sessions/{self.session_id}/execute-command",
            json_data=payload
        )
        
        result_data = response.get("result", {})
        return ExecuteCommandResponse.model_validate(result_data)


class ExecuteAsyncCommandCommand(Command[ExecuteCommandResponse]):
    """Command to execute an async command in a shell session."""
    
    def __init__(self, http_client: HTTPClient, session_id: str, request: Union[ExecuteCommandRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.session_id = session_id
        self.request = request
    
    def execute(self) -> ExecuteCommandResponse:
        """Execute the async command in the shell session."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.post(
            f"interact/shell/sessions/{self.session_id}/execute-async-command",
            json_data=payload
        )
        
        result_data = response.get("result", {})
        return ExecuteCommandResponse.model_validate(result_data)


class InterruptCommandCommand(Command[Dict[str, Any]]):
    """Command to interrupt a command in a shell session."""
    
    def __init__(self, http_client: HTTPClient, session_id: str, message_id: str):
        self.http_client = http_client
        self.session_id = session_id
        self.message_id = message_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to interrupt a running command."""
        response = self.http_client.post(
            f"interact/shell/sessions/{self.session_id}/messages/{self.message_id}/interrupt-command",
            json_data={}
        )
        
        return response


class CloseSessionCommand(Command[Dict[str, Any]]):
    """Command to close a shell session."""
    
    def __init__(self, http_client: HTTPClient, session_id: str):
        self.http_client = http_client
        self.session_id = session_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to close a shell session."""
        response = self.http_client.post(
            f"interact/shell/sessions/{self.session_id}/close",
            json_data={}
        )
        
        return response 