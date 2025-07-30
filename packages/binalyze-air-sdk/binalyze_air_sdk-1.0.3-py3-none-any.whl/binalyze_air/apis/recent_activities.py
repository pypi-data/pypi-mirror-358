"""
Recent Activities API for the Binalyze AIR SDK.
"""

from typing import Optional, Union, Dict, Any

from ..http_client import HTTPClient
from ..models.recent_activities import RecentActivity, RecentActivitiesList, RecentActivitiesFilter, CreateRecentActivityRequest
from ..queries.recent_activities import GetRecentActivitiesQuery
from ..commands.recent_activities import CreateRecentActivityCommand


class RecentActivitiesAPI:
    """Recent Activities API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def get_recent_activities(self, filter_params: Optional[RecentActivitiesFilter] = None) -> RecentActivitiesList:
        """Get recent activities with optional filtering."""
        query = GetRecentActivitiesQuery(self.http_client, filter_params)
        return query.execute()
    
    # Convenience methods for common queries
    def get_recent_activities_by_organization(self, organization_id: Union[int, str]) -> RecentActivitiesList:
        """Get recent activities by organization ID."""
        filter_params = RecentActivitiesFilter()
        filter_params.organization_id = int(organization_id)
        return self.get_recent_activities(filter_params)
    
    def get_recent_activities_by_type(self, activity_type: str, organization_id: Optional[Union[int, str]] = None) -> RecentActivitiesList:
        """Get recent activities by type (e.g., 'asset', 'case', 'task', 'report')."""
        filter_params = RecentActivitiesFilter()
        filter_params.type = activity_type
        if organization_id is not None:
            filter_params.organization_id = int(organization_id)
        return self.get_recent_activities(filter_params)
    
    def get_recent_activities_by_user(self, username: str, organization_id: Optional[Union[int, str]] = None) -> RecentActivitiesList:
        """Get recent activities by username."""
        filter_params = RecentActivitiesFilter()
        filter_params.username = username
        if organization_id is not None:
            filter_params.organization_id = int(organization_id)
        return self.get_recent_activities(filter_params)
    
    def search_recent_activities(self, search_term: str, organization_id: Optional[Union[int, str]] = None) -> RecentActivitiesList:
        """Search recent activities by search term."""
        filter_params = RecentActivitiesFilter()
        filter_params.search_term = search_term
        if organization_id is not None:
            filter_params.organization_id = int(organization_id)
        return self.get_recent_activities(filter_params)
    
    # COMMANDS (Write operations)
    def create_recent_activity(self, activity_data: CreateRecentActivityRequest) -> Dict[str, Any]:
        """Create a new recent activity."""
        command = CreateRecentActivityCommand(self.http_client, activity_data)
        return command.execute()
    
    # Convenience methods
    def get_recent_activities_count(self, organization_id: Optional[Union[int, str]] = None) -> int:
        """Get total recent activities count."""
        filter_params = RecentActivitiesFilter()
        if organization_id is not None:
            filter_params.organization_id = int(organization_id)
        filter_params.page_size = 1  # We only need the count
        
        result = self.get_recent_activities(filter_params)
        return result.total_entity_count or 0 