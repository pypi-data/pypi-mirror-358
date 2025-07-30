"""
Relay Server models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from ..base import AIRBaseModel, Filter


class RelayServer(AIRBaseModel):
    """Relay server model."""
    
    id: int
    name: str
    endpoint_count: int
    last_seen: datetime
    online_status: str
    label: str
    address: str


class RelayServersList(AIRBaseModel):
    """Relay servers list response model."""
    
    entities: List[RelayServer]
    total_entity_count: Optional[int] = None
    current_page: Optional[int] = None
    page_size: Optional[int] = None
    previous_page: Optional[int] = None
    total_page_count: Optional[int] = None
    next_page: Optional[int] = None
    filters: Optional[List[Dict[str, Any]]] = None
    sortables: Optional[List[str]] = None


class RelayServersFilter(Filter):
    """Filter parameters for relay servers queries."""
    
    # Override the default organization_ids to use singular organizationId
    organization_ids: Optional[List[int]] = None
    
    # Add organizationId (singular) as required by the API
    organization_id: Optional[int] = None
    
    name: Optional[str] = None
    online_status: Optional[str] = None
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters, using organizationId (singular) for relay servers."""
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


class RebootTaskRequest(AIRBaseModel):
    """Request model for reboot task."""
    
    endpoint_filter: Dict[str, Any]


class ShutdownTaskRequest(AIRBaseModel):
    """Request model for shutdown task."""
    
    endpoint_filter: Dict[str, Any]


class LogRetrievalTaskRequest(AIRBaseModel):
    """Request model for log retrieval task."""
    
    endpoint_filter: Dict[str, Any]


class VersionUpdateTaskRequest(AIRBaseModel):
    """Request model for version update task."""
    
    endpoint_filter: Dict[str, Any]


class UpdateTagsRequest(AIRBaseModel):
    """Request model for updating tags."""
    
    tags: List[str]


class UpdateLabelRequest(AIRBaseModel):
    """Request model for updating label."""
    
    label: str


class UpdateAddressRequest(AIRBaseModel):
    """Request model for updating address."""
    
    address: str 