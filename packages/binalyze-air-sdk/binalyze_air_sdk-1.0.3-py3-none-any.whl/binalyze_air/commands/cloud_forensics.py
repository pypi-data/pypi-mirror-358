"""
Cloud Forensics commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any

from ..base import Command
from ..models.cloud_forensics import (
    CloudAccount, CreateCloudAccountRequest, UpdateCloudAccountRequest, 
    CloudVendorSyncResult, CloudVendor
)
from ..http_client import HTTPClient


class CreateCloudAccountCommand(Command[CloudAccount]):
    """Command to create a new cloud account."""
    
    def __init__(self, http_client: HTTPClient, request: CreateCloudAccountRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> CloudAccount:
        """Execute the command."""
        response = self.http_client.post(
            "cloud-forensics/accounts",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return CloudAccount(**response["result"])


class UpdateCloudAccountCommand(Command[CloudAccount]):
    """Command to update an existing cloud account."""
    
    def __init__(self, http_client: HTTPClient, account_id: str, request: UpdateCloudAccountRequest):
        self.http_client = http_client
        self.account_id = account_id
        self.request = request
    
    def execute(self) -> CloudAccount:
        """Execute the command."""
        response = self.http_client.patch(
            f"cloud-forensics/accounts/{self.account_id}",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return CloudAccount(**response["result"])


class DeleteCloudAccountCommand(Command[Dict[str, Any]]):
    """Command to delete a cloud account."""
    
    def __init__(self, http_client: HTTPClient, account_id: str):
        self.http_client = http_client
        self.account_id = account_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.delete(f"cloud-forensics/accounts/{self.account_id}")
        return response 


class SyncCloudAccountsCommand(Command[CloudVendorSyncResult]):
    """Command to sync cloud accounts."""
    
    def __init__(self, http_client: HTTPClient, cloud_vendor: CloudVendor):
        self.http_client = http_client
        self.cloud_vendor = cloud_vendor
    
    def execute(self) -> CloudVendorSyncResult:
        """Execute the command."""
        response = self.http_client.post(f"cloud-forensics/accounts/sync/{self.cloud_vendor}")
        
        if response.get("success"):
            result_data = response.get("result")
            # Handle null result properly - API may return null
            if result_data is None:
                # Return a minimal CloudVendorSyncResult for null responses
                from datetime import datetime
                # Use model_validate instead of direct constructor to ensure proper field mapping
                return CloudVendorSyncResult.model_validate({
                    "cloudVendor": self.cloud_vendor,
                    "accountsSynced": 0,
                    "totalAssetsDiscovered": 0,
                    "syncStartedAt": datetime.now(),
                    "accountResults": []
                })
            return CloudVendorSyncResult(**result_data)
        
        raise Exception(f"Failed to sync cloud accounts: {response.get('errors', [])}") 