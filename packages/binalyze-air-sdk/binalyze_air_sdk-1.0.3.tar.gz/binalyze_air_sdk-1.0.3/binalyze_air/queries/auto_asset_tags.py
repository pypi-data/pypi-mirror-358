"""
Auto Asset Tags-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.auto_asset_tags import AutoAssetTag, AutoAssetTagFilter
from ..http_client import HTTPClient


class ListAutoAssetTagsQuery(Query[List[AutoAssetTag]]):
    """Query to list auto asset tags."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[AutoAssetTagFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> List[AutoAssetTag]:
        """Execute the list auto asset tags query."""
        params = {}
        
        # Add default organization filtering if no filter is provided
        if self.filter_params:
            params = self.filter_params.to_params()
        else:
            # Default organization filtering - critical for the API to work
            params["filter[organizationIds]"] = "0"
        
        # Ensure organization filtering is always present
        if "filter[organizationIds]" not in params and "filter[organizationId]" not in params:
            params["filter[organizationIds]"] = "0"
        
        response = self.http_client.get("auto-asset-tag", params=params)
        
        if response.get("success"):
            tags_data = response.get("result", {}).get("entities", [])
            # Use Pydantic parsing with proper field aliasing
            return [AutoAssetTag.model_validate(tag_data) for tag_data in tags_data]
        
        return []


class GetAutoAssetTagQuery(Query[AutoAssetTag]):
    """Query to get auto asset tag by ID."""
    
    def __init__(self, http_client: HTTPClient, tag_id: str):
        self.http_client = http_client
        self.tag_id = tag_id
    
    def execute(self) -> AutoAssetTag:
        """Execute the get auto asset tag query."""
        response = self.http_client.get(f"auto-asset-tag/{self.tag_id}")
        
        if response.get("success"):
            tag_data = response.get("result", {})
            # Use Pydantic parsing with proper field aliasing
            return AutoAssetTag.model_validate(tag_data)
        
        raise Exception(f"Auto asset tag not found: {self.tag_id}") 