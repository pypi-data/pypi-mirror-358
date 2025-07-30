"""
Asset-related data models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel, Filter


class OnlineStatus(str, Enum):
    """Asset online status."""
    ONLINE = "online"
    OFFLINE = "offline"


class Platform(str, Enum):
    """Asset platform."""
    WINDOWS = "windows"
    LINUX = "linux"
    DARWIN = "darwin"  # Fixed: API uses 'darwin' not 'macos'
    AIX = "aix"
    DISK_IMAGE = "disk-image"  # API also returns this value


class IsolationStatus(str, Enum):
    """Asset isolation status."""
    ISOLATING = "isolating"
    ISOLATED = "isolated"
    UNISOLATING = "unisolating"
    UNISOLATED = "unisolated"


class ManagedStatus(str, Enum):
    """Asset managed status."""
    MANAGED = "managed"
    UNMANAGED = "unmanaged"
    OFF_NETWORK = "off-network"  # Added missing status


class IssueType(str, Enum):
    """Asset issue types."""
    UNREACHABLE = "unreachable"
    OLD_VERSION = "old-version"
    UPDATE_REQUIRED = "update-required"


class Tag(AIRBaseModel):
    """Tag model for assets."""
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    color: Optional[str] = None
    assignee_count: Optional[int] = Field(alias="assigneeCount", default=None)  # NEW
    organization_id: Optional[int] = Field(alias="organizationId", default=None)
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)  # NEW
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)  # NEW


class SystemResources(AIRBaseModel):
    """System resources information."""
    cpu: Optional[Dict[str, Any]] = None
    ram: Optional[Dict[str, Any]] = None
    disks: Optional[List[Dict[str, Any]]] = None


class NetworkInterface(AIRBaseModel):
    """Network interface information."""
    name: str
    mac_addr: Optional[str] = Field(alias="macAddr", default=None)
    ipv4_addrs: Optional[List[str]] = Field(alias="ipv4Addrs", default_factory=list)
    ipv6_addrs: Optional[List[str]] = Field(alias="ipv6Addrs", default_factory=list)


class AssetFeatures(AIRBaseModel):
    """Asset feature capabilities."""
    isolation_supported: Optional[bool] = Field(alias="isolationSupported", default=None)
    full_disk_access_enabled: Optional[bool] = Field(alias="fullDiskAccessEnabled", default=None)


class CloudInfo(AIRBaseModel):
    """Cloud provider information."""
    # This will be populated based on actual API response structure
    provider: Optional[str] = None
    region: Optional[str] = None
    instance_id: Optional[str] = None


class Asset(AIRBaseModel):
    """Asset (endpoint) model."""
    
    # Basic identification
    id: str = Field(alias="_id")
    name: str
    os: Optional[str] = None  # Make optional since some assets don't have this
    platform: Platform
    ip_address: Optional[str] = Field(alias="ipAddress", default=None)
    organization_id: int = Field(alias="organizationId", default=0)
    
    # Group and labeling
    group_id: Optional[str] = Field(alias="groupId", default=None)
    group_full_path: Optional[str] = Field(alias="groupFullPath", default=None)
    label: Optional[str] = None
    
    # Server and management status
    is_server: bool = Field(alias="isServer", default=False)
    is_managed: bool = Field(alias="isManaged", default=True)
    agent_installed: Optional[bool] = Field(alias="agentInstalled", default=None)
    managed_status: ManagedStatus = Field(alias="managedStatus", default=ManagedStatus.MANAGED)
    
    # Network information
    net_interfaces: Optional[List[NetworkInterface]] = Field(alias="netInterfaces", default_factory=list)
    
    # Timestamps
    last_seen: Optional[datetime] = Field(alias="lastSeen", default=None)
    registered_at: Optional[datetime] = Field(alias="registeredAt", default=None)
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)
    
    # Version and architecture
    version: Optional[str] = None
    version_no: Optional[int] = Field(alias="versionNo", default=None)
    build_arch: Optional[str] = Field(alias="buildArch", default=None)
    
    # Security and authentication
    security_token: Optional[str] = Field(alias="securityToken", default=None)
    online_status: OnlineStatus = Field(alias="onlineStatus", default=OnlineStatus.OFFLINE)
    isolation_status: IsolationStatus = Field(alias="isolationStatus", default=IsolationStatus.UNISOLATED)
    
    # System resources and capabilities
    system_resources: Optional[SystemResources] = Field(alias="systemResources", default=None)
    features: Optional[AssetFeatures] = None
    
    # Cloud and infrastructure
    cloud: Optional[CloudInfo] = None
    has_evidence: Optional[bool] = Field(alias="hasEvidence", default=None)
    relay_server_id: Optional[str] = Field(alias="relayServerId", default=None)
    connection_route: Optional[str] = Field(alias="connectionRoute", default=None)
    
    # Asset classification
    asset_id: Optional[str] = Field(alias="assetId", default=None)
    asset_type: Optional[str] = Field(alias="assetType", default=None)
    timezone_offset: Optional[int] = Field(alias="timezoneOffset", default=None)
    
    # Vendor information
    vendor_id: Optional[str] = Field(alias="vendorId", default=None)
    vendor_device_id: Optional[str] = Field(alias="vendorDeviceId", default=None)
    responder_id: Optional[str] = Field(alias="responderId", default=None)
    
    # Update management
    excluded_from_updates: Optional[bool] = Field(alias="excludedFromUpdates", default=None)
    unsupported_os_to_update: Optional[bool] = Field(alias="unsupportedOsToUpdate", default=None)
    version_updating: Optional[bool] = Field(alias="versionUpdating", default=None)
    deploying: Optional[bool] = Field(alias="deploying", default=None)
    waiting_for_version_update_fix: bool = Field(alias="waitingForVersionUpdateFix", default=False)
    
    # Issues, tags, and policies
    issues: List[str] = []
    tags: List[Union[str, Tag]] = []
    policies: List[Any] = []


class AssetDetail(Asset):
    """Detailed asset information."""
    pass  # Same as Asset for now, can be extended


class TaskDurations(AIRBaseModel):
    """Task duration information."""
    processing: Optional[int] = None
    uploading: Optional[int] = None
    analyzing: Optional[int] = None
    compressing: Optional[int] = None


class TaskMetadata(AIRBaseModel):
    """Task metadata information."""
    purged: Optional[bool] = None
    has_case_db: Optional[bool] = Field(alias="hasCaseDb", default=None)
    has_case_ppc: Optional[bool] = Field(alias="hasCasePpc", default=None)
    has_drone_data: Optional[bool] = Field(alias="hasDroneData", default=None)
    isolation: Optional[bool] = None
    import_status: Optional[str] = Field(alias="importStatus", default=None)
    disk_usage_in_bytes: Optional[int] = Field(alias="diskUsageInBytes", default=None)


class TaskResponse(AIRBaseModel):
    """Task response information."""
    error_message: Optional[str] = Field(alias="errorMessage", default=None)
    case_directory: Optional[str] = Field(alias="caseDirectory", default=None)
    match_count: Optional[int] = Field(alias="matchCount", default=None)
    result: Optional[Dict[str, Any]] = None


class AssetTask(AIRBaseModel):
    """Task associated with an asset."""
    
    # Basic identification
    id: str = Field(alias="_id")
    task_id: str = Field(alias="taskId")
    name: str
    type: str
    endpoint_id: str = Field(alias="endpointId")
    endpoint_name: str = Field(alias="endpointName")
    organization_id: int = Field(alias="organizationId", default=0)
    
    # Status and progress
    status: str
    recurrence: Optional[str] = None
    progress: int = 0
    
    # Duration information
    duration: Optional[int] = None  # Legacy single duration field
    durations: Optional[TaskDurations] = None  # NEW - Complex duration object
    
    # Task metadata
    metadata: Optional[TaskMetadata] = None  # NEW - Task metadata
    
    # Relationships
    case_ids: Optional[List[str]] = Field(alias="caseIds", default_factory=list)
    
    # Timestamps and users
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)
    created_by: Optional[str] = Field(alias="createdBy", default=None)  # NEW
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)
    updated_by: Optional[str] = Field(alias="updatedBy", default=None)  # NEW - Not in response but likely exists
    
    # Response data
    response: Optional[TaskResponse] = None  # Enhanced response structure


class AssetFilter(Filter):
    """Filter for asset queries - matches API documentation exactly."""
    
    # Basic search and identification
    search_term: Optional[str] = None
    name: Optional[str] = None
    ip_address: Optional[str] = None
    
    # Group and organization
    group_id: Optional[str] = None
    group_full_path: Optional[str] = None
    organization_ids: List[int] = []  # Required by API
    
    # Status filters (arrays as per API)
    managed_status: Optional[List[str]] = None  # ["managed", "unmanaged", "off-network"]
    isolation_status: Optional[List[str]] = None  # ["isolating", "isolated", "unisolating", "unisolated"]
    online_status: Optional[List[str]] = None  # ["online", "offline"]
    
    # Platform and technical details
    platform: Optional[List[str]] = None  # ["windows", "linux", "darwin"]
    issue: Optional[List[str]] = None  # ["unreachable", "old-version", "update-required"] - Changed to List
    version: Optional[str] = None
    policy: Optional[str] = None
    
    # Tags and labels
    tags: Optional[List[str]] = None
    tag_id: Optional[str] = None  # Added missing field - required by some endpoints
    label: Optional[str] = None  # Added missing field
    
    # Endpoint targeting
    included_endpoint_ids: Optional[List[str]] = None
    excluded_endpoint_ids: Optional[List[str]] = None
    
    # Date/time filters - Added missing fields
    last_seen_before: Optional[str] = None  # ISO 8601 format
    last_seen_after: Optional[str] = None   # ISO 8601 format
    last_seen_between: Optional[str] = None # Comma-separated range
    last_seen: Optional[str] = None  # For backward compatibility
    
    # Cloud provider filters - Added missing fields
    aws_regions: Optional[List[str]] = None
    azure_regions: Optional[List[str]] = None
    
    # Special filters - Added missing field
    unisolated: Optional[str] = None  # Added per API docs
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters."""
        # Start with base pagination/sorting parameters from parent class
        params = super().to_params()
        
        # Add asset-specific filter parameters
        if self.search_term is not None:
            params["filter[searchTerm]"] = self.search_term
        if self.name is not None:
            params["filter[name]"] = self.name
        if self.ip_address is not None:
            params["filter[ipAddress]"] = self.ip_address
            
        # Group parameters
        if self.group_id is not None:
            params["filter[groupId]"] = self.group_id
        if self.group_full_path is not None:
            params["filter[groupFullPath]"] = self.group_full_path
            
        # Organization IDs (required)
        if self.organization_ids:
            params["filter[organizationIds]"] = ",".join([str(x) for x in self.organization_ids])
        
        # Status arrays
        if self.managed_status:
            params["filter[managedStatus]"] = ",".join(self.managed_status)
        if self.isolation_status:
            params["filter[isolationStatus]"] = ",".join(self.isolation_status)
        if self.online_status:
            params["filter[onlineStatus]"] = ",".join(self.online_status)
            
        # Platform and technical
        if self.platform:
            params["filter[platform]"] = ",".join(self.platform)
        if self.issue:
            params["filter[issue]"] = ",".join(self.issue)
        if self.version is not None:
            params["filter[version]"] = self.version
        if self.policy is not None:
            params["filter[policy]"] = self.policy
            
        # Tags and labels
        if self.tags:
            params["filter[tags]"] = ",".join(self.tags)
        if self.tag_id is not None:
            params["filter[tagId]"] = self.tag_id
        if self.label is not None:
            params["filter[label]"] = self.label
            
        # Endpoint targeting
        if self.included_endpoint_ids:
            params["filter[includedEndpointIds]"] = ",".join(self.included_endpoint_ids)
        if self.excluded_endpoint_ids:
            params["filter[excludedEndpointIds]"] = ",".join(self.excluded_endpoint_ids)
            
        # Date/time filters
        if self.last_seen_before is not None:
            params["filter[lastSeenBefore]"] = self.last_seen_before
        if self.last_seen_after is not None:
            params["filter[lastSeenAfter]"] = self.last_seen_after
        if self.last_seen_between is not None:
            params["filter[lastSeenBetween]"] = self.last_seen_between
        if self.last_seen is not None:
            params["filter[lastSeen]"] = self.last_seen
            
        # Cloud provider filters
        if self.aws_regions:
            params["filter[awsRegions]"] = ",".join(self.aws_regions)
        if self.azure_regions:
            params["filter[azureRegions]"] = ",".join(self.azure_regions)
            
        # Special filters
        if self.unisolated is not None:
            params["filter[unisolated]"] = self.unisolated
        
        return params
    
    def to_filter_dict(self) -> Dict[str, Any]:
        """Convert filter to dictionary for command payloads - matches API specification exactly."""
        # Include ALL fields as per API specification, with empty defaults
        filter_dict = {
            # Basic search fields (empty strings as defaults)
            "searchTerm": self.search_term or "",
            "name": self.name or "",
            "ipAddress": self.ip_address or "",
            "groupId": self.group_id or "",
            "groupFullPath": self.group_full_path or "",
            
            # Required array fields (with proper defaults)
            "organizationIds": self.organization_ids or [0],  # Keep as integers
            "managedStatus": self.managed_status or ["managed"],  # Default to managed
            "isolationStatus": self.isolation_status or [],
            "onlineStatus": self.online_status or [],
            "platform": self.platform or [],
            "tags": self.tags or [],
            
            # Technical fields (empty strings as defaults)  
            "issue": self.issue[0] if self.issue and len(self.issue) > 0 else "",  # API expects string not array
            "version": self.version or "",
            "policy": self.policy or "",
            "tagId": self.tag_id or "",  # Added missing field
            
            # Endpoint targeting (with proper defaults)
            "includedEndpointIds": self.included_endpoint_ids or [],
            "excludedEndpointIds": self.excluded_endpoint_ids or [],
        }
        
        return filter_dict 


class AssetTaskFilter(Filter):
    """Filter for asset task queries - matches API specification exactly."""
    
    # Search and identification
    search_term: Optional[str] = None
    name: Optional[str] = None
    endpoint_ids: Optional[List[str]] = None
    
    # Task properties
    status: Optional[List[str]] = None  # scheduled, assigned, processing, completed, failed, expired, cancelled, compressing, uploading, analyzing, partially-completed
    type: Optional[List[str]] = None  # acquisition, offline-acquisition, triage, offline-triage, investigation, interact-shell, baseline-comparison, baseline-acquisition, acquire-image
    execution_type: Optional[List[str]] = None  # instant, scheduled
    
    # Task metadata
    has_drone_data: Optional[str] = None  # yes, no
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters."""
        params = {}
        
        # Pagination parameters (not in filter namespace) - only if set
        if self.page_number is not None:
            params["pageNumber"] = self.page_number
        if self.page_size is not None:
            params["pageSize"] = self.page_size
        if self.sort_by is not None:
            params["sortBy"] = self.sort_by
        if self.sort_type is not None:
            params["sortType"] = self.sort_type
        
        # Add task-specific filter parameters (use API field names)
        if self.search_term is not None:
            params["filter[searchTerm]"] = self.search_term
        if self.name is not None:
            params["filter[name]"] = self.name
        if self.endpoint_ids:
            params["filter[endpointIds]"] = ",".join(self.endpoint_ids)
            
        # Status and type arrays
        if self.status:
            params["filter[status]"] = ",".join(self.status)
        if self.type:
            params["filter[type]"] = ",".join(self.type)
        if self.execution_type:
            params["filter[executionType]"] = ",".join(self.execution_type)
            
        # Special filters
        if self.has_drone_data is not None:
            params["filter[hasDroneData]"] = self.has_drone_data
        
        return params 