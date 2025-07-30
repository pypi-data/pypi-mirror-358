"""
Backup commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any

from ..base import Command
from ..models.backup import BackupNowRequest
from ..http_client import HTTPClient


class BackupNowCommand(Command[Dict[str, Any]]):
    """Command to create an immediate backup."""
    
    def __init__(self, http_client: HTTPClient, request: BackupNowRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        # Create the filter structure based on the API specification
        filter_data = {}
        
        if self.request.include_endpoint_ids:
            filter_data["includedEndpointIds"] = self.request.include_endpoint_ids
        if self.request.exclude_endpoint_ids:
            filter_data["excludedEndpointIds"] = self.request.exclude_endpoint_ids
        if self.request.organization_ids:
            filter_data["organizationIds"] = self.request.organization_ids
        
        payload = {"filter": filter_data}
        
        response = self.http_client.post("backup/now", json_data=payload)
        return response


class DeleteBackupCommand(Command[Dict[str, Any]]):
    """Command to delete a backup."""
    
    def __init__(self, http_client: HTTPClient, backup_id: str):
        self.http_client = http_client
        self.backup_id = backup_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.delete(f"backup/{self.backup_id}")
        return response 