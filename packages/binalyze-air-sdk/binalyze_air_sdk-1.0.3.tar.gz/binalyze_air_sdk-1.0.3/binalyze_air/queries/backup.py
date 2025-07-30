"""
Backup queries for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any

from ..base import Query
from ..models.backup import (
    BackupHistoryResponse, BackupFilter, BackupDownloadInfo
)
from ..http_client import HTTPClient


class GetBackupHistoryQuery(Query[BackupHistoryResponse]):
    """Query to get backup history with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[BackupFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or BackupFilter()
    
    def execute(self) -> BackupHistoryResponse:
        """Execute the query."""
        params = {}
        
        # Add pagination parameters
        if self.filter_params.page_size is not None:
            params["pageSize"] = self.filter_params.page_size
        if self.filter_params.page_number is not None:
            params["pageNumber"] = self.filter_params.page_number
        if self.filter_params.sort_type is not None:
            params["sortType"] = self.filter_params.sort_type
        if self.filter_params.sort_by is not None:
            params["sortBy"] = self.filter_params.sort_by
        
        # Add filter parameters
        if self.filter_params.search_term is not None:
            params["filter[searchTerm]"] = self.filter_params.search_term
        if self.filter_params.username is not None:
            params["filter[username]"] = self.filter_params.username
        if self.filter_params.source is not None:
            params["filter[source]"] = self.filter_params.source
        if self.filter_params.status is not None:
            params["filter[status]"] = self.filter_params.status
        if self.filter_params.start_date is not None:
            params["filter[startDate]"] = self.filter_params.start_date.isoformat()
        if self.filter_params.end_date is not None:
            params["filter[endDate]"] = self.filter_params.end_date.isoformat()
        if self.filter_params.location is not None:
            params["filter[location]"] = self.filter_params.location
        
        response = self.http_client.get("backup/history", params=params)
        return BackupHistoryResponse(**response["result"])


class GetBackupDownloadQuery(Query[Dict[str, Any]]):
    """Query to get backup download information."""
    
    def __init__(self, http_client: HTTPClient, backup_id: str):
        self.http_client = http_client
        self.backup_id = backup_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query."""
        # This endpoint typically returns a file download or download URL
        response = self.http_client.get(f"backup/{self.backup_id}/download")
        return response 