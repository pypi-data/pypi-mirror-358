"""
Policy-related data models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel, Filter, PaginatedResponse


class PolicyType(str, Enum):
    """Policy type."""
    ACQUISITION = "acquisition"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    CUSTOM = "custom"


class PolicyStatus(str, Enum):
    """Policy status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class PolicyCondition(AIRBaseModel):
    """Policy condition model based on API structure."""
    
    # For leaf conditions
    field: Optional[str] = None
    operator: Optional[str] = None
    value: Optional[Any] = None
    
    # For nested conditions (when this is a group)
    conditions: Optional[List['PolicyCondition']] = None


class PolicyAction(AIRBaseModel):
    """Policy action model."""
    
    type: str
    parameters: Dict[str, Any] = {}
    enabled: bool = True


class PolicyRule(AIRBaseModel):
    """Policy rule model."""
    
    id: str
    name: str
    description: Optional[str] = None
    conditions: List[PolicyCondition] = []
    actions: List[PolicyAction] = []
    enabled: bool = True
    priority: int = 0


class PolicyFilterStructure(AIRBaseModel):
    """Policy filter model based on API structure."""
    
    operator: str
    conditions: List[PolicyCondition]


class PolicyCpuSettings(AIRBaseModel):
    """Policy CPU settings."""
    
    limit: int


class PolicySaveToSettings(AIRBaseModel):
    """Policy save-to settings for a platform."""
    
    location: str
    path: Optional[str] = None
    repository_id: Optional[str] = Field(default=None, alias="repositoryId")
    use_most_free_volume: bool = Field(default=True, alias="useMostFreeVolume")
    volume: Optional[str] = None
    tmp: Optional[str] = None


class PolicySaveTo(AIRBaseModel):
    """Policy save-to settings for all platforms."""
    
    windows: Optional[PolicySaveToSettings] = None
    linux: Optional[PolicySaveToSettings] = None
    macos: Optional[PolicySaveToSettings] = None


class PolicyEncryption(AIRBaseModel):
    """Policy encryption settings."""
    
    enabled: bool
    password: Optional[str] = None


class PolicyCompression(AIRBaseModel):
    """Policy compression settings."""
    
    enabled: bool
    encryption: Optional[PolicyEncryption] = None


class PolicySendTo(AIRBaseModel):
    """Policy send-to settings."""
    
    location: str
    repository_id: Optional[str] = Field(default=None, alias="repositoryId")


class IsolationAllowedProcess(AIRBaseModel):
    """Isolation allowed process model - matches API response format."""
    
    platform: str  # e.g., "linux", "windows", "macos"
    process_path: str = Field(alias="processPath")  # e.g., "firefox", "/usr/bin/firefox"


class Policy(AIRBaseModel):
    """Policy model based on API response structure."""
    
    id: str = Field(alias="_id")
    name: str
    organization_ids: List[int] = Field(default=[], alias="organizationIds")
    default: Optional[bool] = None
    order: Optional[int] = None
    created_by: Optional[str] = Field(default=None, alias="createdBy")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    
    # Policy configuration
    filter: Optional[PolicyFilterStructure] = None
    cpu: Optional[PolicyCpuSettings] = None
    save_to: Optional[PolicySaveTo] = Field(default=None, alias="saveTo")
    send_to: Optional[PolicySendTo] = Field(default=None, alias="sendTo")
    compression: Optional[PolicyCompression] = None
    
    # Optional fields that may be present
    bandwidth: Optional[Dict[str, Any]] = None
    disk_space: Optional[Dict[str, Any]] = Field(default=None, alias="diskSpace")
    triage_local_drives_only: Optional[Dict[str, Any]] = Field(default=None, alias="triageLocalDrivesOnly")
    isolation_allowed_ips: Optional[List[str]] = Field(default=None, alias="isolationAllowedIps")
    isolation_allowed_processes: Optional[List[IsolationAllowedProcess]] = Field(default=None, alias="isolationAllowedProcesses")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Policy object to dictionary for JSON serialization."""
        return self.model_dump(exclude_none=True, by_alias=True)


class PolicyPriority(AIRBaseModel):
    """Policy priority update model."""
    
    id: str = Field(alias="_id")
    order: int


class PolicyMatchStats(AIRBaseModel):
    """Policy match statistics model."""
    
    total_matches: int = Field(alias="totalMatches")
    policy_matches: List[Dict[str, Any]] = Field(default=[], alias="policyMatches")


class PolicyAssignment(AIRBaseModel):
    """Policy assignment model."""
    
    id: str
    policy_id: str
    endpoint_id: str
    assigned_at: Optional[datetime] = None
    assigned_by: str
    status: str = "active"


class PolicyExecution(AIRBaseModel):
    """Policy execution result model."""
    
    id: str
    policy_id: str
    endpoint_id: str
    executed_at: Optional[datetime] = None
    status: str
    result: Dict[str, Any] = {}
    errors: List[str] = []
    duration: Optional[int] = None


class CreatePolicyRequest(AIRBaseModel):
    """Request model for creating a policy - matches API specification exactly."""
    
    name: str
    organizationIds: List[int]  # Use camelCase to match API
    filter: PolicyFilterStructure
    cpu: PolicyCpuSettings
    saveTo: PolicySaveTo  # Use camelCase to match API
    sendTo: PolicySendTo  # Use camelCase to match API
    compression: PolicyCompression
    
    # Optional fields
    bandwidth: Optional[Dict[str, Any]] = None
    diskSpace: Optional[Dict[str, Any]] = None  # Use camelCase
    triageLocalDrivesOnly: Optional[Dict[str, Any]] = None  # Use camelCase
    isolationAllowedIps: Optional[List[str]] = None  # Use camelCase
    isolationAllowedProcesses: Optional[List[IsolationAllowedProcess]] = None  # Use camelCase


class UpdatePolicyRequest(AIRBaseModel):
    """Request model for updating a policy - matches API specification exactly."""
    
    name: str  # Required by API
    organizationIds: List[int]  # Required by API - use camelCase
    filter: PolicyFilterStructure  # Required by API
    cpu: PolicyCpuSettings  # Required by API
    saveTo: PolicySaveTo  # Required by API - use camelCase
    sendTo: PolicySendTo  # Required by API - use camelCase
    compression: PolicyCompression  # Required by API
    
    # Optional fields that may be present
    bandwidth: Optional[Dict[str, Any]] = None
    diskSpace: Optional[Dict[str, Any]] = None  # Use camelCase
    triageLocalDrivesOnly: Optional[Dict[str, Any]] = None  # Use camelCase
    isolationAllowedIps: Optional[List[str]] = None  # Use camelCase
    isolationAllowedProcesses: Optional[List[IsolationAllowedProcess]] = None  # Use camelCase


class UpdatePoliciesPrioritiesRequest(AIRBaseModel):
    """Request model for updating policy priorities."""
    
    policies: List[PolicyPriority]


class PolicyFilter(Filter):
    """Filter for policy queries."""
    
    organization_ids: Optional[List[int]] = None
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to query parameters."""
        params = {}
        if self.organization_ids:
            params["filter[organizationIds]"] = ",".join([str(x) for x in self.organization_ids])
        return params


class PoliciesPaginatedResponse(PaginatedResponse[Policy]):
    """Paginated response for policies."""
    
    # Add field aliases for pagination fields
    total_entity_count: int = Field(alias="totalEntityCount")
    current_page: int = Field(alias="currentPage")
    page_size: int = Field(alias="pageSize")
    total_page_count: int = Field(alias="totalPageCount")


class AssignPolicyRequest(AIRBaseModel):
    """Request model for assigning policy to endpoints."""
    
    policy_id: str
    endpoint_ids: List[str] = []
    organization_ids: List[int] = []
    filter_params: Optional[Dict[str, Any]] = None 