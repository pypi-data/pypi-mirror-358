"""
Auto Asset Tags API for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any, Union

from ..http_client import HTTPClient
from ..models.auto_asset_tags import (
    AutoAssetTag, AutoAssetTagFilter, CreateAutoAssetTagRequest, UpdateAutoAssetTagRequest,
    StartTaggingRequest, TaggingResponse
)
from ..queries.auto_asset_tags import ListAutoAssetTagsQuery, GetAutoAssetTagQuery
from ..commands.auto_asset_tags import (
    CreateAutoAssetTagCommand, UpdateAutoAssetTagCommand, DeleteAutoAssetTagCommand,
    StartTaggingCommand
)


class AutoAssetTagsAPI:
    """Auto Asset Tags API with CQRS pattern - separated queries and commands."""

    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client

    # QUERIES (Read operations)
    def list(self, filter_params: Optional[AutoAssetTagFilter] = None) -> List[AutoAssetTag]:
        """List auto asset tags with optional filtering."""
        query = ListAutoAssetTagsQuery(self.http_client, filter_params)
        return query.execute()

    def get(self, tag_id: str) -> AutoAssetTag:
        """Get a specific auto asset tag by ID."""
        query = GetAutoAssetTagQuery(self.http_client, tag_id)
        return query.execute()

    def get_by_id(self, tag_id: str) -> AutoAssetTag:
        """Get a specific auto asset tag by ID - alias for get."""
        return self.get(tag_id)

    # COMMANDS (Write operations)
    def create(self, request: Union[CreateAutoAssetTagRequest, Dict[str, Any]]) -> AutoAssetTag:
        """Create a new auto asset tag."""
        command = CreateAutoAssetTagCommand(self.http_client, request)
        return command.execute()

    def update(
        self,
        tag_id_or_data: Union[str, Dict[str, Any]],
        request: Optional[Union[UpdateAutoAssetTagRequest, Dict[str, Any]]] = None
    ) -> AutoAssetTag:
        """Update an existing auto asset tag."""
        # Handle both signatures: update(tag_id, request) and update(data_dict)
        if isinstance(tag_id_or_data, str) and request is not None:
            # Traditional signature: update(tag_id, request)
            command = UpdateAutoAssetTagCommand(self.http_client, tag_id_or_data, request)
        elif isinstance(tag_id_or_data, dict):
            # Dict signature: update(data_dict) where data_dict contains 'id'
            tag_id = tag_id_or_data.get('id')
            if not tag_id:
                raise ValueError("Tag ID must be provided in data dict or as separate parameter")
            command = UpdateAutoAssetTagCommand(self.http_client, tag_id, tag_id_or_data)
        else:
            raise ValueError("Invalid arguments for update")

        return command.execute()

    def delete(self, tag_id: str) -> Dict[str, Any]:
        """Delete an auto asset tag."""
        command = DeleteAutoAssetTagCommand(self.http_client, tag_id)
        return command.execute()

    def delete_by_id(self, tag_id: str) -> Dict[str, Any]:
        """Delete an auto asset tag by ID - alias for delete."""
        return self.delete(tag_id)

    def start_tagging(self, request: Union[StartTaggingRequest, Dict[str, Any]]) -> TaggingResponse:
        """Start the tagging process for auto asset tags."""
        command = StartTaggingCommand(self.http_client, request)
        return command.execute()
