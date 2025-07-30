"""
Preset Filters queries for the Binalyze AIR SDK.
"""

from typing import Optional

from ..base import Query
from ..models.preset_filters import PresetFilter, PresetFiltersList, PresetFiltersFilter
from ..http_client import HTTPClient


class GetPresetFiltersQuery(Query[PresetFiltersList]):
    """Query to get preset filters."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[PresetFiltersFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or PresetFiltersFilter()
    
    def execute(self) -> PresetFiltersList:
        """Execute the query to get preset filters."""
        params = {}
        
        # Add filter parameters
        if self.filter_params.organization_id is not None:
            params['filter[organizationId]'] = str(self.filter_params.organization_id)
        if self.filter_params.type:
            params['filter[type]'] = self.filter_params.type
        if self.filter_params.name:
            params['filter[name]'] = self.filter_params.name
        if self.filter_params.created_by:
            params['filter[createdBy]'] = self.filter_params.created_by
        
        # Add pagination parameters
        if self.filter_params.page_size:
            params['pageSize'] = str(self.filter_params.page_size)
        if self.filter_params.page_number:
            params['pageNumber'] = str(self.filter_params.page_number)
        if self.filter_params.sort_by:
            params['sortBy'] = self.filter_params.sort_by
        if self.filter_params.sort_type:
            params['sortType'] = self.filter_params.sort_type
        
        response = self.http_client.get('/preset-filters', params=params)
        return PresetFiltersList(**response['result'])


class GetPresetFilterByIdQuery(Query[Optional[PresetFilter]]):
    """Query to get a specific preset filter by ID."""
    
    def __init__(self, http_client: HTTPClient, filter_id: str):
        self.http_client = http_client
        self.filter_id = filter_id
    
    def execute(self) -> Optional[PresetFilter]:
        """Execute the query to get a preset filter by ID."""
        try:
            response = self.http_client.get(f'/preset-filters/{self.filter_id}')
            return PresetFilter(**response['result'])
        except Exception:
            return None 