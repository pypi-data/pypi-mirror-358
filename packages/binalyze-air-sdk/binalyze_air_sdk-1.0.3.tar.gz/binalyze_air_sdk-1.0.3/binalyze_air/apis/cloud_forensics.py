"""
Cloud Forensics API for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any

from ..http_client import HTTPClient
from ..models.cloud_forensics import (
    CloudAccount, CloudAccountsPaginatedResponse, CloudAccountFilter,
    CreateCloudAccountRequest, UpdateCloudAccountRequest, CloudAccountSyncResult,
    CloudVendorSyncResult, CloudVendor
)
from ..queries.cloud_forensics import (
    ListCloudAccountsQuery, GetCloudAccountQuery, ExportCloudAccountsQuery,
    SyncCloudAccountQuery, SyncCloudAccountsByVendorQuery
)
from ..commands.cloud_forensics import (
    CreateCloudAccountCommand, UpdateCloudAccountCommand, DeleteCloudAccountCommand
)


class CloudForensicsAPI:
    """Cloud Forensics API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list_accounts(self, filter_params: Optional[CloudAccountFilter] = None) -> CloudAccountsPaginatedResponse:
        """List cloud accounts with optional filtering."""
        query = ListCloudAccountsQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_account(self, account_id: str) -> CloudAccount:
        """Get a specific cloud account by ID."""
        query = GetCloudAccountQuery(self.http_client, account_id)
        return query.execute()
    
    def export_accounts(self, filter_params: Optional[CloudAccountFilter] = None) -> Dict[str, Any]:
        """Export cloud accounts data."""
        query = ExportCloudAccountsQuery(self.http_client, filter_params)
        return query.execute()
    
    def sync_account(self, account_id: str) -> CloudAccountSyncResult:
        """Sync a specific cloud account by ID."""
        query = SyncCloudAccountQuery(self.http_client, account_id)
        return query.execute()
    
    def sync_accounts_by_vendor(self, cloud_vendor: CloudVendor) -> CloudVendorSyncResult:
        """Sync all cloud accounts by vendor."""
        query = SyncCloudAccountsByVendorQuery(self.http_client, cloud_vendor)
        return query.execute()
    
    # COMMANDS (Write operations)
    def create_account(self, request: CreateCloudAccountRequest) -> CloudAccount:
        """Create a new cloud account."""
        command = CreateCloudAccountCommand(self.http_client, request)
        return command.execute()
    
    def update_account(self, account_id: str, request: UpdateCloudAccountRequest) -> CloudAccount:
        """Update an existing cloud account."""
        command = UpdateCloudAccountCommand(self.http_client, account_id, request)
        return command.execute()
    
    def delete_account(self, account_id: str) -> Dict[str, Any]:
        """Delete a cloud account."""
        command = DeleteCloudAccountCommand(self.http_client, account_id)
        return command.execute()
    
    # Convenience methods
    def list_aws_accounts(self, filter_params: Optional[CloudAccountFilter] = None) -> CloudAccountsPaginatedResponse:
        """List AWS cloud accounts."""
        if filter_params is None:
            filter_params = CloudAccountFilter()
        filter_params.cloud_vendor = CloudVendor.AWS
        return self.list_accounts(filter_params)
    
    def list_azure_accounts(self, filter_params: Optional[CloudAccountFilter] = None) -> CloudAccountsPaginatedResponse:
        """List Azure cloud accounts."""
        if filter_params is None:
            filter_params = CloudAccountFilter()
        filter_params.cloud_vendor = CloudVendor.AZURE
        return self.list_accounts(filter_params)
    
    def sync_all_aws_accounts(self) -> CloudVendorSyncResult:
        """Sync all AWS accounts."""
        return self.sync_accounts_by_vendor(CloudVendor.AWS)
    
    def sync_all_azure_accounts(self) -> CloudVendorSyncResult:
        """Sync all Azure accounts."""
        return self.sync_accounts_by_vendor(CloudVendor.AZURE)
    
    def get_account_summary(self, filter_params: Optional[CloudAccountFilter] = None) -> Dict[str, Any]:
        """Get a summary of cloud accounts including counts by vendor and status."""
        accounts = self.list_accounts(filter_params)
        
        summary = {
            "total_accounts": len(accounts.entities),
            "by_vendor": {},
            "by_status": {},
            "total_assets": 0
        }
        
        for account in accounts.entities:
            # Count by vendor (handle both enum and string cases)
            vendor = account.cloud_vendor.value if hasattr(account.cloud_vendor, 'value') else str(account.cloud_vendor)
            summary["by_vendor"][vendor] = summary["by_vendor"].get(vendor, 0) + 1
            
            # Count by status (handle both enum and string cases)
            status = account.status.value if hasattr(account.status, 'value') else str(account.status)
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
            
            # Sum total assets
            summary["total_assets"] += account.detected_assets_count
        
        return summary 