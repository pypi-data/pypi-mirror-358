"""
Notifications queries for the Binalyze AIR SDK.
"""

from typing import Optional, List

from ..base import Query
from ..models.notifications import Notification, NotificationsList, NotificationsFilter
from ..http_client import HTTPClient


class GetNotificationsQuery(Query[NotificationsList]):
    """Query to get notifications with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[NotificationsFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> NotificationsList:
        """Execute the query to get notifications."""
        params = {}
        
        if self.filter_params:
            params = self.filter_params.to_params()
        
        # Ensure organization filter is set (required by API)
        if "filter[organizationIds]" not in params:
            params["filter[organizationIds]"] = "0"
        
        response = self.http_client.get("notifications", params=params)
        
        result_data = response.get("result", {})
        
        # Parse entities
        entities_data = result_data.get("entities", [])
        entities = [Notification.model_validate(entity) for entity in entities_data]
        
        # Create notifications list
        notifications_list = NotificationsList(
            entities=entities,
            currentPage=result_data.get("currentPage", 1),
            pageSize=result_data.get("pageSize", 10),
            totalEntityCount=result_data.get("totalEntityCount", 0),
            totalPageCount=result_data.get("totalPageCount", 0)
        )
        
        return notifications_list


class GetNotificationByIdQuery(Query[Optional[Notification]]):
    """Query to get a specific notification by ID."""
    
    def __init__(self, http_client: HTTPClient, notification_id: str):
        self.http_client = http_client
        self.notification_id = notification_id
    
    def execute(self) -> Optional[Notification]:
        """Execute the query to get notification by ID."""
        # Get all notifications and find the specific one
        # (API doesn't have individual notification endpoint)
        params = {"filter[organizationIds]": "0", "pageSize": "100"}
        response = self.http_client.get("notifications", params=params)
        
        result_data = response.get("result", {})
        entities_data = result_data.get("entities", [])
        
        for entity_data in entities_data:
            if str(entity_data.get("_id")) == str(self.notification_id):
                return Notification.model_validate(entity_data)
        
        return None 