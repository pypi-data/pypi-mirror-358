"""
API Tokens models for the Binalyze AIR SDK.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel


class APIToken(AIRBaseModel):
    """API Token model."""
    
    id: str = Field(alias="_id")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    username: str
    name: str
    description: str
    token: Optional[str] = None  # Only returned on creation
    expiration_date: Optional[datetime] = Field(default=None, alias="expirationDate")
    last_used_at: Optional[datetime] = Field(default=None, alias="lastUsedAt")
    role_id: str = Field(alias="roleId")


class APITokensPaginatedResponse(AIRBaseModel):
    """Paginated response for API tokens."""
    
    entities: List[APIToken]
    filters: List[str]
    sortables: List[str]
    total_entity_count: int = Field(alias="totalEntityCount")
    current_page: int = Field(alias="currentPage")
    page_size: int = Field(alias="pageSize")
    previous_page: int = Field(alias="previousPage")
    total_page_count: int = Field(alias="totalPageCount")
    next_page: int = Field(alias="nextPage")


class CreateAPITokenRequest(AIRBaseModel):
    """Request model for creating API tokens."""
    
    name: str
    description: str = ""
    expiration_date: Optional[datetime] = Field(default=None, alias="expirationDate")
    role_id: str = Field(alias="roleId")


class UpdateAPITokenRequest(AIRBaseModel):
    """Request model for updating API tokens."""
    
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    expiration_date: Optional[datetime] = Field(default=None, alias="expirationDate")
    role_id: Optional[str] = Field(default=None, alias="roleId")
        
    def model_dump(self, **kwargs):
        """Override model_dump to ensure proper serialization."""
        # Always exclude unset values for partial updates
        kwargs.setdefault('exclude_unset', True)
        kwargs.setdefault('by_alias', True)
        kwargs.setdefault('mode', 'json')
        return super().model_dump(**kwargs)


class APITokenFilter(AIRBaseModel):
    """Filter parameters for API tokens."""
    
    page_size: Optional[int] = Field(default=10, alias="pageSize")
    page_number: Optional[int] = Field(default=1, alias="pageNumber")
    sort_type: Optional[str] = Field(default="DESC", alias="sortType")  # ASC or DESC
    sort_by: Optional[str] = Field(default="createdAt", alias="sortBy")  # name, description, expirationDate, createdAt 