"""
Recent Activities queries for the Binalyze AIR SDK.
"""

from typing import Optional

from ..base import Query
from ..models.recent_activities import RecentActivitiesList, RecentActivitiesFilter
from ..http_client import HTTPClient


class GetRecentActivitiesQuery(Query[RecentActivitiesList]):
    """Query to get recent activities."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[RecentActivitiesFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or RecentActivitiesFilter()
    
    def execute(self) -> RecentActivitiesList:
        """Execute the query to get recent activities."""
        params = {}
        
        # Add filter parameters
        if self.filter_params.organization_id is not None:
            params['filter[organizationId]'] = str(self.filter_params.organization_id)
        if self.filter_params.type:
            params['filter[type]'] = self.filter_params.type
        if self.filter_params.username:
            params['filter[username]'] = self.filter_params.username
        if self.filter_params.search_term:
            params['filter[searchTerm]'] = self.filter_params.search_term
        
        # Add pagination parameters
        if self.filter_params.page_size:
            params['pageSize'] = str(self.filter_params.page_size)
        if self.filter_params.page_number:
            params['pageNumber'] = str(self.filter_params.page_number)
        if self.filter_params.sort_by:
            params['sortBy'] = self.filter_params.sort_by
        if self.filter_params.sort_type:
            params['sortType'] = self.filter_params.sort_type
        
        response = self.http_client.get('/recent-activities', params=params)
        return RecentActivitiesList(**response['result']) 