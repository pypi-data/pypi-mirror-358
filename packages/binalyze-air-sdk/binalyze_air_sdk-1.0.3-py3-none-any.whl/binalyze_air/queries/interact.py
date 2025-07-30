"""
Interact queries for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any

from ..base import Query
from ..models.interact import (
    ShellInteraction, LibraryFile, LibraryFileFilter, 
    InteractCommand, CommandMessage, FileExistsResponse
)
from ..http_client import HTTPClient


class GetShellInteractionQuery(Query[ShellInteraction]):
    """Query to get a specific shell interaction."""
    
    def __init__(self, http_client: HTTPClient, interaction_id: str):
        self.http_client = http_client
        self.interaction_id = interaction_id
    
    def execute(self) -> ShellInteraction:
        """Execute the query to get a specific shell interaction."""
        response = self.http_client.get(f"interact/shell/{self.interaction_id}")
        
        if response.get("success"):
            result_data = response.get("result", {})
            # Use Pydantic parsing with proper field aliasing
            return ShellInteraction.model_validate(result_data)
        
        raise Exception(f"Shell interaction not found: {self.interaction_id}")


# LIBRARY FILE QUERIES

class ListLibraryFilesQuery(Query[List[LibraryFile]]):
    """Query to list library files."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[LibraryFileFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or LibraryFileFilter()
    
    def execute(self) -> List[LibraryFile]:
        """Execute the query to get library files."""
        params = self.filter_params.to_params()
        response = self.http_client.get("interact/library/files", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing
        files = []
        for item in entities:
            files.append(LibraryFile.model_validate(item))
        
        return files


class DownloadLibraryFileQuery(Query[bytes]):
    """Query to download a library file."""
    
    def __init__(self, http_client: HTTPClient, file_id: str):
        self.http_client = http_client
        self.file_id = file_id
    
    def execute(self) -> bytes:
        """Execute the query to download a library file."""
        params = {"fileId": self.file_id}
        response = self.http_client.get("interact/library/download", params=params)
        
        # Return file content as bytes
        if isinstance(response, bytes):
            return response
        
        # If response is JSON, convert to bytes
        return str(response).encode('utf-8')


class CheckFileExistsQuery(Query[bool]):
    """Query to check if a file exists in library."""
    
    def __init__(self, http_client: HTTPClient, name: str, sha256: Optional[str] = None, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.name = name
        self.sha256 = sha256
        self.organization_ids = organization_ids or [0]  # Default to organization 0
    
    def execute(self) -> bool:
        """Execute the query to check if file exists."""
        import json
        params = {"name": self.name}
        if self.sha256:
            params["sha256"] = self.sha256
        
        # API requires organizationIds as JSON string array
        params["organizationIds"] = json.dumps(self.organization_ids)
        
        response = self.http_client.get("interact/library/check", params=params)
        
        # API returns simple boolean response, not object
        return response.get("result", False)


# SHELL SESSION QUERIES

class GetCommandMessageQuery(Query[CommandMessage]):
    """Query to get a command message from a session."""
    
    def __init__(self, http_client: HTTPClient, session_id: str, message_id: str):
        self.http_client = http_client
        self.session_id = session_id
        self.message_id = message_id
    
    def execute(self) -> CommandMessage:
        """Execute the query to get a command message."""
        response = self.http_client.get(
            f"interact/shell/sessions/{self.session_id}/messages/{self.message_id}"
        )
        
        result_data = response.get("result", {})
        return CommandMessage.model_validate(result_data)


class ListInteractCommandsQuery(Query[List[InteractCommand]]):
    """Query to list available interact commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> List[InteractCommand]:
        """Execute the query to get available interact commands."""
        response = self.http_client.get("interact/commands")
        
        commands_data = response.get("result", [])
        
        # Use Pydantic parsing with proper field aliasing
        commands = []
        for item in commands_data:
            commands.append(InteractCommand.model_validate(item))
        
        return commands 