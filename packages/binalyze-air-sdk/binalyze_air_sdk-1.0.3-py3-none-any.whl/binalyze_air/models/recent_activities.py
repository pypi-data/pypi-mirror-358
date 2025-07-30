"""
Recent Activities models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel


class RecentActivityUser(AIRBaseModel):
    """User information in recent activity model."""
    
    id: str = Field(alias="_id")
    username: str
    profile: Dict[str, Any]


class RecentActivity(AIRBaseModel):
    """Recent activity model."""
    
    id: str = Field(alias="_id")
    type: str
    username: str
    entity_id: str = Field(alias="entityId")
    organization_id: int = Field(alias="organizationId")
    last_used_at: datetime = Field(alias="lastUsedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    user: RecentActivityUser
    data: Dict[str, Any]


class RecentActivitiesList(AIRBaseModel):
    """Recent activities list response model."""
    
    entities: List[RecentActivity]
    total_entity_count: Optional[int] = None
    current_page: Optional[int] = None
    page_size: Optional[int] = None
    previous_page: Optional[int] = None
    total_page_count: Optional[int] = None
    next_page: Optional[int] = None
    filters: Optional[List[Dict[str, Any]]] = None
    sortables: Optional[List[str]] = None


class RecentActivitiesFilter(AIRBaseModel):
    """Filter parameters for recent activities queries."""
    
    organization_id: Optional[int] = None
    type: Optional[str] = None
    username: Optional[str] = None
    search_term: Optional[str] = None
    page_size: Optional[int] = None
    page_number: Optional[int] = None
    sort_by: Optional[str] = None
    sort_type: Optional[str] = None


class CreateRecentActivityRequest(AIRBaseModel):
    """Request model for creating a recent activity."""
    
    type: str
    entity_id: str = Field(alias="entityId")
    # Optional fields - API will auto-populate from authenticated user
    username: Optional[str] = None
    organization_id: Optional[int] = None
    data: Optional[Dict[str, Any]] = None 