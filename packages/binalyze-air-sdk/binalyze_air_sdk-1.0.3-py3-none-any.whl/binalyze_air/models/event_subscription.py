"""
Event Subscription API models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field, field_validator

from ..base import AIRBaseModel, Filter


class SubscriptionStatus(str, Enum):
    """Event subscription status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    FAILED = "failed"


class EventType(str, Enum):
    """Event types for subscriptions."""
    # Real API event names from JSON specification
    DEPLOYMENT_TOKEN_REGENERATED = "DeploymentTokenRegeneratedEvent"
    TASK_PROCESSING_FAILED = "TaskProcessingFailedEvent"
    TASK_PROCESSING_COMPLETED = "TaskProcessingCompletedEvent"
    CASE_FILE_SAVED = "CaseFileSavedEvent"
    
    # Additional event types found in the API
    TASK_FAILED = "TaskFailedEvent"  # Found in API response
    ENDPOINT_ONLINE = "EndpointOnlineEvent"  # Found in API response
    ENDPOINT_OFFLINE = "EndpointOfflineEvent"  # Found in API response
    TASK_COMPLETED = "TaskCompletedEvent"  # Found in API response
    
    # Additional common event types (these may exist in the system)
    ASSET_CREATED = "AssetCreatedEvent"
    ASSET_UPDATED = "AssetUpdatedEvent"
    ASSET_DELETED = "AssetDeletedEvent"
    CASE_CREATED = "CaseCreatedEvent"
    CASE_UPDATED = "CaseUpdatedEvent"
    CASE_CLOSED = "CaseClosedEvent"
    TASK_STARTED = "TaskStartedEvent"
    POLICY_EXECUTED = "PolicyExecutedEvent"
    ALERT_TRIGGERED = "AlertTriggeredEvent"


class DeliveryMethod(str, Enum):
    """Event delivery methods."""
    WEBHOOK = "webhook"
    EMAIL = "email"
    SYSLOG = "syslog"


class EventSubscription(AIRBaseModel):
    """Event subscription model."""
    
    id: str = Field(alias="id")  # API returns int, but we'll convert to string
    name: str
    description: Optional[str] = None
    event_types: Optional[List[EventType]] = Field(default=[], alias="events")  # API: events -> SDK: event_types
    delivery_method: Optional[DeliveryMethod] = Field(default=None, alias="deliveryMethod")
    endpoint_url: Optional[str] = Field(default=None, alias="url")  # API: url -> SDK: endpoint_url
    email_addresses: Optional[List[str]] = Field(default=None, alias="emailAddresses")
    syslog_server: Optional[str] = Field(default=None, alias="syslogServer")
    status: Optional[SubscriptionStatus] = None
    active: Optional[bool] = None  # API uses active boolean instead of status enum
    organization_id: Optional[int] = Field(default=None, alias="organizationId")
    created_by: Optional[str] = Field(default=None, alias="createdBy")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    last_triggered: Optional[datetime] = Field(default=None, alias="lastTriggered")
    trigger_count: int = Field(default=0, alias="triggerCount")
    retry_count: int = Field(default=3, alias="retryCount")
    retry_interval: int = Field(default=300, alias="retryInterval")  # seconds
    headers: Optional[Dict[str, str]] = None  # For webhook headers
    authentication: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None  # Event filtering criteria
    url: Optional[str] = None  # Keep original API field name for backward compatibility
    auth_token: Optional[str] = Field(default=None, alias="authToken")
    
    @field_validator('id', mode='before')
    @classmethod
    def convert_id_to_string(cls, v):
        """Convert ID from int to string as API returns numbers."""
        return str(v) if v is not None else v


class CreateEventSubscriptionRequest(AIRBaseModel):
    """Request model for creating event subscriptions."""
    
    name: str
    description: Optional[str] = None
    event_types: List[EventType]
    delivery_method: DeliveryMethod
    endpoint_url: Optional[str] = None
    email_addresses: Optional[List[str]] = None
    syslog_server: Optional[str] = None
    organization_id: int
    retry_count: Optional[int] = 3
    retry_interval: Optional[int] = 300
    headers: Optional[Dict[str, str]] = None
    authentication: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None


class UpdateEventSubscriptionRequest(AIRBaseModel):
    """Request model for updating event subscriptions."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    event_types: Optional[List[EventType]] = None
    delivery_method: Optional[DeliveryMethod] = None
    endpoint_url: Optional[str] = None
    email_addresses: Optional[List[str]] = None
    syslog_server: Optional[str] = None
    status: Optional[SubscriptionStatus] = None
    retry_count: Optional[int] = None
    retry_interval: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    authentication: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None


class EventSubscriptionFilter(Filter):
    """Filter for event subscription queries."""
    
    # Override the default organization_ids to not use organization filtering
    organization_ids: Optional[List[int]] = None
    
    # Add organizationId (singular) as required by the API
    organization_id: Optional[int] = None
    
    name: Optional[str] = None
    event_type: Optional[EventType] = None
    delivery_method: Optional[DeliveryMethod] = None
    status: Optional[SubscriptionStatus] = None
    created_by: Optional[str] = None
    is_active: Optional[bool] = None  # API uses isActive
    url: Optional[str] = None  # API supports URL filtering
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters, using organizationId (singular) for event subscriptions."""
        params = {}
        
        # Pagination parameters (not in filter namespace)
        if self.page_number is not None:
            params["pageNumber"] = self.page_number
        if self.page_size is not None:
            params["pageSize"] = self.page_size
        if self.sort_by is not None:
            params["sortBy"] = self.sort_by
        if self.sort_type is not None:
            params["sortType"] = self.sort_type
        
        # Always add organizationId (required by API) - default to 0 if not set
        organization_id = self.organization_id if self.organization_id is not None else 0
        params["filter[organizationId]"] = str(organization_id)
        
        # Filter parameters (in filter namespace) - EXCLUDE organization_ids and organization_id
        for field_name, field_value in self.model_dump(exclude_none=True).items():
            # Skip pagination/sorting fields and organization fields (handled above)
            if field_name in ["page_number", "page_size", "sort_by", "sort_type", "organization_ids", "organization_id"]:
                continue
                
            if field_value is not None:
                if isinstance(field_value, list):
                    if len(field_value) > 0:  # Only add non-empty lists
                        params[f"filter[{field_name}]"] = ",".join([str(x) for x in field_value])
                else:
                    params[f"filter[{field_name}]"] = str(field_value)
        return params 