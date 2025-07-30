"""
Event Subscription commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.event_subscription import EventSubscription, CreateEventSubscriptionRequest, UpdateEventSubscriptionRequest
from ..http_client import HTTPClient


class CreateEventSubscriptionCommand(Command[EventSubscription]):
    """Command to create an event subscription."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateEventSubscriptionRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> EventSubscription:
        """Execute the command to create an event subscription."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            data = self.request
        else:
            data = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("event-subscription", json_data=data)
        
        # Handle null result from API
        result = response.get("result")
        if result is None:
            # If result is null but status is success, create a basic EventSubscription
            if response.get("success"):
                # Use Pydantic parsing with proper field aliasing
                basic_data = {
                    "id": data.get("name", "unknown"),  # Use name as fallback ID
                    "name": data.get("name", ""),
                    "url": data.get("url", ""),
                    "active": data.get("active", True),
                    "events": data.get("events", []),
                    "organizationId": data.get("organizationId", 0)
                }
                return EventSubscription.model_validate(basic_data)
            else:
                # Create empty EventSubscription for failed requests
                basic_data = {
                    "id": "failed",
                    "name": "Failed Creation"
                }
                return EventSubscription.model_validate(basic_data)
        
        # Convert id to string as Pydantic expects
        if "id" in result:
            result["id"] = str(result["id"])
        
        # Use Pydantic parsing with proper field aliasing
        return EventSubscription.model_validate(result)


class UpdateEventSubscriptionCommand(Command[EventSubscription]):
    """Command to update an event subscription."""
    
    def __init__(self, http_client: HTTPClient, subscription_id: str, request: Union[UpdateEventSubscriptionRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.subscription_id = subscription_id
        self.request = request
    
    def execute(self) -> EventSubscription:
        """Execute the command to update an event subscription."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            data = self.request
        else:
            data = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.put(
            f"event-subscription/{self.subscription_id}", 
            json_data=data
        )
        
        result = response.get("result", {})
        
        # Convert id to string as Pydantic expects
        if "id" in result:
            result["id"] = str(result["id"])
        
        # Use Pydantic parsing with proper field aliasing
        return EventSubscription.model_validate(result)


class DeleteEventSubscriptionCommand(Command[Dict[str, Any]]):
    """Command to delete an event subscription."""
    
    def __init__(self, http_client: HTTPClient, subscription_id: str):
        self.http_client = http_client
        self.subscription_id = subscription_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to delete an event subscription."""
        response = self.http_client.delete(f"event-subscription/{self.subscription_id}")
        
        return response 