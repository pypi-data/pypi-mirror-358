"""
Asset-related queries for the Binalyze AIR SDK.
"""

from typing import List, Dict, Any, Optional

from ..base import Query, PaginatedResponse, APIResponse, PaginatedList
from ..models.assets import Asset, AssetDetail, AssetTask, AssetFilter, AssetTaskFilter
from ..http_client import HTTPClient


class ListAssetsQuery(Query[List[Asset]]):
    """Query to list assets with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[AssetFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or AssetFilter()
    
    def execute(self) -> List[Asset]:
        """Execute the query to list assets."""
        params = self.filter_params.to_params()
        
        # Set default organization_ids if not provided
        if not self.filter_params.organization_ids:
            params["filter[organizationIds]"] = "0"
        
        # Ensure consistent sorting to match API defaults
        if "sortBy" not in params:
            params["sortBy"] = "createdAt"
        if "sortType" not in params:
            params["sortType"] = "ASC"
        
        response = self.http_client.get("assets", params=params)
        
        # Parse the paginated response
        entities = response.get("result", {}).get("entities", [])
        
        # Convert to Asset objects using Pydantic parsing with aliases
        assets = []
        for entity_data in entities:
            # Let Pydantic handle the field mapping via aliases
            asset = Asset.model_validate(entity_data)
            assets.append(asset)
        
        return assets


class GetAssetQuery(Query[AssetDetail]):
    """Query to get a specific asset by ID."""
    
    def __init__(self, http_client: HTTPClient, asset_id: str):
        self.http_client = http_client
        self.asset_id = asset_id
    
    def execute(self) -> AssetDetail:
        """Execute the query to get asset details."""
        response = self.http_client.get(f"assets/{self.asset_id}")
        
        entity_data = response.get("result", {})
        
        # Let Pydantic handle the field mapping via aliases
        return AssetDetail.model_validate(entity_data)


class GetAssetTasksQuery(Query[List[AssetTask]]):
    """Query to get tasks for a specific asset with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, asset_id: str, filter_params: Optional[AssetTaskFilter] = None):
        self.http_client = http_client
        self.asset_id = asset_id
        self.filter_params = filter_params or AssetTaskFilter()
    
    def execute(self) -> List[AssetTask]:
        """Execute the query to get asset tasks."""
        # Get filter parameters
        params = self.filter_params.to_params()
        
        # Provide sensible defaults that mirror the HTTP test defaults if not supplied
        # Default pagination
        if "pageNumber" not in params:
            params["pageNumber"] = 1
        if "pageSize" not in params:
            params["pageSize"] = 10
        # Default sorting
        if "sortBy" not in params:
            params["sortBy"] = "createdAt"
        if "sortType" not in params:
            params["sortType"] = "ASC"
        
        # Make request with parameters
        response = self.http_client.get(f"assets/{self.asset_id}/tasks", params=params)
        
        result_meta = response.get("result", {})
        entities_data = result_meta.get("entities", [])
        
        # Convert to AssetTask objects using Pydantic parsing with aliases
        paginated_tasks = PaginatedList(
            [AssetTask.model_validate(entity) for entity in entities_data],
            total_entity_count=result_meta.get("totalEntityCount"),
            current_page=result_meta.get("currentPage", params.get("pageNumber", 1)),
            page_size=result_meta.get("pageSize", params.get("pageSize", len(entities_data))),
            total_page_count=result_meta.get("totalPageCount"),
        )

        return paginated_tasks


class GetAssetGroupsByOrganizationIdQuery(Query[List[Dict[str, Any]]]):
    """Query to get root asset groups by organization ID."""
    
    def __init__(self, http_client: HTTPClient, organization_id: int):
        self.http_client = http_client
        self.organization_id = organization_id
    
    def execute(self) -> List[Dict[str, Any]]:
        """Execute the query to get asset groups by organization ID."""
        response = self.http_client.get(f"asset-groups/root/{self.organization_id}")
        return response.get("result", [])


class GetAssetGroupsByParentIdQuery(Query[List[Dict[str, Any]]]):
    """Query to get asset groups by parent ID."""
    
    def __init__(self, http_client: HTTPClient, group_id: str):
        self.http_client = http_client
        self.group_id = group_id
    
    def execute(self) -> List[Dict[str, Any]]:
        """Execute the query to get asset groups by parent ID."""
        response = self.http_client.get(f"asset-groups/{self.group_id}")
        return response.get("result", [])


class GetAssetTagsQuery(Query[Dict[str, Any]]):
    """Query to get asset tags with filtering."""
    
    def __init__(self, http_client: HTTPClient, organization_ids: List[int], 
                 page_number: int = 1, page_size: int = 10, sort_by: str = "createdAt",
                 search_term: Optional[str] = None):
        self.http_client = http_client
        self.organization_ids = organization_ids
        self.page_number = page_number
        self.page_size = page_size
        self.sort_by = sort_by
        self.search_term = search_term
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query to get asset tags."""
        params = {
            "filter[organizationIds]": ",".join(map(str, self.organization_ids)),
            "pageNumber": self.page_number,
            "pageSize": self.page_size,
            "sortBy": self.sort_by
        }
        
        if self.search_term:
            params["filter[searchTerm]"] = self.search_term
        
        response = self.http_client.get("asset-tags", params=params)
        return response.get("result", {})


class GetProcessorsByAssetTypeIdQuery(Query[List[Dict[str, Any]]]):
    """Query to get processors by asset type ID."""
    
    def __init__(self, http_client: HTTPClient, asset_type_id: int):
        self.http_client = http_client
        self.asset_type_id = asset_type_id
    
    def execute(self) -> List[Dict[str, Any]]:
        """Execute the query to get processors by asset type ID."""
        response = self.http_client.get(f"processors/asset-type/{self.asset_type_id}")
        return response.get("result", [])


class GetProcessorTypesByAssetTypeQuery(Query[Dict[str, Any]]):
    """Query to get processor types by asset type ID."""
    
    def __init__(self, http_client: HTTPClient, asset_type_id: int):
        self.http_client = http_client
        self.asset_type_id = asset_type_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query to get processor types by asset type ID."""
        response = self.http_client.get(f"processors/type/{self.asset_type_id}")
        return response.get("result", {}) 