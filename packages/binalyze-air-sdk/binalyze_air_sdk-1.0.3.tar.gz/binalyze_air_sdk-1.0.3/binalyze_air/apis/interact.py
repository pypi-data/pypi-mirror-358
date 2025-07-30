"""
Interact API for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any, Union

from ..http_client import HTTPClient
from ..models.interact import (
    ShellInteraction, AssignInteractiveShellTaskRequest, InteractiveShellTaskResponse,
    LibraryFile, LibraryFileFilter, ExecuteCommandRequest, ExecuteCommandResponse,
    InteractCommand, CommandMessage
)
from ..queries.interact import (
    GetShellInteractionQuery, ListLibraryFilesQuery, DownloadLibraryFileQuery,
    CheckFileExistsQuery, GetCommandMessageQuery, ListInteractCommandsQuery
)
from ..commands.interact import (
    AssignInteractiveShellTaskCommand, UploadFileToLibraryCommand, DeleteFileFromLibraryCommand,
    ExecuteCommandCommand, ExecuteAsyncCommandCommand, InterruptCommandCommand, CloseSessionCommand
)


class InteractAPI:
    """Interact API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # ========================================
    # LIBRARY FILE OPERATIONS (5 endpoints)
    # ========================================
    
    # QUERIES (Read operations)
    def list_library_files(self, filter_params: Optional[LibraryFileFilter] = None) -> List[LibraryFile]:
        """List files in the interact library."""
        query = ListLibraryFilesQuery(self.http_client, filter_params)
        return query.execute()
    
    def download_library_file(self, file_id: str) -> bytes:
        """Download a file from the interact library."""
        query = DownloadLibraryFileQuery(self.http_client, file_id)
        return query.execute()
    
    def check_file_exists(self, filename: str, sha256: Optional[str] = None, organization_ids: Optional[List[int]] = None) -> bool:
        """Check if a file exists in the interact library."""
        query = CheckFileExistsQuery(self.http_client, filename, sha256, organization_ids)
        return query.execute()
    
    # COMMANDS (Write operations)
    def upload_file_to_library(self, file_content: bytes, filename: str, organization_ids: Optional[List[int]] = None) -> Optional[LibraryFile]:
        """Upload a file to the interact library."""
        command = UploadFileToLibraryCommand(self.http_client, file_content, filename, organization_ids)
        return command.execute()
    
    def delete_file_from_library(self, file_id: str) -> Dict[str, Any]:
        """Delete a file from the interact library."""
        command = DeleteFileFromLibraryCommand(self.http_client, file_id)
        return command.execute()
    
    # ========================================
    # SHELL SESSION OPERATIONS (6 endpoints)
    # ========================================
    
    # QUERIES (Read operations)
    def get_command_message(self, session_id: str, message_id: str) -> CommandMessage:
        """Get a command message from a shell session."""
        query = GetCommandMessageQuery(self.http_client, session_id, message_id)
        return query.execute()
    
    def list_interact_commands(self) -> List[InteractCommand]:
        """List available interact commands."""
        query = ListInteractCommandsQuery(self.http_client)
        return query.execute()
    
    # COMMANDS (Write operations)
    def assign_interactive_shell_task(self, request: Union[AssignInteractiveShellTaskRequest, Dict[str, Any]]) -> InteractiveShellTaskResponse:
        """Assign an interactive shell task to an asset."""
        command = AssignInteractiveShellTaskCommand(self.http_client, request)
        return command.execute()
    
    def execute_command(self, session_id: str, request: Union[ExecuteCommandRequest, Dict[str, Any]]) -> ExecuteCommandResponse:
        """Execute a command in a shell session."""
        command = ExecuteCommandCommand(self.http_client, session_id, request)
        return command.execute()
    
    def execute_async_command(self, session_id: str, request: Union[ExecuteCommandRequest, Dict[str, Any]]) -> ExecuteCommandResponse:
        """Execute an async command in a shell session."""
        command = ExecuteAsyncCommandCommand(self.http_client, session_id, request)
        return command.execute()
    
    def interrupt_command(self, session_id: str, message_id: str) -> Dict[str, Any]:
        """Interrupt a running command in a shell session."""
        command = InterruptCommandCommand(self.http_client, session_id, message_id)
        return command.execute()
    
    def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close a shell session."""
        command = CloseSessionCommand(self.http_client, session_id)
        return command.execute()
    
    # ========================================
    # LEGACY METHODS (for backward compatibility)
    # ========================================
    
    def get_shell_interaction(self, interaction_id: str) -> ShellInteraction:
        """Get a specific shell interaction by ID (legacy)."""
        query = GetShellInteractionQuery(self.http_client, interaction_id)
        return query.execute()
    
    # ========================================
    # CONVENIENCE ALIASES
    # ========================================
    
    # Library aliases
    def list_files(self, filter_params: Optional[LibraryFileFilter] = None) -> List[LibraryFile]:
        """List files - alias for list_library_files."""
        return self.list_library_files(filter_params)
    
    def download_file(self, file_id: str) -> bytes:
        """Download file - alias for download_library_file."""
        return self.download_library_file(file_id)
    
    def upload_file(self, file_content: bytes, filename: str, organization_ids: Optional[List[int]] = None) -> Optional[LibraryFile]:
        """Upload file - alias for upload_file_to_library."""
        return self.upload_file_to_library(file_content, filename, organization_ids)
    
    def delete_file(self, file_id: str) -> Dict[str, Any]:
        """Delete file - alias for delete_file_from_library."""
        return self.delete_file_from_library(file_id)
    
    # Shell aliases
    def execute(self, session_id: str, command: str, accept: str = "json") -> ExecuteCommandResponse:
        """Execute command - convenience method."""
        request = ExecuteCommandRequest(command=command, accept=accept)
        return self.execute_command(session_id, request)
    
    def execute_async(self, session_id: str, command: str, accept: str = "json") -> ExecuteCommandResponse:
        """Execute async command - convenience method."""
        request = ExecuteCommandRequest(command=command, accept=accept)
        return self.execute_async_command(session_id, request)
    
    def get_commands(self) -> List[InteractCommand]:
        """Get commands - alias for list_interact_commands."""
        return self.list_interact_commands()
    
    def assign_shell_task(self, asset_id: str, case_id: str, task_config: Dict[str, Any]) -> InteractiveShellTaskResponse:
        """Assign shell task - convenience method."""
        request_data = {
            "assetId": asset_id,
            "caseId": case_id,
            "taskConfig": task_config
        }
        return self.assign_interactive_shell_task(request_data) 