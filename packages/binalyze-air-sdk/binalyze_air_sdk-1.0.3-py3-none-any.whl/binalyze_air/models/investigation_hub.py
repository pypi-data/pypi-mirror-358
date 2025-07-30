"""
Investigation Hub models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel


class InvestigationMeta(AIRBaseModel):
    """Investigation metadata model."""
    
    case_id: Optional[str] = Field(default=None, alias="caseId")
    disk_usage_in_bytes: Optional[int] = Field(default=None, alias="diskUsageInBytes")


class Investigation(AIRBaseModel):
    """Investigation model."""
    
    uid: str
    investigation_schema: str = Field(alias="schema")
    type: str
    meta: Optional[InvestigationMeta] = None
    timezone: str = "UTC"
    organization_id: int = Field(alias="organizationId")
    last_accessed_at: Optional[datetime] = Field(default=None, alias="lastAccessedAt")
    status: str
    migrations_completed: bool = Field(default=True, alias="migrationsCompleted")


class UpdateInvestigationRequest(AIRBaseModel):
    """Request model for updating investigations."""
    
    timezone: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class InvestigationAsset(AIRBaseModel):
    """Investigation asset model."""
    
    id: str = Field(alias="_id")
    name: str
    platform: str
    ip_address: Optional[str] = Field(default=None, alias="ipAddress")
    organization_id: int = Field(alias="organizationId")


class FlagSummary(AIRBaseModel):
    """Flag summary model."""
    
    id: int
    name: str
    color: str
    count: int


class EvidenceSection(AIRBaseModel):
    """Evidence section model."""
    
    name: str
    display_name: str = Field(alias="displayName")
    table_count: int = Field(alias="tableCount")
    record_count: int = Field(alias="recordCount")


class EvidenceStructure(AIRBaseModel):
    """Evidence structure model."""
    
    name: str
    type: str
    nullable: bool = Field(default=True)
    primary_key: bool = Field(default=False, alias="primaryKey")


class SQLQueryRequest(AIRBaseModel):
    """SQL query request model."""
    
    query: str
    page_size: int = Field(default=10, alias="pageSize")
    page_number: int = Field(default=1, alias="pageNumber")


class SQLQueryResult(AIRBaseModel):
    """SQL query result model."""
    
    entities: List[Dict[str, Any]]
    total_entity_count: int = Field(alias="totalEntityCount")
    current_page: int = Field(alias="currentPage")
    page_size: int = Field(alias="pageSize")
    next_page: int = Field(alias="nextPage")
    total_page_count: int = Field(alias="totalPageCount")
    previous_page: int = Field(alias="previousPage")


class FlagEvidenceRequest(AIRBaseModel):
    """Flag evidence request model."""
    
    flag_id: int = Field(alias="flagId")
    records: List[Dict[str, Any]]
    section: str


class EvidenceNote(AIRBaseModel):
    """Evidence note model."""
    
    id: str
    content: str
    created_at: datetime = Field(alias="createdAt")
    created_by: str = Field(alias="createdBy")


class FindingsSummary(AIRBaseModel):
    """Findings summary model."""
    
    total_findings: int = Field(alias="totalFindings")
    critical_count: int = Field(alias="criticalCount")
    high_count: int = Field(alias="highCount")
    medium_count: int = Field(alias="mediumCount")
    low_count: int = Field(alias="lowCount")
    info_count: int = Field(alias="infoCount")


class FindingsStructure(AIRBaseModel):
    """Findings structure model."""
    
    flagged_by_list: List[str] = Field(alias="flaggedByList")
    tactics: List[str]
    tactic_ids: List[str] = Field(alias="tacticIds")
    techniques: List[str]
    technique_ids: List[str] = Field(alias="techniqueIds")
    evidence_categories: List[Dict[str, str]] = Field(alias="evidenceCategories")
    extra_columns: List[Dict[str, Any]] = Field(alias="extraColumns")
    columns_structure: List[Dict[str, Any]] = Field(alias="columnsStructure")


class FindingsFilter(AIRBaseModel):
    """Findings filter model."""
    
    assignment_ids: Optional[List[str]] = Field(default=None, alias="assignmentIds")
    flag_ids: Optional[List[int]] = Field(default=None, alias="flagIds")
    verdict_scores: Optional[List[str]] = Field(default=None, alias="verdictScores")
    created_by: Optional[List[str]] = Field(default=None, alias="createdBy")
    mitre_technique_ids: Optional[List[str]] = Field(default=None, alias="mitreTechniqueIds")
    mitre_tactic_ids: Optional[List[str]] = Field(default=None, alias="mitreTacticIds")


class FindingsRequest(AIRBaseModel):
    """Findings request model."""
    
    take: int = Field(default=50)
    skip: int = Field(default=0)
    filter: Optional[List[Dict[str, Any]]] = Field(default=None)
    global_filter: Optional[FindingsFilter] = Field(default=None, alias="globalFilter")
    sort: Optional[List[Dict[str, str]]] = Field(default=None)


class FindingsResult(AIRBaseModel):
    """Findings result model."""
    
    entities: List[Dict[str, Any]]
    total_count: int = Field(alias="totalCount")
    total_count_with_no_filter: int = Field(alias="totalCountWithNoFilter")


class MitreMatch(AIRBaseModel):
    """MITRE ATT&CK match model."""
    
    technique_id: str = Field(alias="techniqueId")
    technique_name: str = Field(alias="techniqueName")
    tactic: str
    confidence: float


class InvestigationComment(AIRBaseModel):
    """Investigation comment model."""
    
    id: str
    content: str
    evidence_id: Optional[str] = Field(default=None, alias="evidenceId")
    created_at: datetime = Field(alias="createdAt")
    created_by: str = Field(alias="createdBy")


class EvidenceItem(AIRBaseModel):
    """Evidence item for comments."""
    
    evidence: str
    task_assignment_id: str = Field(alias="taskAssignmentId")
    object_id: int = Field(alias="objectId")


class AddNoteRequest(AIRBaseModel):
    """Add note request model."""
    
    items: List[EvidenceItem]
    note: str
    source: str = "EVIDENCE"


class CreateCommentRequest(AIRBaseModel):
    """Create comment request model."""
    
    items: List[EvidenceItem]
    content: str
    mentioned_usernames: List[str] = Field(default_factory=list, alias="mentionedUsernames")
    source: str = "EVIDENCE"


class InvestigationActivity(AIRBaseModel):
    """Investigation activity model."""
    
    id: str
    type: str
    description: str
    user_id: str = Field(alias="userId")
    created_at: datetime = Field(alias="createdAt")
    read: bool = Field(default=False)


class MarkActivityAsReadRequest(AIRBaseModel):
    """Mark activity as read request model."""
    
    mark_all: bool = Field(default=False, alias="markAll")
    activity_id: Optional[int] = Field(default=None, alias="activityId")


class AdvancedFilter(AIRBaseModel):
    """Advanced filter model."""
    
    id: int  # API returns integer ID
    name: str
    organization_id: int = Field(alias="organizationId")
    filter: Optional[Dict[str, Any]] = Field(default=None)  # Match API response
    table_name: Optional[str] = Field(default=None, alias="tableName")
    created_at: datetime = Field(alias="createdAt")
    created_by: Optional[str] = Field(default=None, alias="createdBy")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")


class CreateAdvancedFilterRequest(AIRBaseModel):
    """Create advanced filter request model."""
    
    name: str
    filter: Dict[str, Any]  # Contains main and sections
    table_name: str = Field(alias="tableName")
    organization_id: int = Field(alias="organizationId")


class UpdateAdvancedFilterRequest(AIRBaseModel):
    """Update advanced filter request model."""
    
    name: Optional[str] = Field(default=None)
    filter: Optional[Dict[str, Any]] = Field(default=None)  # Contains main and sections
    table_name: Optional[str] = Field(default=None, alias="tableName")
    organization_id: Optional[int] = Field(default=None, alias="organizationId")


class ExportRequest(AIRBaseModel):
    """Export request model."""
    
    format: str = "csv"  # csv, json, xlsx
    filters: Optional[Dict[str, Any]] = None
    columns: Optional[List[str]] = None 