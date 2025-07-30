"""
Assets API for the Binalyze AIR SDK using CQRS pattern.
"""

from typing import List, Optional, Dict, Any, Union
from ..http_client import HTTPClient
from ..models.assets import Asset, AssetDetail, AssetTask, AssetFilter, AssetTaskFilter
from ..queries.assets import (
    ListAssetsQuery,
    GetAssetQuery,
    GetAssetTasksQuery,
    GetAssetGroupsByOrganizationIdQuery,
    GetAssetGroupsByParentIdQuery,
    GetAssetTagsQuery,
    GetProcessorsByAssetTypeIdQuery,
    GetProcessorTypesByAssetTypeQuery,
)
from ..commands.assets import (
    IsolateAssetsCommand,
    UnisolateAssetsCommand,
    RebootAssetsCommand,
    ShutdownAssetsCommand,
    AddTagsToAssetsCommand,
    RemoveTagsFromAssetsCommand,
    UninstallAssetsCommand,
    LogRetrievalCommand,
    VersionUpdateCommand,
    DeleteAssetTagByIdCommand,
    DeleteAssetTagsByOrganizationIdCommand,
)


class AssetsAPI:
    """Assets API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, filter_params: Optional[AssetFilter] = None) -> List[Asset]:
        """List assets with optional filtering."""
        query = ListAssetsQuery(self.http_client, filter_params)
        return query.execute()
    
    def get(self, asset_id: str) -> AssetDetail:
        """Get a specific asset by ID."""
        query = GetAssetQuery(self.http_client, asset_id)
        return query.execute()
    
    def get_tasks(self, asset_id: str, filter_params: Optional[AssetTaskFilter] = None) -> List[AssetTask]:
        """Get tasks for a specific asset with optional filtering."""
        query = GetAssetTasksQuery(self.http_client, asset_id, filter_params)
        return query.execute()
    
    def get_asset_groups_by_organization_id(self, organization_id: int) -> List[Dict[str, Any]]:
        """Get root asset groups by organization ID."""
        query = GetAssetGroupsByOrganizationIdQuery(self.http_client, organization_id)
        return query.execute()
    
    def get_asset_groups_by_parent_id(self, group_id: str) -> List[Dict[str, Any]]:
        """Get asset groups by parent ID."""
        query = GetAssetGroupsByParentIdQuery(self.http_client, group_id)
        return query.execute()
    
    def get_asset_tags(self, organization_ids: List[int], page_number: int = 1, 
                      page_size: int = 10, sort_by: str = "createdAt",
                      search_term: Optional[str] = None) -> Dict[str, Any]:
        """Get asset tags with filtering."""
        query = GetAssetTagsQuery(self.http_client, organization_ids, page_number, 
                                page_size, sort_by, search_term)
        return query.execute()
    
    def get_processors_by_asset_type_id(self, asset_type_id: int) -> List[Dict[str, Any]]:
        """Get processors by asset type ID."""
        query = GetProcessorsByAssetTypeIdQuery(self.http_client, asset_type_id)
        return query.execute()
    
    def get_processor_types_by_asset_type(self, asset_type_id: int) -> Dict[str, Any]:
        """Get processor types by asset type ID."""
        query = GetProcessorTypesByAssetTypeQuery(self.http_client, asset_type_id)
        return query.execute()
    
    # COMMANDS (Write operations)
    def isolate(self, endpoint_ids: Union[str, List[str]], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Isolate one or more assets."""
        # Create AssetFilter from endpoint IDs for backward compatibility
        from ..commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = IsolateAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def unisolate(self, endpoint_ids: Union[str, List[str]], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Remove isolation from one or more assets."""
        from ..commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = UnisolateAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def reboot(self, endpoint_ids: Union[str, List[str]], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Reboot one or more assets."""
        from ..commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = RebootAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def shutdown(self, endpoint_ids: Union[str, List[str]], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Shutdown one or more assets."""
        from ..commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = ShutdownAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def add_tags(self, endpoint_ids: List[str], tags: List[str], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Add tags to assets."""
        from ..commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = AddTagsToAssetsCommand(self.http_client, asset_filter, tags)
        return command.execute()
    
    def remove_tags(self, endpoint_ids: List[str], tags: List[str], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Remove tags from assets."""
        from ..commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = RemoveTagsFromAssetsCommand(self.http_client, asset_filter, tags)
        return command.execute()
    
    def delete_asset_tag_by_id(self, organization_id: int, tag_id: str) -> Dict[str, Any]:
        """Delete an asset tag by ID."""
        command = DeleteAssetTagByIdCommand(self.http_client, organization_id, tag_id)
        return command.execute()
    
    def delete_asset_tags_by_organization_id(self, organization_id: int) -> Dict[str, Any]:
        """Delete asset tags by organization ID."""
        command = DeleteAssetTagsByOrganizationIdCommand(self.http_client, organization_id)
        return command.execute()
    
    def uninstall(self, endpoint_ids: List[str], purge_data: bool = False, organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Uninstall assets with optional data purging."""
        from ..commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        if purge_data:
            from ..commands.assets import PurgeAndUninstallAssetsCommand
            command = PurgeAndUninstallAssetsCommand(self.http_client, asset_filter)
        else:
            from ..commands.assets import UninstallAssetsCommand
            command = UninstallAssetsCommand(self.http_client, asset_filter)
        return command.execute()
    
    def retrieve_logs(self, endpoint_ids: List[str], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Retrieve logs from assets."""
        from ..commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = LogRetrievalCommand(self.http_client, asset_filter)
        return command.execute()
    
    def version_update(self, endpoint_ids: List[str], organization_ids: Optional[List[Union[int, str]]] = None) -> Dict[str, Any]:
        """Update version on assets."""
        from ..commands.assets import create_asset_filter_from_endpoint_ids
        asset_filter = create_asset_filter_from_endpoint_ids(endpoint_ids, organization_ids)
        command = VersionUpdateCommand(self.http_client, asset_filter)
        return command.execute() 