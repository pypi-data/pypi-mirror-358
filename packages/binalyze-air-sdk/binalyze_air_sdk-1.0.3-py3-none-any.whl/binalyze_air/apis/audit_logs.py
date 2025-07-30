"""
Audit Logs API for the Binalyze AIR SDK using CQRS pattern.
"""

from typing import List, Optional, Dict, Any
from ..http_client import HTTPClient
from ..models.audit import AuditLog, AuditLogsFilter
from ..queries.audit import ListAuditLogsQuery, ExportAuditLogsQuery


class AuditAPI:
    """Audit logs API aligned with official API specification."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list_logs(self, filter_params: Optional[AuditLogsFilter] = None, organization_ids: Optional[int] = None) -> List[AuditLog]:
        """List audit logs with filtering - Official API endpoint."""
        query = ListAuditLogsQuery(self.http_client, filter_params, organization_ids)
        return query.execute()
    
    def export_logs(self, filter_params: Optional[AuditLogsFilter] = None, format: str = "json", organization_ids: Optional[int] = None) -> Dict[str, Any]:
        """Export audit logs with filtering - Official API endpoint."""
        query = ExportAuditLogsQuery(self.http_client, filter_params, format, organization_ids)
        return query.execute() 