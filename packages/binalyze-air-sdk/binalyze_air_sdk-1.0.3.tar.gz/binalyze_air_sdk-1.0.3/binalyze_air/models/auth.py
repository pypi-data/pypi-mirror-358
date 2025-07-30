"""
Auth-related data models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel


class UserProfile(AIRBaseModel):
    """User profile information."""
    name: Optional[str] = None
    surname: Optional[str] = None
    department: Optional[str] = None


class UserRole(AIRBaseModel):
    """User role information."""
    id: Optional[str] = Field(alias="_id", default=None)
    name: str
    tag: str
    created_at: Optional[str] = Field(alias="createdAt", default=None)
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    created_by: Optional[str] = Field(alias="createdBy", default=None)
    privilege_types: List[str] = Field(alias="privilegeTypes", default_factory=list)


class User(AIRBaseModel):
    """User model."""
    
    id: str = Field(alias="_id")
    username: str
    email: str
    organization_ids: Optional[str] = Field(alias="organizationIds", default=None)  # Can be "ALL"
    strategy: Optional[str] = None
    profile: Optional[UserProfile] = None
    privileges: List[str] = Field(default_factory=list)
    roles: List[UserRole] = Field(default_factory=list)
    tfa_enabled: bool = Field(alias="tfaEnabled", default=False)
    created_at: Optional[str] = Field(alias="createdAt", default=None)
    updated_at: Optional[str] = Field(alias="updatedAt", default=None)
    has_password: bool = Field(alias="hasPassword", default=False)
    photo: Optional[str] = None
    groups: List[Any] = Field(default_factory=list)
    user_flow_user_signature: Optional[str] = Field(alias="userFlowUserSignature", default=None)
    user_flow_group_signature: Optional[str] = Field(alias="userFlowGroupSignature", default=None)


class AuthStatus(AIRBaseModel):
    """Authentication status model - matches actual API response."""
    
    # The API doesn't return authenticated field, we derive it from success
    authenticated: bool = True  # Default to True since if we get a response, we're authenticated
    user: Optional[User] = None
    

class LoginRequest(AIRBaseModel):
    """Login request model."""
    
    username: str
    password: str


class LoginResponse(AIRBaseModel):
    """Login response model."""
    
    access_token: str = Field(alias="accessToken")
    refresh_token: str = Field(alias="refreshToken") 