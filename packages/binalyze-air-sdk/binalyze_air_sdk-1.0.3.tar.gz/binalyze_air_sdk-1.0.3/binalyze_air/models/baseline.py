"""
Baseline-related data models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel, Filter


class BaselineStatus(str, Enum):
    """Baseline status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CREATING = "creating"
    FAILED = "failed"


class BaselineType(str, Enum):
    """Baseline type."""
    SYSTEM = "system"
    SECURITY = "security"
    CUSTOM = "custom"
    COMPLIANCE = "compliance"


class ComparisonStatus(str, Enum):
    """Comparison status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ChangeType(str, Enum):
    """Type of change detected."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    MOVED = "moved"


class BaselineItem(AIRBaseModel):
    """Individual baseline item."""
    
    id: str
    path: str
    item_type: str  # file, registry, service, process, etc.
    hash: Optional[str] = None
    size: Optional[int] = None
    permissions: Optional[str] = None
    owner: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    attributes: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class Baseline(AIRBaseModel):
    """Baseline model."""
    
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    type: BaselineType
    status: BaselineStatus = BaselineStatus.CREATING
    endpoint_id: str = Field(alias="endpointId")
    endpoint_name: str = Field(alias="endpointName")
    organization_id: int = Field(default=0, alias="organizationId")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    created_by: str = Field(alias="createdBy")
    item_count: int = Field(default=0, alias="itemCount")
    file_count: int = Field(default=0, alias="fileCount")
    registry_count: int = Field(default=0, alias="registryCount")
    service_count: int = Field(default=0, alias="serviceCount")
    process_count: int = Field(default=0, alias="processCount")
    network_connection_count: int = Field(default=0, alias="networkConnectionCount")
    tags: List[str] = []
    profile_id: Optional[str] = Field(default=None, alias="profileId")
    profile_name: Optional[str] = Field(default=None, alias="profileName")
    last_comparison: Optional[datetime] = Field(default=None, alias="lastComparison")
    comparison_count: int = Field(default=0, alias="comparisonCount")


class BaselineProfile(AIRBaseModel):
    """Baseline profile model."""
    
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    organization_id: int = Field(default=0, alias="organizationId")
    include_files: bool = Field(default=True, alias="includeFiles")
    include_registry: bool = Field(default=True, alias="includeRegistry")
    include_services: bool = Field(default=True, alias="includeServices")
    include_processes: bool = Field(default=False, alias="includeProcesses")
    include_network: bool = Field(default=False, alias="includeNetwork")
    file_patterns: List[str] = Field(default=[], alias="filePatterns")
    exclude_patterns: List[str] = Field(default=[], alias="excludePatterns")
    registry_keys: List[str] = Field(default=[], alias="registryKeys")
    custom_checks: List[Dict[str, Any]] = Field(default=[], alias="customChecks")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    created_by: str = Field(alias="createdBy")
    is_default: bool = Field(default=False, alias="isDefault")
    usage_count: int = Field(default=0, alias="usageCount")


class BaselineChange(AIRBaseModel):
    """Baseline change detection model."""
    
    id: str = Field(alias="_id")
    comparison_id: str = Field(alias="comparisonId")
    change_type: ChangeType = Field(alias="changeType")
    item_type: str = Field(alias="itemType")
    path: str
    old_value: Optional[Dict[str, Any]] = Field(default=None, alias="oldValue")
    new_value: Optional[Dict[str, Any]] = Field(default=None, alias="newValue")
    severity: str = "medium"  # low, medium, high, critical
    category: str
    description: str
    detected_at: datetime = Field(alias="detectedAt")
    risk_score: float = Field(default=0.0, alias="riskScore")


class BaselineComparison(AIRBaseModel):
    """Baseline comparison result model."""
    
    id: str = Field(alias="_id")
    baseline_id: str = Field(alias="baselineId")
    baseline_name: str = Field(alias="baselineName")
    endpoint_id: str = Field(alias="endpointId")
    endpoint_name: str = Field(alias="endpointName")
    status: ComparisonStatus
    started_at: Optional[datetime] = Field(default=None, alias="startedAt")
    completed_at: Optional[datetime] = Field(default=None, alias="completedAt")
    duration: Optional[int] = None  # seconds
    total_changes: int = Field(default=0, alias="totalChanges")
    added_items: int = Field(default=0, alias="addedItems")
    removed_items: int = Field(default=0, alias="removedItems")
    modified_items: int = Field(default=0, alias="modifiedItems")
    moved_items: int = Field(default=0, alias="movedItems")
    high_risk_changes: int = Field(default=0, alias="highRiskChanges")
    medium_risk_changes: int = Field(default=0, alias="mediumRiskChanges")
    low_risk_changes: int = Field(default=0, alias="lowRiskChanges")
    changes: List[BaselineChange] = []
    organization_id: int = Field(default=0, alias="organizationId")
    triggered_by: str = Field(alias="triggeredBy")
    error_message: Optional[str] = Field(default=None, alias="errorMessage")


class BaselineSchedule(AIRBaseModel):
    """Baseline comparison schedule model."""
    
    id: str = Field(alias="_id")
    baseline_id: str = Field(alias="baselineId")
    name: str
    enabled: bool = True
    frequency: str  # daily, weekly, monthly
    time_of_day: str = Field(alias="timeOfDay")  # HH:MM format
    day_of_week: Optional[int] = Field(default=None, alias="dayOfWeek")  # 0-6, Monday=0
    day_of_month: Optional[int] = Field(default=None, alias="dayOfMonth")  # 1-31
    next_run: Optional[datetime] = Field(default=None, alias="nextRun")
    last_run: Optional[datetime] = Field(default=None, alias="lastRun")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    created_by: str = Field(alias="createdBy")
    notification_enabled: bool = Field(default=True, alias="notificationEnabled")
    notification_threshold: int = Field(default=10, alias="notificationThreshold")  # minimum changes to notify


class BaselineFilter(Filter):
    """Filter for baseline queries."""
    
    name: Optional[str] = None
    type: Optional[List[BaselineType]] = None
    status: Optional[List[BaselineStatus]] = None
    endpoint_id: Optional[str] = None
    endpoint_name: Optional[str] = None
    created_by: Optional[str] = None
    tags: Optional[List[str]] = None
    profile_id: Optional[str] = None
    has_recent_comparison: Optional[bool] = None


class CreateBaselineRequest(AIRBaseModel):
    """Request model for creating a baseline."""
    
    name: str
    description: Optional[str] = None
    type: BaselineType = BaselineType.SYSTEM
    endpoint_id: str
    profile_id: Optional[str] = None
    tags: List[str] = []
    organization_id: int = 0


class UpdateBaselineRequest(AIRBaseModel):
    """Request model for updating a baseline."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[BaselineStatus] = None
    tags: Optional[List[str]] = None


class CreateBaselineProfileRequest(AIRBaseModel):
    """Request model for creating a baseline profile."""
    
    name: str
    description: Optional[str] = None
    include_files: bool = True
    include_registry: bool = True
    include_services: bool = True
    include_processes: bool = False
    include_network: bool = False
    file_patterns: List[str] = []
    exclude_patterns: List[str] = []
    registry_keys: List[str] = []
    custom_checks: List[Dict[str, Any]] = []
    organization_id: int = 0


class CompareBaselineRequest(AIRBaseModel):
    """Request model for comparing baselines."""
    
    baseline_id: str
    endpoint_ids: Optional[List[str]] = None  # If None, use baseline's endpoint
    profile_id: Optional[str] = None  # Override baseline's profile
    include_low_risk: bool = True
    generate_report: bool = True 