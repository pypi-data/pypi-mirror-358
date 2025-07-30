"""
Asset-related commands for the Binalyze AIR SDK.
Fixed to match API documentation exactly.
"""

from typing import List, Union, Optional, Dict, Any

from ..base import Command
from ..models.assets import AssetFilter
from ..http_client import HTTPClient


class RebootAssetsCommand(Command[Dict[str, Any]]):
    """Command to reboot assets by filter - FIXED to match API documentation."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
    
    def execute(self) -> Dict[str, Any]:
        """Execute the reboot command with correct payload structure."""
        # Use the correct payload structure as per API documentation
        payload = {
            "filter": self.asset_filter.to_filter_dict()
        }
        
        # FIXED: Correct endpoint URL (confirmed from API docs)
        return self.http_client.post("assets/tasks/reboot", json_data=payload)


class ShutdownAssetsCommand(Command[Dict[str, Any]]):
    """Command to shutdown assets by filter - FIXED to match API documentation."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
    
    def execute(self) -> Dict[str, Any]:
        """Execute the shutdown command with correct payload structure."""
        payload = {
            "filter": self.asset_filter.to_filter_dict()
        }
        
        # FIXED: Correct endpoint URL (following same pattern as reboot)
        return self.http_client.post("assets/tasks/shutdown", json_data=payload)


class IsolateAssetsCommand(Command[Dict[str, Any]]):
    """Command to isolate assets by filter - FIXED to match API documentation."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter,
        isolation_settings: Optional[Dict[str, Any]] = None
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
        self.isolation_settings = isolation_settings or {}
    
    def execute(self) -> Dict[str, Any]:
        """Execute the isolation command with correct payload structure."""
        payload = {
            "enabled": True,  # Required field for isolation
            "filter": self.asset_filter.to_filter_dict()
        }
        
        # Add isolation settings if provided
        if self.isolation_settings:
            payload.update(self.isolation_settings)
        
        # FIXED: Correct endpoint URL and payload
        return self.http_client.post("assets/tasks/isolation", json_data=payload)


class UnisolateAssetsCommand(Command[Dict[str, Any]]):
    """Command to unisolate (remove isolation from) assets - FIXED to match API documentation."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
    
    def execute(self) -> Dict[str, Any]:
        """Execute the unisolate command with correct payload structure."""
        payload = {
            "enabled": False,  # Disable isolation for unisolate
            "filter": self.asset_filter.to_filter_dict()
        }
        
        # FIXED: Correct endpoint URL and payload
        return self.http_client.post("assets/tasks/isolation", json_data=payload)


class LogRetrievalCommand(Command[Dict[str, Any]]):
    """Command to retrieve logs from assets - FIXED endpoint URL and payload structure."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter,
        log_settings: Optional[Dict[str, Any]] = None
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
        self.log_settings = log_settings or {}
    
    def execute(self) -> Dict[str, Any]:
        """Execute the log retrieval command with correct endpoint and payload."""
        payload = {
            "filter": self.asset_filter.to_filter_dict()
        }
        
        # Add log retrieval settings if provided
        if self.log_settings:
            payload.update(self.log_settings)
        
        # FIXED: Correct endpoint URL to match API specification
        return self.http_client.post("assets/tasks/retrieve-logs", json_data=payload)


class VersionUpdateCommand(Command[Dict[str, Any]]):
    """Command to update version on assets - FIXED to match API documentation."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter,
        update_settings: Optional[Dict[str, Any]] = None
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
        self.update_settings = update_settings or {}
    
    def execute(self) -> Dict[str, Any]:
        """Execute the version update command with correct payload structure."""
        payload = {
            "filter": self.asset_filter.to_filter_dict()
        }
        
        # Add version update settings if provided
        if self.update_settings:
            payload.update(self.update_settings)
        
        # FIXED: Correct endpoint URL (following tasks pattern)
        return self.http_client.post("assets/tasks/version-update", json_data=payload)


class UninstallAssetsCommand(Command[Dict[str, Any]]):
    """Command to uninstall assets without purging data - FIXED endpoint URL and HTTP method."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
    
    def execute(self) -> Dict[str, Any]:
        """Execute the uninstall command with correct endpoint, HTTP method and payload structure."""
        payload = {
            "filter": self.asset_filter.to_filter_dict()
        }
        
        # FIXED: Correct endpoint URL and HTTP method (DELETE, not POST)
        return self.http_client.delete("assets/uninstall-without-purge", json_data=payload)


class PurgeAndUninstallAssetsCommand(Command[Dict[str, Any]]):
    """Command to purge and uninstall assets - FIXED endpoint URL and HTTP method."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
    
    def execute(self) -> Dict[str, Any]:
        """Execute the purge and uninstall command with correct endpoint, HTTP method and payload."""
        payload = {
            "filter": self.asset_filter.to_filter_dict()
        }
        
        # FIXED: Correct endpoint URL and HTTP method (DELETE, not POST)
        return self.http_client.delete("assets/purge-and-uninstall", json_data=payload)


class AddTagsToAssetsCommand(Command[Dict[str, Any]]):
    """Command to add tags to assets - FIXED endpoint URL and payload structure."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter,
        tags: List[str]
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
        self.tags = tags
    
    def execute(self) -> Dict[str, Any]:
        """Execute the add tags command with correct endpoint and payload structure."""
        payload = {
            "filter": self.asset_filter.to_filter_dict(),
            "tags": self.tags
        }
        
        # FIXED: Correct endpoint URL (from API documentation) 
        return self.http_client.post("assets/tags", json_data=payload)


class RemoveTagsFromAssetsCommand(Command[Dict[str, Any]]):
    """Command to remove tags from assets by filter - FIXED to match API documentation."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        asset_filter: AssetFilter,
        tags: List[str]
    ):
        self.http_client = http_client
        self.asset_filter = asset_filter
        self.tags = tags
    
    def execute(self) -> Dict[str, Any]:
        """Execute the remove tags command with correct payload structure."""
        payload = {
            "filter": self.asset_filter.to_filter_dict(),
            "tags": self.tags
        }
        
        # FIXED: Correct endpoint URL and HTTP method
        return self.http_client.delete("assets/tags", json_data=payload)


class DeleteAssetTagByIdCommand(Command[Dict[str, Any]]):
    """Command to delete an asset tag by ID."""
    
    def __init__(self, http_client: HTTPClient, organization_id: int, tag_id: str):
        self.http_client = http_client
        self.organization_id = organization_id
        self.tag_id = tag_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete asset tag command."""
        return self.http_client.delete(f"asset-tags/{self.organization_id}/{self.tag_id}")


class DeleteAssetTagsByOrganizationIdCommand(Command[Dict[str, Any]]):
    """Command to delete asset tags by organization ID."""
    
    def __init__(self, http_client: HTTPClient, organization_id: int):
        self.http_client = http_client
        self.organization_id = organization_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete asset tags by organization ID command."""
        return self.http_client.delete(f"asset-tags/{self.organization_id}/all")


# Convenience functions for backward compatibility
def create_asset_filter_from_endpoint_ids(
    endpoint_ids: Union[str, List[str]], 
    organization_ids: Optional[List[Union[int, str]]] = None
) -> AssetFilter:
    """
    Create an AssetFilter from endpoint IDs - helper function.
    
    Args:
        endpoint_ids: Single endpoint ID or list of endpoint IDs
        organization_ids: Optional list of organization IDs
        
    Returns:
        AssetFilter: Configured filter object
    """
    # Convert single endpoint ID to list
    if isinstance(endpoint_ids, str):
        endpoint_ids = [endpoint_ids]
    
    # Set default organization IDs if not provided and convert to integers
    if organization_ids is None:
        org_ids = [0]
    else:
        org_ids = [int(org_id) for org_id in organization_ids]
    
    # Create and return the filter
    return AssetFilter(
        included_endpoint_ids=endpoint_ids,
        organization_ids=org_ids
    )


# Export the main corrected classes
__all__ = [
    # Main corrected commands
    'RebootAssetsCommand',
    'ShutdownAssetsCommand', 
    'IsolateAssetsCommand',
    'UnisolateAssetsCommand',
    'LogRetrievalCommand',
    'VersionUpdateCommand',
    'UninstallAssetsCommand',
    'PurgeAndUninstallAssetsCommand',
    'AddTagsToAssetsCommand',
    'RemoveTagsFromAssetsCommand',
    'DeleteAssetTagByIdCommand',
    'DeleteAssetTagsByOrganizationIdCommand',
    
    # Utility functions
    'create_asset_filter_from_endpoint_ids'
] 