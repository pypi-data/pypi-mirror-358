"""
Recent Activities commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any

from ..base import Command
from ..models.recent_activities import CreateRecentActivityRequest
from ..http_client import HTTPClient


class CreateRecentActivityCommand(Command[Dict[str, Any]]):
    """Command to create a recent activity."""
    
    def __init__(self, http_client: HTTPClient, activity_data: CreateRecentActivityRequest):
        self.http_client = http_client
        self.activity_data = activity_data
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to create a recent activity."""
        # API only requires 'type' and 'entityId' fields
        # Other fields like username, organizationId are filled automatically by server
        minimal_data = {
            'type': self.activity_data.type,
            'entityId': self.activity_data.entity_id
        }
        
        response = self.http_client.post(
            '/recent-activities',
            json_data=minimal_data
        )
        return response 