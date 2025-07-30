"""
Audit-related data models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import Field

from ..base import AIRBaseModel, Filter


class AuditLevel(str, Enum):
    """Audit log level."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditCategory(str, Enum):
    """Audit event category."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_CHANGE = "system_change"
    USER_ACTION = "user_action"
    API_CALL = "api_call"
    POLICY_EXECUTION = "policy_execution"
    TASK_EXECUTION = "task_execution"


class AuditAction(str, Enum):
    """Audit action type."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    LOGIN = "login"
    LOGOUT = "logout"
    DOWNLOAD = "download"
    UPLOAD = "upload"


class AuditLog(AIRBaseModel):
    """Audit log model."""
    
    id: str
    timestamp: datetime
    user_id: Optional[str] = None
    username: Optional[str] = None
    organization_id: int = 0
    category: AuditCategory
    action: AuditAction
    resource_type: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    level: AuditLevel = AuditLevel.INFO
    message: str
    details: Dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    success: bool = True
    error_code: Optional[str] = None
    duration: Optional[int] = None  # milliseconds
    tags: List[str] = []


class AuditSummary(AIRBaseModel):
    """Audit summary model."""
    
    organization_id: int
    date: datetime
    total_events: int = 0
    successful_events: int = 0
    failed_events: int = 0
    authentication_events: int = 0
    authorization_events: int = 0
    data_access_events: int = 0
    system_change_events: int = 0
    user_action_events: int = 0
    api_call_events: int = 0
    unique_users: int = 0
    unique_ips: int = 0
    top_users: List[Dict[str, Any]] = []
    top_actions: List[Dict[str, Any]] = []
    error_summary: List[Dict[str, Any]] = []


class AuditUserActivity(AIRBaseModel):
    """User activity audit model."""
    
    user_id: str
    username: str
    organization_id: int
    date: datetime
    login_count: int = 0
    action_count: int = 0
    failed_login_count: int = 0
    last_login: Optional[datetime] = None
    last_action: Optional[datetime] = None
    unique_ips: List[str] = []
    actions_by_category: Dict[str, int] = {}
    risk_score: float = 0.0


class AuditSystemEvent(AIRBaseModel):
    """System event audit model."""
    
    id: str
    timestamp: datetime
    event_type: str
    severity: AuditLevel
    component: str
    message: str
    details: Dict[str, Any] = {}
    organization_id: int = 0
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None


class AuditLogsFilter(Filter):
    """Filter for audit logs queries - matches NEW API specification exactly (POST with JSON body)."""
    
    # Search and identification
    search_term: Optional[str] = None
    name: Optional[str] = None
    
    # Audit log specific filters
    type: Optional[str] = None  # audit log type filter (changed from List[str] to str)
    performed_by: Optional[str] = None  # user who performed the action
    endpoint_name: Optional[str] = None  # endpoint name filter
    
    # NEW PARAMETERS from updated API spec
    event_source: Optional[str] = None  # NEW: event source filter
    occurred_at: Optional[str] = None  # NEW: timestamp filter
    data_filter: Optional[str] = None  # NEW: data filtering capability
    
    # Organization parameters - changed to single int instead of list
    organization_ids: Optional[int] = Field(default=None, alias="organizationIds")  # API expects camelCase
    all_organizations: Optional[bool] = None  # true/false
    
    def to_json_body(self) -> Dict[str, Any]:
        """Convert filter to JSON body for POST request - NEW API FORMAT."""
        body = {}
        
        # Pagination parameters (top level in body)
        if self.page_number is not None:
            body["pageNumber"] = self.page_number
        if self.page_size is not None:
            body["pageSize"] = self.page_size
        if self.sort_by is not None:
            body["sortBy"] = self.sort_by
        if self.sort_type is not None:
            body["sortType"] = self.sort_type
        
        # Filter object (nested in body)
        filter_obj = {}
        
        if self.search_term is not None:
            filter_obj["searchTerm"] = self.search_term
        if self.name is not None:
            filter_obj["name"] = self.name
        if self.type is not None:
            filter_obj["type"] = self.type
        if self.performed_by is not None:
            filter_obj["performedBy"] = self.performed_by
        if self.endpoint_name is not None:
            filter_obj["endpointName"] = self.endpoint_name
        
        # NEW PARAMETERS
        if self.event_source is not None:
            filter_obj["eventSource"] = self.event_source
        if self.occurred_at is not None:
            filter_obj["occurredAt"] = self.occurred_at
        if self.data_filter is not None:
            filter_obj["dataFilter"] = self.data_filter
        
        # Organization parameters - API requires organizationIds to be empty
        # Don't include organizationIds in filter as API requires it to be empty
        # if self.organization_ids is not None:
        #     filter_obj["organizationIds"] = self.organization_ids
        if self.all_organizations is not None:
            filter_obj["allOrganizations"] = self.all_organizations
        
        # Only add filter object if it has content
        if filter_obj:
            body["filter"] = filter_obj
        
        return body

    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters with correct camelCase naming."""
        # Get base parameters
        params = super().to_params()
        
        # Fix organization_ids parameter name to match API specification
        if 'filter[organization_ids]' in params:
            # Move from snake_case to camelCase as required by API
            params['filter[organizationIds]'] = params.pop('filter[organization_ids]')
        
        return params


class AuditFilter(Filter):
    """Filter for audit queries."""
    
    user_id: Optional[str] = None
    username: Optional[str] = None
    category: Optional[List[AuditCategory]] = None
    action: Optional[List[AuditAction]] = None
    level: Optional[List[AuditLevel]] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    success: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    correlation_id: Optional[str] = None


class AuditExportRequest(AIRBaseModel):
    """Request model for exporting audit logs."""
    
    filter_params: AuditFilter
    format: str = "json"  # json, csv, excel
    include_details: bool = True
    organization_ids: List[int] = []


class AuditRetentionPolicy(AIRBaseModel):
    """Audit retention policy model."""
    
    organization_id: int
    retention_days: int = 365
    auto_archive: bool = True
    archive_location: Optional[str] = None
    compress_archives: bool = True
    delete_after_archive: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str 