"""
Interact API models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel


class SendToLocation(str, Enum):
    """Send to location options."""
    USER_LOCAL = "user-local"
    REPOSITORY = "repository"
    EVIDENCE_REPOSITORY = "evidence-repository"


class TaskConfigChoice(str, Enum):
    """Task configuration choice options."""
    USE_POLICY = "use-policy"
    USE_CUSTOM_OPTIONS = "use-custom-options"


class SendToConfig(AIRBaseModel):
    """Send to configuration model."""
    
    location: SendToLocation
    repository_id: Optional[str] = Field(default=None, alias="repositoryId")
    evidence_repository_id: Optional[str] = Field(default=None, alias="evidenceRepositoryId")


class BandwidthConfig(AIRBaseModel):
    """Bandwidth configuration model."""
    
    limit: Optional[int] = None


class DiskSpaceConfig(AIRBaseModel):
    """Disk space configuration model."""
    
    reserve: Optional[int] = None


class TaskConfig(AIRBaseModel):
    """Task configuration model."""
    
    choice: TaskConfigChoice
    send_to: Optional[SendToConfig] = Field(default=None, alias="sendTo")
    bandwidth: Optional[BandwidthConfig] = None
    disk_space: Optional[DiskSpaceConfig] = Field(default=None, alias="diskSpace")


class AssignInteractiveShellTaskRequest(AIRBaseModel):
    """Request model for assigning interactive shell task."""
    
    asset_id: str = Field(alias="assetId")
    case_id: str = Field(alias="caseId")
    task_config: TaskConfig = Field(alias="taskConfig")


class InteractiveShellTaskResponse(AIRBaseModel):
    """Response model for interactive shell task assignment."""
    
    session_id: str = Field(alias="sessionId")
    idle_timeout: int = Field(alias="idleTimeout")
    config: TaskConfig


# NEW MODELS FOR INTERACT API

class LibraryFile(AIRBaseModel):
    """Library file model."""
    
    id: str = Field(alias="_id")
    name: str
    organization_ids: List[int] = Field(alias="organizationIds")
    size: int
    sha256: str
    uploaded_by: str = Field(alias="uploadedBy")
    uploaded_at: datetime = Field(alias="uploadedAt")
    last_used_at: Optional[datetime] = Field(default=None, alias="lastUsedAt")
    last_used_by: Optional[str] = Field(default=None, alias="lastUsedBy")


class LibraryFileFilter(AIRBaseModel):
    """Library file filter model."""
    
    search_term: Optional[str] = Field(default=None, alias="searchTerm")
    organization_ids: Optional[List[int]] = Field(default=None, alias="organizationIds")
    name: Optional[str] = None
    uploaded_by: Optional[str] = Field(default=None, alias="uploadedBy")
    uploaded_at: Optional[str] = Field(default=None, alias="uploadedAt")
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to query parameters."""
        params = {}
        if self.search_term:
            params["filter[searchTerm]"] = self.search_term
        if self.organization_ids:
            params["filter[organizationIds]"] = ",".join([str(x) for x in self.organization_ids])
        if self.name:
            params["filter[name]"] = self.name
        if self.uploaded_by:
            params["filter[uploadedBy]"] = self.uploaded_by
        if self.uploaded_at:
            params["filter[uploadedAt]"] = self.uploaded_at
        return params


class ExecuteCommandRequest(AIRBaseModel):
    """Request model for executing interact command."""
    
    command: str
    accept: Optional[str] = "json"  # json or text


class ExecuteCommandResponse(AIRBaseModel):
    """Response model for execute command."""
    
    message_id: str = Field(alias="messageId")
    session: Dict[str, str]
    body: str
    cwd: str
    exit_code: int = Field(alias="exitCode")


class InteractCommandOption(AIRBaseModel):
    """Interact command option model."""
    
    name: str
    abbreviations: List[str]
    effect: str
    required: bool


class InteractCommand(AIRBaseModel):
    """Interact command model."""
    
    command: List[str]
    description: str
    options: List[InteractCommandOption]
    privilege: str
    usage: List[str]


class SessionInfo(AIRBaseModel):
    """Session information model."""
    
    id: str


class CommandMessage(AIRBaseModel):
    """Command message model."""
    
    message_id: str = Field(alias="messageId")
    session: SessionInfo
    body: str
    cwd: str
    exit_code: int = Field(alias="exitCode")


class InterruptCommandRequest(AIRBaseModel):
    """Request model for interrupting command."""
    pass  # Empty request body


class CloseSessionRequest(AIRBaseModel):
    """Request model for closing session."""
    pass  # Empty request body


class UploadFileRequest(AIRBaseModel):
    """Request model for uploading file to library."""
    
    file_content: bytes
    filename: str
    organization_ids: Optional[List[int]] = Field(default=None, alias="organizationIds")


class DeleteFileRequest(AIRBaseModel):
    """Request model for deleting file from library."""
    
    file_id: str = Field(alias="fileId")


class CheckFileExistsRequest(AIRBaseModel):
    """Request model for checking if file exists."""
    
    filename: str
    sha256: Optional[str] = None


class FileExistsResponse(AIRBaseModel):
    """Response model for file exists check."""
    
    exists: bool
    file_id: Optional[str] = Field(default=None, alias="fileId")


# Legacy models for backward compatibility (deprecated)
class InteractionType(str, Enum):
    """Interaction types."""
    SHELL = "shell"
    POWERSHELL = "powershell"
    CMD = "cmd"
    BASH = "bash"


class InteractionStatus(str, Enum):
    """Interaction status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ShellInteraction(AIRBaseModel):
    """Shell interaction model (legacy)."""
    
    id: str
    task_id: str
    endpoint_id: str
    endpoint_name: str
    interaction_type: InteractionType
    command: str
    output: Optional[str] = None
    error_output: Optional[str] = None
    exit_code: Optional[int] = None
    status: InteractionStatus = InteractionStatus.PENDING
    timeout: int = 300  # seconds
    organization_id: int
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None  # seconds
    environment_variables: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None


class AssignShellTaskRequest(AIRBaseModel):
    """Request model for assigning shell interaction tasks (legacy)."""
    
    endpoint_ids: List[str]
    command: str
    interaction_type: InteractionType = InteractionType.SHELL
    timeout: Optional[int] = 300
    organization_ids: Optional[List[int]] = None
    case_id: Optional[str] = None
    environment_variables: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None
    description: Optional[str] = None


class ShellTaskResponse(AIRBaseModel):
    """Response model for shell task assignment (legacy)."""
    
    task_id: str
    endpoint_interactions: List[ShellInteraction]
    success_count: int
    failure_count: int
    total_count: int
    errors: Optional[List[Dict[str, Any]]] = None 