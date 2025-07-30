"""
Preset Filters models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel


class PresetFilter(AIRBaseModel):
    """Preset filter model."""
    
    id: int
    organization_id: int = Field(alias="organizationId")
    type: str
    name: str
    filter: List[Dict[str, Any]]
    created_by: str = Field(alias="createdBy")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class PresetFiltersList(AIRBaseModel):
    """Preset filters list response model."""
    
    entities: List[PresetFilter]
    total_entity_count: Optional[int] = Field(alias="totalEntityCount", default=None)
    current_page: Optional[int] = Field(alias="currentPage", default=None)
    page_size: Optional[int] = Field(alias="pageSize", default=None)
    previous_page: Optional[int] = Field(alias="previousPage", default=None)
    total_page_count: Optional[int] = Field(alias="totalPageCount", default=None)
    next_page: Optional[int] = Field(alias="nextPage", default=None)
    filters: Optional[List[Dict[str, Any]]] = None
    sortables: Optional[List[str]] = None


class PresetFiltersFilter(AIRBaseModel):
    """Filter parameters for preset filters queries."""
    
    organization_id: Optional[int] = None
    type: Optional[str] = None
    name: Optional[str] = None
    created_by: Optional[str] = None
    page_size: Optional[int] = None
    page_number: Optional[int] = None
    sort_by: Optional[str] = None
    sort_type: Optional[str] = None


class CreatePresetFilterRequest(AIRBaseModel):
    """Request model for creating a preset filter."""
    
    name: str
    organization_id: int = Field(alias="organizationId")
    type: str = Field(default="ENDPOINT", alias="type")
    filter: List[Dict[str, Any]]
    created_by: str = Field(alias="createdBy")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API requests, always forcing type to 'ENDPOINT'."""
        d = self.model_dump(exclude_none=True, by_alias=True)
        d["type"] = "ENDPOINT"
        return d


class UpdatePresetFilterRequest(AIRBaseModel):
    """Request model for updating a preset filter."""
    
    name: Optional[str] = None
    type: Optional[str] = Field(default="ENDPOINT", alias="type")
    filter: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API requests, always forcing type to 'ENDPOINT'."""
        d = self.model_dump(exclude_none=True, by_alias=True)
        d["type"] = "ENDPOINT"
        return d 