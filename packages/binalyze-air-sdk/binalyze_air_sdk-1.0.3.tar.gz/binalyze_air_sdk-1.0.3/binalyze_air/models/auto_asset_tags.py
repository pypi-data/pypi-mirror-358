"""
Auto Asset Tags-related data models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import Field
from pydantic import ConfigDict
from enum import Enum

from ..base import AIRBaseModel, Filter


class ConditionField(str, Enum):
    """Valid condition fields for auto asset tags."""
    HOSTNAME = "hostname"
    IP_ADDRESS = "ip-address"
    SUBNET = "subnet"
    OSQUERY = "osquery"
    PROCESS = "process"
    FILE = "file"
    DIRECTORY = "directory"


class ConditionOperator(str, Enum):
    """Valid condition operators for auto asset tags."""
    RUNNING = "running"
    EXIST = "exist"
    IS = "is"
    CONTAINS = "contains"
    STARTS_WITH = "starts-with"
    ENDS_WITH = "ends-with"
    IN_RANGE = "in-range"
    HAS_RESULT = "has-result"
    NOT_RUNNING = "not-running"
    NOT_EXIST = "not-exist"
    HAS_NO_RESULT = "has-no-result"


class LogicalOperator(str, Enum):
    """Valid logical operators for condition groups."""
    AND = "and"
    OR = "or"


class AutoAssetTagCondition(AIRBaseModel):
    """Individual condition for auto asset tag."""
    
    field: ConditionField
    operator: ConditionOperator
    value: str


class AutoAssetTagConditionGroup(AIRBaseModel):
    """Group of conditions with logical operator."""
    
    operator: LogicalOperator
    conditions: List[AutoAssetTagCondition]


class AutoAssetTagConditions(AIRBaseModel):
    """Platform-specific conditions structure."""
    
    operator: LogicalOperator
    conditions: List[AutoAssetTagConditionGroup]


class AutoAssetTag(AIRBaseModel):
    """Auto asset tag model - handles actual API response format."""
    
    id: str = Field(alias="_id")
    tag: str
    linuxConditions: Optional[Union[AutoAssetTagConditions, Dict[str, Any]]] = None
    windowsConditions: Optional[Union[AutoAssetTagConditions, Dict[str, Any]]] = None
    macosConditions: Optional[Union[AutoAssetTagConditions, Dict[str, Any]]] = None
    organizationIds: Optional[List[int]] = Field(default_factory=list)
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    conditionIdCounter: Optional[int] = None  # API includes this field


class CreateAutoAssetTagRequest(AIRBaseModel):
    """Create auto asset tag request model - matches API specification exactly."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    tag: str
    linuxConditions: AutoAssetTagConditions  # Required by API
    windowsConditions: AutoAssetTagConditions  # Required by API  
    macosConditions: AutoAssetTagConditions  # Required by API
    organizationIds: List[int] = Field(default_factory=list)
    
    def model_dump(self, **kwargs):
        """Exclude None values from serialization to prevent API validation errors."""
        # Set exclude_none=True if not explicitly set
        if 'exclude_none' not in kwargs:
            kwargs['exclude_none'] = True
        return super().model_dump(**kwargs)


class UpdateAutoAssetTagRequest(AIRBaseModel):
    """Update auto asset tag request model."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    tag: Optional[str] = None
    linuxConditions: Optional[AutoAssetTagConditions] = None
    windowsConditions: Optional[AutoAssetTagConditions] = None
    macosConditions: Optional[AutoAssetTagConditions] = None
    organizationIds: Optional[List[int]] = Field(default_factory=list)
    
    def model_dump(self, **kwargs):
        """Exclude None values from serialization to prevent API validation errors."""
        # Set exclude_none=True if not explicitly set
        if 'exclude_none' not in kwargs:
            kwargs['exclude_none'] = True
        return super().model_dump(**kwargs)


class StartTaggingSchedulerConfig(AIRBaseModel):
    """Scheduler configuration for start tagging."""
    
    when: str  # "now" or "scheduled"
    timezoneType: Optional[str] = None  # "asset" or "custom" - required if scheduled
    timezone: Optional[str] = None  # required if scheduled and custom timezone
    startDate: Optional[int] = None  # unix timestamp - required if scheduled
    recurrence: Optional[str] = None  # "onetime", "daily", "weekly", "monthly" - required if scheduled
    repeatEvery: Optional[int] = None  # required if scheduled and daily/monthly
    repeatOnWeek: Optional[List[str]] = None  # required if scheduled and weekly
    repeatOnMonth: Optional[int] = None  # required if scheduled and monthly
    endRepeatType: Optional[str] = None  # "never", "date", "occurrence" - required if scheduled
    endDate: Optional[int] = None  # unix timestamp - required if end repeat type is date
    limit: Optional[int] = None  # required if end repeat type is occurrence


class StartTaggingFilter(AIRBaseModel):
    """Filter for start tagging process - matches API specification exactly."""
    
    organizationIds: List[int]  # Required
    searchTerm: Optional[str] = ""
    name: Optional[str] = ""
    ipAddress: Optional[str] = ""
    groupId: Optional[str] = ""
    groupFullPath: Optional[str] = ""
    label: Optional[str] = ""
    lastSeen: Optional[str] = ""
    managedStatus: List[str] = []  # "unmanaged", "managed", "off-network"
    isolationStatus: List[str] = []  # "isolating", "isolated", "unisolating", "unisolated"
    platform: List[str] = []  # "windows", "linux", "darwin"
    issue: Optional[str] = ""  # "unreachable", "old-version", "update-required"
    onlineStatus: List[str] = []  # "online", "offline"
    tags: List[str] = []
    version: Optional[str] = ""
    policy: Optional[str] = ""
    includedEndpointIds: List[str] = []
    excludedEndpointIds: List[str] = []
    caseId: Optional[str] = None


class StartTaggingRequest(AIRBaseModel):
    """Start tagging process request model - matches API specification exactly."""
    
    filter: StartTaggingFilter
    schedulerConfig: StartTaggingSchedulerConfig


class TaggingResult(AIRBaseModel):
    """Tagging process result model."""
    
    taskId: str
    message: str
    processedTags: int
    affectedAssets: int


class TaggingTask(AIRBaseModel):
    """Individual tagging task result from start tagging API."""
    
    task_id: str = Field(alias="_id")
    name: str = Field(alias="name")


class TaggingResponse(AIRBaseModel):
    """Response from start tagging API containing list of tasks."""
    
    tasks: List[TaggingTask] = []
    
    @classmethod
    def from_api_result(cls, result_list: List[Dict[str, Any]]) -> 'TaggingResponse':
        """Create TaggingResponse from API result list."""
        if not isinstance(result_list, list):
            raise ValueError("API result must be a list")
        
        tasks = [TaggingTask(**task) for task in result_list]
        return cls(tasks=tasks)
    
    @property
    def task_count(self) -> int:
        """Get the number of tasks created."""
        return len(self.tasks)
    
    def get_task_ids(self) -> List[str]:
        """Get list of all task IDs."""
        return [task.task_id for task in self.tasks]


class AutoAssetTagFilter(Filter):
    """Filter for auto asset tag queries."""
    
    tag: Optional[str] = None
    organization_ids: Optional[List[int]] = None
    search_term: Optional[str] = None
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters with proper field name mapping."""
        params = super().to_params()
        
        # Convert organization_ids to organizationIds for API compatibility
        if "filter[organization_ids]" in params:
            params["filter[organizationIds]"] = params.pop("filter[organization_ids]")
        
        # Convert search_term to searchTerm for API compatibility
        if "filter[search_term]" in params:
            params["filter[searchTerm]"] = params.pop("filter[search_term]")
            
        return params 