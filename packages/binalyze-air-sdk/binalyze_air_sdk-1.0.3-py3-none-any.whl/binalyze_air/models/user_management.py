"""
User Management-related data models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel, Filter


class UserManagementUser(AIRBaseModel):
    """User management user model."""
    
    id: str = Field(alias="_id")
    username: str
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    organizationId: Optional[int] = Field(default=None, alias="organizationId")  # Made optional as API may not always include it
    role: Optional[str] = None
    isActive: bool = True
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class CreateUserRequest(AIRBaseModel):
    """Create user request model."""
    
    username: str
    email: str
    password: str
    organizationIds: List[int]  # API expects plural and array
    roles: Optional[List[str]] = None  # API expects plural array of role IDs
    strategy: str = "local"  # API requires strategy field
    profile: Optional[Dict[str, str]] = None  # API supports profile object


class UpdateUserRequest(AIRBaseModel):
    """Update user request model."""
    
    username: Optional[str] = None
    email: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[str] = None
    isActive: Optional[bool] = None


class AIUser(AIRBaseModel):
    """AI user model."""
    
    id: str
    name: str
    description: Optional[str] = None
    capabilities: List[str] = []
    organizationId: int
    isActive: bool = True


class CreateAIUserRequest(AIRBaseModel):
    """Create AI user request model."""
    
    name: str
    description: Optional[str] = None
    capabilities: List[str] = []
    organizationId: int


class APIUser(AIRBaseModel):
    """API user model."""
    
    id: str
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    organizationId: int
    apiKey: Optional[str] = None
    isActive: bool = True


class CreateAPIUserRequest(AIRBaseModel):
    """Create API user request model."""
    
    name: str
    description: Optional[str] = None
    permissions: List[str] = []
    organizationId: int


class UserFilter(Filter):
    """Filter for user queries."""
    
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    organizationId: Optional[int] = None
    isActive: Optional[bool] = None


# Password Management Models
class ChangePasswordRequest(AIRBaseModel):
    """Change current user password request model."""
    
    oldPassword: str
    newPassword: str
    confirmPassword: str


class SetAPIUserPasswordRequest(AIRBaseModel):
    """Set API user password request model."""
    
    password: str
    confirmPassword: str


class ResetPasswordRequest(AIRBaseModel):
    """Reset password request model."""
    
    password: str
    confirmPassword: str


# Role Management Models
class Role(AIRBaseModel):
    """Role model."""
    
    id: str = Field(alias="_id")
    name: str
    tag: Optional[str] = None
    privileges: List[str] = []
    privilegeTypes: List[str] = []
    createdBy: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class CreateRoleRequest(AIRBaseModel):
    """Create role request model."""
    
    name: str
    tag: Optional[str] = None
    privileges: List[str] = []


class UpdateRoleRequest(AIRBaseModel):
    """Update role request model."""
    
    name: Optional[str] = None
    tag: Optional[str] = None
    privileges: Optional[List[str]] = None


class Privilege(AIRBaseModel):
    """Privilege model."""
    
    name: str
    description: Optional[str] = None
    category: Optional[str] = None


# User Group Management Models
class UserGroup(AIRBaseModel):
    """User group model."""
    
    id: str
    name: str
    description: Optional[str] = None
    isSyncedWithSso: bool = False
    organizationIds: List[int] = []
    users: List[UserManagementUser] = []
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class CreateUserGroupRequest(AIRBaseModel):
    """Create user group request model."""
    
    name: str
    description: Optional[str] = None
    organizationIds: List[int] = []
    userIds: List[str] = []
    isSyncedWithSso: bool = False  # API expects this field
    ssoGroupConfig: Optional[Dict[str, str]] = None  # API expects this field


class UpdateUserGroupRequest(AIRBaseModel):
    """Update user group request model."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    organizationIds: Optional[List[int]] = None
    userIds: Optional[List[str]] = None


class UserGroupFilter(Filter):
    """Filter for user group queries."""
    
    name: Optional[str] = None
    description: Optional[str] = None 