"""
Notifications API for the Binalyze AIR SDK.
"""

from typing import Optional, Union, Dict, Any

from ..http_client import HTTPClient
from ..models.notifications import Notification, NotificationsList, NotificationsFilter, NotificationType, NotificationLevel
from ..queries.notifications import GetNotificationsQuery, GetNotificationByIdQuery
from ..commands.notifications import DeleteAllNotificationsCommand, MarkAllAsReadCommand, MarkAsReadByIdCommand


class NotificationsAPI:
    """Notifications API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def get_notifications(self, filter_params: Optional[NotificationsFilter] = None) -> NotificationsList:
        """Get notifications with optional filtering."""
        query = GetNotificationsQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_notification_by_id(self, notification_id: Union[int, str]) -> Optional[Notification]:
        """Get a specific notification by ID."""
        query = GetNotificationByIdQuery(self.http_client, str(notification_id))
        return query.execute()
    
    # Convenience methods for common queries
    def get_unread_notifications(self, organization_ids: Union[int, list] = 0) -> NotificationsList:
        """Get unread notifications."""
        # Create filter with explicit field values
        filter_params = NotificationsFilter()
        filter_params.is_read = False
        if isinstance(organization_ids, list):
            filter_params.organization_ids = organization_ids
        else:
            filter_params.organization_ids = organization_ids
        
        return self.get_notifications(filter_params)
    
    def get_notifications_by_type(self, notification_type: Union[str, NotificationType], organization_ids: Union[int, list] = 0) -> NotificationsList:
        """Get notifications by type."""
        # Create filter with explicit field values
        filter_params = NotificationsFilter()
        if isinstance(notification_type, str):
            filter_params.type = NotificationType(notification_type)
        else:
            filter_params.type = notification_type
        if isinstance(organization_ids, list):
            filter_params.organization_ids = organization_ids
        else:
            filter_params.organization_ids = organization_ids
        
        return self.get_notifications(filter_params)
    
    def get_notifications_by_level(self, level: Union[str, NotificationLevel], organization_ids: Union[int, list] = 0) -> NotificationsList:
        """Get notifications by level."""
        # Create filter with explicit field values  
        filter_params = NotificationsFilter()
        if isinstance(level, str):
            filter_params.level = NotificationLevel(level)
        else:
            filter_params.level = level
        if isinstance(organization_ids, list):
            filter_params.organization_ids = organization_ids
        else:
            filter_params.organization_ids = organization_ids
        
        return self.get_notifications(filter_params)
    
    # COMMANDS (Write operations)
    def delete_all_notifications(self) -> Dict[str, Any]:
        """Delete all notifications for the current user."""
        command = DeleteAllNotificationsCommand(self.http_client)
        return command.execute()
    
    def mark_all_as_read(self) -> Dict[str, Any]:
        """Mark all notifications as read."""
        command = MarkAllAsReadCommand(self.http_client)
        return command.execute()
    
    def mark_as_read_by_id(self, notification_id: Union[int, str]) -> Dict[str, Any]:
        """Mark a specific notification as read by ID."""
        command = MarkAsReadByIdCommand(self.http_client, notification_id)
        return command.execute()
    
    # Convenience methods
    def get_notification_count(self, organization_ids: Union[int, list] = 0) -> int:
        """Get total notification count."""
        # Create filter with explicit field values
        filter_params = NotificationsFilter()
        if isinstance(organization_ids, list):
            filter_params.organization_ids = organization_ids
        else:
            filter_params.organization_ids = organization_ids
        filter_params.page_size = 1  # We only need the count
        
        result = self.get_notifications(filter_params)
        return result.total_entity_count
    
    def get_unread_count(self, organization_ids: Union[int, list] = 0) -> int:
        """Get unread notification count."""
        # Create filter with explicit field values
        filter_params = NotificationsFilter()
        filter_params.is_read = False
        if isinstance(organization_ids, list):
            filter_params.organization_ids = organization_ids
        else:
            filter_params.organization_ids = organization_ids
        filter_params.page_size = 1  # We only need the count
        
        result = self.get_notifications(filter_params)
        return result.total_entity_count 