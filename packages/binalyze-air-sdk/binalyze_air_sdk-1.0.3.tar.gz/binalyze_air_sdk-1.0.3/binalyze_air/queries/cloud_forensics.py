"""
Cloud Forensics queries for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any

from ..base import Query
from ..models.cloud_forensics import (
    CloudAccount, CloudAccountsPaginatedResponse, CloudAccountFilter,
    CloudAccountSyncResult, CloudVendorSyncResult, CloudVendor
)
from ..http_client import HTTPClient


class ListCloudAccountsQuery(Query[CloudAccountsPaginatedResponse]):
    """Query to list cloud accounts with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[CloudAccountFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or CloudAccountFilter()
    
    def execute(self) -> CloudAccountsPaginatedResponse:
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
        
        # Add required filter parameters (API requires these)
        # Default to AWS and organization ID 0 if not specified
        cloud_vendor = self.filter_params.cloud_vendor or CloudVendor.AWS
        # Handle both enum and string values - FIXED
        if hasattr(cloud_vendor, 'value'):
            params["filter[cloudVendor]"] = cloud_vendor.value
        else:
            params["filter[cloudVendor]"] = cloud_vendor
        
        organization_ids = self.filter_params.organization_ids or [0]
        params["filter[organizationIds]"] = ",".join(map(str, organization_ids))
        
        # Add optional filter parameters
        if self.filter_params.search_term is not None:
            params["filter[searchTerm]"] = self.filter_params.search_term
        if self.filter_params.status is not None:
            # Handle both enum and string values - FIXED
            if hasattr(self.filter_params.status, 'value'):
                params["filter[status]"] = self.filter_params.status.value
            else:
                params["filter[status]"] = self.filter_params.status
        
        response = self.http_client.get("cloud-forensics/accounts", params=params)
        return CloudAccountsPaginatedResponse(**response["result"])


class GetCloudAccountQuery(Query[CloudAccount]):
    """Query to get a specific cloud account by ID."""
    
    def __init__(self, http_client: HTTPClient, account_id: str):
        self.http_client = http_client
        self.account_id = account_id
    
    def execute(self) -> CloudAccount:
        """Execute the query."""
        response = self.http_client.get(f"cloud-forensics/accounts/{self.account_id}")
        return CloudAccount(**response["result"])


class ExportCloudAccountsQuery(Query[Dict[str, Any]]):
    """Query to export cloud accounts data."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[CloudAccountFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or CloudAccountFilter()
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query."""
        params = {}
        
        # Add required filter parameters (API requires these)
        # Default to AWS and organization ID 0 if not specified
        cloud_vendor = self.filter_params.cloud_vendor or CloudVendor.AWS
        # Handle both enum and string values - FIXED
        if hasattr(cloud_vendor, 'value'):
            params["filter[cloudVendor]"] = cloud_vendor.value
        else:
            params["filter[cloudVendor]"] = cloud_vendor
        
        organization_ids = self.filter_params.organization_ids or [0]
        params["filter[organizationIds]"] = ",".join(map(str, organization_ids))
        
        # Add optional filter parameters for export
        if self.filter_params.search_term is not None:
            params["filter[searchTerm]"] = self.filter_params.search_term
        if self.filter_params.status is not None:
            # Handle both enum and string values - FIXED
            if hasattr(self.filter_params.status, 'value'):
                params["filter[status]"] = self.filter_params.status.value
            else:
                params["filter[status]"] = self.filter_params.status
        
        response = self.http_client.get("cloud-forensics/accounts/export", params=params)
        return response


class SyncCloudAccountQuery(Query[CloudAccountSyncResult]):
    """Query to sync a specific cloud account by ID."""
    
    def __init__(self, http_client: HTTPClient, account_id: str):
        self.http_client = http_client
        self.account_id = account_id
    
    def execute(self) -> CloudAccountSyncResult:
        """Execute the query."""
        response = self.http_client.get(f"cloud-forensics/accounts/sync/{self.account_id}")
        return CloudAccountSyncResult(**response["result"])


class SyncCloudAccountsByVendorQuery(Query[CloudVendorSyncResult]):
    """Query to sync all cloud accounts by vendor."""
    
    def __init__(self, http_client: HTTPClient, cloud_vendor: CloudVendor):
        self.http_client = http_client
        self.cloud_vendor = cloud_vendor
    
    def execute(self) -> CloudVendorSyncResult:
        """Execute the query."""
        response = self.http_client.get(f"cloud-forensics/accounts/sync/{self.cloud_vendor.value}/all")
        # Handle case where result might be None
        result_data = response.get("result") or {}
        return CloudVendorSyncResult(**result_data) 