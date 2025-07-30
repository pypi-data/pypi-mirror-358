"""
Notifications commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..http_client import HTTPClient


class DeleteAllNotificationsCommand(Command[Dict[str, Any]]):
    """Command to delete all notifications for the current user."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete all notifications command."""
        response = self.http_client.delete("notifications")
        return response


class MarkAllAsReadCommand(Command[Dict[str, Any]]):
    """Command to mark all notifications as read."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> Dict[str, Any]:
        """Execute the mark all as read command."""
        response = self.http_client.put("notifications/mark-as-read/all")
        return response


class MarkAsReadByIdCommand(Command[Dict[str, Any]]):
    """Command to mark a specific notification as read by ID."""
    
    def __init__(self, http_client: HTTPClient, notification_id: Union[int, str]):
        self.http_client = http_client
        self.notification_id = notification_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the mark as read by ID command."""
        response = self.http_client.patch(f"notifications/mark-as-read/{self.notification_id}")
        return response 