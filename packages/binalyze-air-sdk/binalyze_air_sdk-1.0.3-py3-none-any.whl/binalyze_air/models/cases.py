"""
Case-related data models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime
from enum import Enum
from pydantic import Field, field_validator

from ..base import AIRBaseModel, Filter


class CaseStatus(str, Enum):
    """Case status."""
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CaseNote(AIRBaseModel):
    """Case note model."""
    
    id: str = Field(alias="_id")
    case_id: str = Field(alias="caseId")
    value: str
    written_at: Optional[datetime] = Field(default=None, alias="writtenAt")
    written_by: Optional[str] = Field(default=None, alias="writtenBy")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")


class Case(AIRBaseModel):
    """Case model."""
    
    id: str = Field(alias="_id")
    name: str
    status: CaseStatus = CaseStatus.OPEN
    owner_user_id: str = Field(alias="ownerUserId")
    owner_user: Optional[Any] = Field(default=None, alias="ownerUser")
    assigned_user_ids: List[str] = Field(default=[], alias="assignedUserIds")
    assigned_users: List[Any] = Field(default=[], alias="assignedUsers")
    visibility: str
    organization_id: int = Field(default=0, alias="organizationId")
    notes: List[Any] = []
    endpoint_count: int = Field(default=0, alias="endpointCount")
    task_count: int = Field(default=0, alias="taskCount")
    acquisition_task_count: int = Field(default=0, alias="acquisitionTaskCount")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    closed_at: Optional[datetime] = Field(default=None, alias="closedAt")
    archived_at: Optional[datetime] = Field(default=None, alias="archivedAt")
    # Optional fields that may not be in all responses
    source: Optional[str] = None
    started_on: Optional[datetime] = Field(default=None, alias="startedOn")
    total_days: int = Field(default=0, alias="totalDays")
    total_endpoints: int = Field(default=0, alias="totalEndpoints")
    closed_on: Optional[datetime] = Field(default=None, alias="closedOn")


class CaseActivity(AIRBaseModel):
    """Case activity model."""
    
    id: Optional[str] = Field(default=None, alias="_id")
    case_id: Optional[str] = Field(default=None, alias="caseId")
    user_id: Optional[str] = Field(default=None, alias="userId")
    user: Optional[Any] = None
    activity_type: Optional[str] = Field(default=None, alias="activityType")
    description: Optional[str] = None
    details: Dict[str, Any] = {}
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    # Legacy fields that may still exist
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    type: Optional[str] = None
    performed_by: Optional[str] = Field(default=None, alias="performedBy")
    data: Optional[Any] = None
    organization_ids: List[int] = Field(default=[], alias="organizationIds")


class CaseEndpoint(AIRBaseModel):
    """Case endpoint model."""
    
    platform: str
    tags: List[str] = []
    isolation_status: str = Field(alias="isolationStatus")
    id: str = Field(alias="_id")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    organization_id: int = Field(default=0, alias="organizationId")
    ip_address: Optional[str] = Field(default=None, alias="ipAddress")
    name: str
    group_id: Optional[str] = Field(default=None, alias="groupId")
    group_full_path: Optional[str] = Field(default=None, alias="groupFullPath")
    os: str
    is_server: bool = Field(default=False, alias="isServer")
    is_managed: bool = Field(default=True, alias="isManaged")
    last_seen: Optional[datetime] = Field(default=None, alias="lastSeen")
    version: Optional[str] = None
    version_no: Optional[int] = Field(default=None, alias="versionNo")
    registered_at: Optional[datetime] = Field(default=None, alias="registeredAt")
    security_token: Optional[str] = Field(default=None, alias="securityToken")
    online_status: str = Field(alias="onlineStatus")
    issues: List[str] = []
    label: Optional[str] = None
    waiting_for_version_update_fix: bool = Field(default=False, alias="waitingForVersionUpdateFix")


class CaseTask(AIRBaseModel):
    """Case task model."""
    
    id: str = Field(alias="_id")
    task_id: str = Field(alias="taskId")
    name: str
    type: str
    endpoint_id: str = Field(alias="endpointId")
    endpoint_name: str = Field(alias="endpointName")
    organization_id: int = Field(default=0, alias="organizationId")
    status: str
    recurrence: Optional[str] = None
    progress: int = 0
    duration: Optional[int] = None
    case_ids: List[str] = Field(default=[], alias="caseIds")
    is_comparable: bool = Field(default=False, alias="isComparable")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    response: Optional[Any] = None


class UserProfile(AIRBaseModel):
    """User profile model."""
    
    name: str
    surname: str
    department: str


class Role(AIRBaseModel):
    """User role model."""
    
    id: str = Field(alias="_id")
    name: str
    created_by: str = Field(alias="createdBy")
    tag: str
    privilege_types: List[str] = Field(default=[], alias="privilegeTypes")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")


class User(AIRBaseModel):
    """User model."""
    
    id: str = Field(alias="_id")
    email: str
    username: str
    organization_ids: Union[List[int], str] = Field(default=[], alias="organizationIds")
    strategy: str
    profile: UserProfile
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    roles: List[Role] = []
    
    @field_validator('organization_ids', mode='before')
    @classmethod
    def parse_organization_ids(cls, v):
        """Handle organizationIds which can be a list of ints or the string 'ALL'."""
        if isinstance(v, str):
            # Handle the "ALL" case - return as is for now
            return v
        elif isinstance(v, list):
            # Ensure all items are integers
            return [int(item) if not isinstance(item, int) else item for item in v]
        else:
            # Default to empty list for other cases
            return []


class CaseFilter(Filter):
    """Filter for case queries."""
    
    name: Optional[str] = None
    status: Optional[List[CaseStatus]] = None
    owner_user_id: Optional[str] = None
    assigned_user_ids: Optional[List[str]] = None
    visibility: Optional[str] = None
    source: Optional[str] = None


class CaseActivityFilter(Filter):
    """Filter for case activity queries."""
    
    performed_by: Optional[List[str]] = None  # User IDs who performed the activities
    types: Optional[List[str]] = None  # Activity types to filter
    search_term: Optional[str] = None  # Search term for activity descriptions
    occurred_at: Optional[str] = None  # Date range filter
    page_number: Optional[int] = Field(default=1, ge=1)  # Page number (min: 1)
    page_size: Optional[int] = Field(default=10, ge=1)  # Page size (min: 1)
    sort_by: Optional[str] = Field(default="createdAt")  # Sort field
    sort_type: Optional[Literal["ASC", "DESC"]] = Field(default="ASC")  # Sort direction


class CaseEndpointFilter(Filter):
    """Filter for case endpoint queries."""
    
    organization_ids: Optional[List[int]] = None  # Required organization IDs
    search_term: Optional[str] = None  # Search term for endpoint names
    name: Optional[str] = None  # Endpoint name filter
    ip_address: Optional[str] = None  # IP address filter
    group_id: Optional[str] = None  # Group ID filter
    group_full_path: Optional[str] = None  # Group full path filter
    label: Optional[str] = None  # Label filter
    last_seen: Optional[str] = None  # Last seen date range (e.g., "2023-03-06T21:00:00.000Z,2023-03-24T21:00:00.000Z")
    managed_status: Optional[List[str]] = None  # Managed status filter (unmanaged, managed, off-network)
    isolation_status: Optional[List[str]] = None  # Isolation status filter (isolating, isolated, unisolating, unisolated)
    platform: Optional[List[str]] = None  # Platform filter (windows, linux, darwin)
    issue: Optional[List[str]] = None  # Issue filter (unreachable, old-version, update-required)
    online_status: Optional[List[str]] = None  # Online status filter (online, offline)
    tags: Optional[List[str]] = None  # Tags filter
    version: Optional[str] = None  # Version filter
    policy: Optional[str] = None  # Policy filter
    included_endpoint_ids: Optional[List[str]] = None  # Included endpoint IDs
    excluded_endpoint_ids: Optional[List[str]] = None  # Excluded endpoint IDs
    aws_regions: Optional[List[str]] = None  # AWS regions filter
    azure_regions: Optional[List[str]] = None  # Azure regions filter
    page_number: Optional[int] = Field(default=1, ge=1)  # Page number (min: 1)
    page_size: Optional[int] = Field(default=10, ge=1)  # Page size (min: 1)
    sort_by: Optional[str] = Field(default="createdAt")  # Sort field
    sort_type: Optional[Literal["ASC", "DESC"]] = Field(default="ASC")  # Sort direction


class CaseTaskFilter(Filter):
    """Filter for case task queries."""
    
    organization_ids: Optional[List[int]] = None  # Required organization IDs
    search_term: Optional[str] = None  # Search term for task names
    name: Optional[str] = None  # Task name filter
    endpoint_ids: Optional[List[str]] = None  # Endpoint IDs filter
    execution_type: Optional[str] = None  # Execution type filter (instant, scheduled)
    status: Optional[str] = None  # Status filter (scheduled, assigned, processing, completed, failed, expired, cancelled, compressing, uploading, analyzing, partially-completed)
    type: Optional[str] = None  # Task type filter (acquisition, offline-acquisition, triage, offline-triage, investigation, interact-shell, baseline-comparison, baseline-acquisition, acquire-image)
    asset_names: Optional[str] = None  # Comma separated asset names
    started_by: Optional[str] = None  # Started by user filter
    page_number: Optional[int] = Field(default=1, ge=1)  # Page number (min: 1)
    page_size: Optional[int] = Field(default=10, ge=1)  # Page size (min: 1)
    sort_by: Optional[str] = Field(default="createdAt")  # Sort field
    sort_type: Optional[Literal["ASC", "DESC"]] = Field(default="ASC")  # Sort direction


class CaseUserFilter(Filter):
    """Filter for case user queries."""
    
    organization_ids: Optional[List[int]] = None  # Required organization IDs
    search_term: Optional[str] = None  # Search term for user filtering
    page_number: Optional[int] = Field(default=1, ge=1)  # Page number (min: 1)
    page_size: Optional[int] = Field(default=10, ge=1)  # Page size (min: 1)
    sort_by: Optional[str] = Field(default="createdAt")  # Sort field
    sort_type: Optional[Literal["ASC", "DESC"]] = Field(default="ASC")  # Sort direction


class CreateCaseRequest(AIRBaseModel):
    """Request model for creating a case."""
    
    organization_id: int = 0
    name: str
    owner_user_id: str
    visibility: str
    assigned_user_ids: List[str] = []


class UpdateCaseRequest(AIRBaseModel):
    """Request model for updating a case."""
    
    name: Optional[str] = None
    owner_user_id: Optional[str] = None
    visibility: Optional[str] = None
    assigned_user_ids: Optional[List[str]] = None
    status: Optional[CaseStatus] = None
    notes: Optional[List[Any]] = None 