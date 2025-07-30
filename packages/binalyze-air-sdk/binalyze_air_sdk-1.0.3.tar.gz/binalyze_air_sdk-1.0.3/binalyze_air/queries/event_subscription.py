"""
Event Subscription queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.event_subscription import EventSubscription, EventSubscriptionFilter
from ..http_client import HTTPClient


class ListEventSubscriptionsQuery(Query[List[EventSubscription]]):
    """Query to list event subscriptions."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[EventSubscriptionFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or EventSubscriptionFilter()
    
    def execute(self) -> List[EventSubscription]:
        """Execute the query to get event subscriptions."""
        params = self.filter_params.to_params()
        response = self.http_client.get("event-subscription", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing
        subscriptions = []
        for item in entities:
            # Convert id to string as Pydantic expects
            if "id" in item:
                item["id"] = str(item["id"])
            subscriptions.append(EventSubscription.model_validate(item))
        
        return subscriptions


class GetEventSubscriptionQuery(Query[EventSubscription]):
    """Query to get a specific event subscription."""
    
    def __init__(self, http_client: HTTPClient, subscription_id: str):
        self.http_client = http_client
        self.subscription_id = subscription_id
    
    def execute(self) -> EventSubscription:
        """Execute the query to get a specific event subscription."""
        response = self.http_client.get(f"event-subscription/{self.subscription_id}")
        
        entity_data = response.get("result", {})
        
        # Convert id to string as Pydantic expects
        if "id" in entity_data:
            entity_data["id"] = str(entity_data["id"])
        
        # Use Pydantic parsing with proper field aliasing
        return EventSubscription.model_validate(entity_data) 