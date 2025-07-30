"""
Triage-related data models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel, Filter


class TriageStatus(str, Enum):
    """Triage status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TriageSeverity(str, Enum):
    """Triage severity level."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TriageRuleType(str, Enum):
    """Triage rule type."""
    YARA = "yara"
    SIGMA = "sigma"
    OSQUERY = "osquery"
    REGEX = "regex"
    HASH = "hash"
    CUSTOM = "custom"


class TriageTag(AIRBaseModel):
    """Triage tag model."""
    
    id: str
    name: str
    description: Optional[str] = None
    color: str = "#3498db"
    created_at: Optional[datetime] = None
    created_by: str
    organization_id: int = 0
    usage_count: int = 0


class TriageRule(AIRBaseModel):
    """Triage rule model."""
    
    id: str
    name: str
    description: Optional[str] = None
    type: TriageRuleType
    rule_content: str
    enabled: bool = True
    severity: TriageSeverity = TriageSeverity.MEDIUM
    tags: List[str] = []
    search_in: Optional[str] = None
    organization_id: int = 0
    organization_ids: List[int] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str
    updated_by: Optional[str] = None
    match_count: int = 0
    last_match: Optional[datetime] = None
    deletable: Optional[bool] = None


class TriageProfile(AIRBaseModel):
    """Triage profile model."""
    
    id: str
    name: str
    description: Optional[str] = None
    rules: List[str] = []  # Rule IDs
    auto_apply: bool = False
    organization_id: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str
    updated_by: Optional[str] = None
    usage_count: int = 0


class TriageFilter(Filter):
    """Filter for triage queries."""
    
    rule_name: Optional[str] = None
    rule_type: Optional[List[TriageRuleType]] = None
    severity: Optional[List[TriageSeverity]] = None
    status: Optional[List[TriageStatus]] = None
    tags: Optional[List[str]] = None
    endpoint_id: Optional[str] = None
    task_id: Optional[str] = None
    created_by: Optional[str] = None
    enabled: Optional[bool] = None


class CreateTriageRuleRequest(AIRBaseModel):
    """Request model for creating a triage rule."""
    
    name: str
    description: Optional[str] = None
    type: TriageRuleType
    rule_content: str
    severity: TriageSeverity = TriageSeverity.MEDIUM
    tags: List[str] = []
    organization_id: int = 0


class UpdateTriageRuleRequest(AIRBaseModel):
    """Request model for updating a triage rule."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    rule_content: Optional[str] = None
    enabled: Optional[bool] = None
    severity: Optional[TriageSeverity] = None
    tags: Optional[List[str]] = None


class CreateTriageTagRequest(AIRBaseModel):
    """Request model for creating a triage tag."""
    
    name: str
    organization_id: int = Field(default=0, serialization_alias="organizationId")


class CreateTriageProfileRequest(AIRBaseModel):
    """Request model for creating a triage profile."""
    
    name: str
    description: Optional[str] = None
    rules: List[str] = []  # Rule IDs
    auto_apply: bool = False
    organization_id: int = 0 