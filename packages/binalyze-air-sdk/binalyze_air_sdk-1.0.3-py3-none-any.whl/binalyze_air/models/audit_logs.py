from typing import Optional, List
from pydantic import Field
from ..base import Filter

class AuditLogsFilter(Filter):
    """Filter for audit logs queries."""
    
    search_term: Optional[str] = None
    organization_ids: Optional[List[int]] = None
    start_date: Optional[str] = Field(default=None, alias="startDate")  # ISO 8601 format
    end_date: Optional[str] = Field(default=None, alias="endDate")      # ISO 8601 format
    user_id: Optional[str] = None
    action: Optional[str] = None
    resource: Optional[str] = None 