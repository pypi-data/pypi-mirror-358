"""
Acquisition-related data models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel, Filter


class NetworkCaptureConfig(AIRBaseModel):
    """Network capture configuration - matches API specification exactly."""
    
    enabled: bool = False
    duration: int = 60
    pcap: Dict[str, bool] = {"enabled": False}
    networkFlow: Dict[str, bool] = {"enabled": False}  # API uses camelCase


class EDiscoveryPattern(AIRBaseModel):
    """eDiscovery pattern model."""
    
    pattern: str
    category: str


class EDiscoveryConfig(AIRBaseModel):
    """eDiscovery configuration matching API specification exactly."""
    
    patterns: List[EDiscoveryPattern] = []
    
    def model_dump(self, **kwargs):
        """Override to serialize patterns under 'edPatterns' key for API."""
        data = super().model_dump(**kwargs)
        if 'patterns' in data:
            data['edPatterns'] = data.pop('patterns')
        return data


class SaveLocationConfig(AIRBaseModel):
    """Save location configuration."""
    
    location: str
    use_most_free_volume: bool = False
    repository_id: Optional[str] = None
    path: str
    volume: Optional[str] = None
    tmp: str = "tmp"
    direct_collection: bool = False


class TaskConfig(AIRBaseModel):
    """Task configuration."""
    
    choice: str
    save_to: Dict[str, SaveLocationConfig]
    cpu: Dict[str, int] = {"limit": 50}
    bandwidth: Optional[Dict[str, int]] = None
    compression: Dict[str, Any] = {
        "enabled": False,
        "encryption": {"enabled": False, "password": ""}
    }


class DroneConfig(AIRBaseModel):
    """Drone configuration."""
    
    auto_pilot: bool = False
    enabled: bool = False
    analyzers: List[str] = []
    keywords: List[str] = []


class FilterConfig(AIRBaseModel):
    """Filter configuration for acquisition tasks - matches API specification exactly."""
    
    # Basic search and identification
    search_term: Optional[str] = None
    name: Optional[str] = None
    ip_address: Optional[str] = None
    group_id: Optional[str] = None
    group_full_path: Optional[str] = None
    label: Optional[str] = None  # NEW - Missing from API spec
    
    # Status filters (arrays as per API)
    managed_status: List[str] = []
    isolation_status: List[str] = []
    platform: List[str] = []
    issue: Optional[str] = None  # API expects string, not array
    online_status: List[str] = []
    
    # Tags and policies
    tags: List[str] = []
    version: Optional[str] = None
    policy: Optional[str] = None
    
    # Endpoint targeting
    included_endpoint_ids: List[str] = []
    excluded_endpoint_ids: List[str] = []
    
    # Organization and case
    organization_ids: List[int] = []  # Required by API
    case_id: Optional[str] = None  # NEW - Missing from API spec
    
    # Date/time filters
    last_seen: Optional[str] = None  # NEW - Missing from API spec (ISO 8601 format)
    
    # Cloud provider filters
    aws_regions: Optional[List[str]] = None  # NEW - Missing from API spec
    azure_regions: Optional[List[str]] = None  # NEW - Missing from API spec


class AcquisitionProfilePlatformDetails(AIRBaseModel):
    """Platform-specific acquisition profile details - matches API specification exactly."""
    
    evidenceList: List[str] = []  # API uses camelCase
    artifactList: Optional[List[str]] = None  # API uses camelCase
    customContentProfiles: List[Any] = []  # API uses camelCase
    osQueries: List[str] = []  # FIXED: Added missing required field
    networkCapture: Optional[NetworkCaptureConfig] = None  # API uses camelCase
    
    # Windows-specific fields
    eventLogRecordsConfig: Optional[Dict[str, List[str]]] = None  # FIXED: Added for Windows platform
    
    @classmethod
    def create_windows_config(cls, evidence_list: Optional[List[str]] = None, artifact_list: Optional[List[str]] = None) -> "AcquisitionProfilePlatformDetails":
        """Create a proper Windows platform configuration with all required fields."""
        return cls(
            evidenceList=evidence_list or [],  # FIXED: Empty by default
            artifactList=artifact_list or [],  # FIXED: Empty by default
            customContentProfiles=[],
            osQueries=[],
            networkCapture=NetworkCaptureConfig(
                enabled=False,
                duration=600,
                pcap={"enabled": False},
                networkFlow={"enabled": False}
            ),
            eventLogRecordsConfig={"types": []}
        )
    
    @classmethod
    def create_linux_config(cls, evidence_list: Optional[List[str]] = None, artifact_list: Optional[List[str]] = None) -> "AcquisitionProfilePlatformDetails":
        """Create a proper Linux platform configuration with all required fields."""
        return cls(
            evidenceList=evidence_list or [],  # FIXED: Empty by default
            artifactList=artifact_list or [],  # FIXED: Empty by default
            customContentProfiles=[],
            osQueries=[],
            networkCapture=NetworkCaptureConfig(
                enabled=False,
                duration=600,
                pcap={"enabled": False},
                networkFlow={"enabled": False}
            )
        )
    
    @classmethod
    def create_macos_config(cls, evidence_list: Optional[List[str]] = None, artifact_list: Optional[List[str]] = None) -> "AcquisitionProfilePlatformDetails":
        """Create a proper macOS platform configuration with all required fields."""
        return cls(
            evidenceList=evidence_list or [],  # FIXED: Empty by default
            artifactList=artifact_list or [],  # FIXED: Empty by default
            customContentProfiles=[],
            osQueries=[],
            networkCapture=NetworkCaptureConfig(
                enabled=False,
                duration=600,
                pcap={"enabled": False},
                networkFlow={"enabled": False}
            )
        )


class AcquisitionProfileAIXDetails(AIRBaseModel):
    """AIX-specific acquisition profile details - AIX doesn't support osQueries or networkCapture."""
    
    evidenceList: List[str] = []  # API uses camelCase
    artifactList: Optional[List[str]] = None  # API uses camelCase
    customContentProfiles: List[Any] = []  # API uses camelCase
    # Note: AIX doesn't have osQueries, networkCapture, or eventLogRecordsConfig
    
    @classmethod
    def create_aix_config(cls, evidence_list: Optional[List[str]] = None, artifact_list: Optional[List[str]] = None) -> "AcquisitionProfileAIXDetails":
        """Create a proper AIX platform configuration with all required fields."""
        return cls(
            evidenceList=evidence_list or [],  # FIXED: Empty by default
            artifactList=artifact_list or [],  # FIXED: Empty by default
            customContentProfiles=[],
            # Note: AIX doesn't have osQueries or networkCapture
        )


class AcquisitionProfile(AIRBaseModel):
    """Acquisition profile model."""
    
    id: str
    name: str
    organization_ids: List[int] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str
    deletable: bool = True
    artifacts: List[str] = []  # Added for test compatibility
    
    # Additional fields from API response
    average_time: Optional[int] = None
    last_used_at: Optional[datetime] = None
    last_used_by: Optional[str] = None
    has_event_log_records_evidence: Optional[bool] = None


class AcquisitionProfileDetails(AcquisitionProfile):
    """Detailed acquisition profile with platform configurations."""
    
    windows: Optional[AcquisitionProfilePlatformDetails] = None
    linux: Optional[AcquisitionProfilePlatformDetails] = None
    macos: Optional[AcquisitionProfilePlatformDetails] = None
    aix: Optional[AcquisitionProfilePlatformDetails] = None
    e_discovery: Optional[Dict[str, List[EDiscoveryPattern]]] = None
    settings: Optional[Dict[str, Any]] = None  # Added for test compatibility


class EndpointVolumeConfig(AIRBaseModel):
    """Endpoint and volume configuration for disk image acquisition."""
    
    endpointId: str  # API uses camelCase
    volumes: List[str] = []


class DiskImageOptions(AIRBaseModel):
    """Disk image options - API field names in camelCase."""
    
    chunkSize: int  # API uses camelCase
    chunkCount: int = 0  # API uses camelCase
    startOffset: int  # API uses camelCase
    imageType: str = "dd"  # API uses camelCase
    singleFile: bool = False  # API uses camelCase
    endpoints: List[EndpointVolumeConfig] = []


class SchedulerConfig(AIRBaseModel):
    """Scheduler configuration for acquisition tasks."""
    
    when: str = "now"
    timezone_type: Optional[str] = None
    timezone: Optional[str] = None
    start_date: Optional[int] = None
    recurrence: Optional[str] = None
    repeat_every: Optional[int] = None
    repeat_on_week: Optional[List[str]] = None
    repeat_on_month: Optional[int] = None
    end_repeat_type: Optional[str] = None
    end_date: Optional[int] = None
    limit: Optional[int] = None


class AcquisitionTaskRequest(AIRBaseModel):
    """Acquisition task request."""
    
    case_id: str
    drone_config: DroneConfig
    task_config: TaskConfig
    acquisition_profile_id: str
    filter: FilterConfig


class ImageAcquisitionTaskRequest(AIRBaseModel):
    """Image acquisition task request."""
    
    case_id: Optional[str] = None
    task_config: TaskConfig
    disk_image_options: DiskImageOptions
    filter: FilterConfig
    scheduler_config: SchedulerConfig = SchedulerConfig()


class CreateAcquisitionProfileRequest(AIRBaseModel):
    """Create acquisition profile request - matches API specification exactly."""
    
    name: str
    organizationIds: List[int] = [0]  # FIXED: Default to [0] instead of []
    windows: AcquisitionProfilePlatformDetails  # Required by API
    linux: AcquisitionProfilePlatformDetails   # Required by API
    macos: AcquisitionProfilePlatformDetails   # Required by API
    aix: AcquisitionProfileAIXDetails          # FIXED: Use AIX-specific model
    eDiscovery: EDiscoveryConfig = EDiscoveryConfig(patterns=[
        EDiscoveryPattern(pattern="**/*.7z", category="Archives")
    ])  # API requires this field to be non-empty


# Simplified request models for testing
class CreateAcquisitionRequest(AIRBaseModel):
    """Simplified acquisition request for testing."""
    
    filter: Dict[str, Any]
    profileId: str
    name: Optional[str] = None


class CreateImageAcquisitionRequest(AIRBaseModel):
    """Simplified image acquisition request for testing - FIXED with required fields."""
    
    filter: Dict[str, Any]
    name: Optional[str] = None
    fullDisk: bool = False
    repository_id: Optional[str] = None
    volumes: Optional[List[str]] = None
    
    # FIXED: Add required fields for image acquisition
    case_id: Optional[str] = None
    task_config: Optional[Dict[str, Any]] = None
    disk_image_options: Optional[Dict[str, Any]] = None
    scheduler_config: Optional[Dict[str, Any]] = None

    # API expects imageFormat for disk image type (e.g., dd, e01)
    image_format: Optional[str] = Field(default=None, alias="imageFormat")


class AcquisitionFilter(Filter):
    """Filter for acquisition profile queries - matches API specification exactly."""
    
    # Search and identification
    search_term: Optional[str] = None
    name: Optional[str] = None
    
    # Organization parameters
    organization_ids: Optional[List[int]] = None  # Required by API
    all_organizations: Optional[bool] = None  # true/false
    
    # Profile metadata (for backwards compatibility)
    created_by: Optional[str] = None
    deletable: Optional[bool] = None
    
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
        
        # Add acquisition-specific filter parameters (use API field names)
        if self.search_term is not None:
            params["filter[searchTerm]"] = self.search_term
        if self.name is not None:
            params["filter[name]"] = self.name
        if self.organization_ids is not None:
            params["filter[organizationIds]"] = ",".join([str(x) for x in self.organization_ids])
        if self.all_organizations is not None:
            params["filter[allOrganizations]"] = "true" if self.all_organizations else "false"
        
        # Backwards compatibility fields (not in API spec but may be used)
        if self.created_by is not None:
            params["filter[createdBy]"] = self.created_by
        if self.deletable is not None:
            params["filter[deletable]"] = "true" if self.deletable else "false"
        
        return params 