"""
Organization-related data models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel, Filter


class OrganizationStatus(str, Enum):
    """Organization status."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"


class UserRoleType(str, Enum):
    """User role type in organization."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    ANALYST = "analyst"


class FilterOption(AIRBaseModel):
    """Filter option model for API response metadata."""
    
    name: str
    type: str  # text, select, etc.
    options: List[Any] = []
    filter_url: Optional[str] = Field(default=None, alias="filterUrl")


class Organization(AIRBaseModel):
    """Organization model with complete field mapping."""
    
    id: int = Field(alias="_id")
    name: str
    note: Optional[str] = None
    owner: Optional[str] = None
    is_default: bool = Field(default=False, alias="isDefault")
    shareable_deployment_enabled: bool = Field(default=True, alias="shareableDeploymentEnabled")
    deployment_token: Optional[str] = Field(default=None, alias="deploymentToken")
    contact: Dict[str, Any] = {}
    total_endpoints: int = Field(default=0, alias="totalEndpoints")
    tags: List[str] = []
    statistics: Optional[Dict[str, Any]] = None  # Organization statistics
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")


class UserProfile(AIRBaseModel):
    """User profile information."""
    
    name: Optional[str] = None
    surname: Optional[str] = None
    department: Optional[str] = None


class UserGroup(AIRBaseModel):
    """User group information."""
    
    id: str
    name: str
    organization_ids: List[int] = Field(default=[], alias="organizationIds")


class UserRole(AIRBaseModel):
    """User role information with full privileges."""
    
    id: str = Field(alias="_id")
    name: str
    tag: str
    created_by: str = Field(alias="createdBy")
    privileges: List[str] = []
    privilege_types: List[str] = Field(default=[], alias="privilegeTypes")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")


class OrganizationUser(AIRBaseModel):
    """Enhanced organization user model with complete field mapping."""
    
    # Core fields
    id: str = Field(alias="_id")
    email: str
    username: str
    strategy: Optional[str] = None
    
    # Profile information
    profile: Optional[UserProfile] = None
    
    # Role and permission information
    roles: List[UserRole] = []
    groups: List[UserGroup] = []
    
    # Organization and permission data
    organization_ids: Optional[Union[str, List[int]]] = Field(default=None, alias="organizationIds")  # Can be "ALL" or list
    
    # Boolean flags
    has_password: bool = Field(default=False, alias="hasPassword")
    tfa_enabled: bool = Field(default=False, alias="tfaEnabled")
    is_authorized_for_all_organizations: bool = Field(default=False, alias="isAuthorizedForAllOrganizations")
    is_global_admin: bool = Field(default=False, alias="isGlobalAdmin")
    is_organization_admin: bool = Field(default=False, alias="isOrganizationAdmin")
    is_not_in_organizations: bool = Field(default=False, alias="isNotInOrganizations")
    
    # Timestamps
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    
    # Legacy fields for backward compatibility
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    organization_id: Optional[int] = None
    last_login: Optional[datetime] = None
    is_active: bool = True
    permissions: List[str] = []


class OrganizationUsersPaginatedResponse(AIRBaseModel):
    """Complete paginated response for organization users endpoint."""
    
    entities: List[OrganizationUser]
    filters: List[FilterOption] = []
    sortables: List[str] = []
    total_entity_count: int = Field(default=0, alias="totalEntityCount")
    current_page: int = Field(default=1, alias="currentPage")
    page_size: int = Field(default=10, alias="pageSize")
    previous_page: int = Field(default=0, alias="previousPage")
    total_page_count: int = Field(default=1, alias="totalPageCount")
    next_page: int = Field(default=2, alias="nextPage")


class OrganizationRole(AIRBaseModel):
    """Organization role model."""
    
    id: str
    name: str
    description: Optional[str] = None
    organization_id: int
    permissions: List[str] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    is_system: bool = False
    user_count: int = 0


class OrganizationLicense(AIRBaseModel):
    """Organization license model."""
    
    id: str
    organization_id: int
    license_type: str
    total_licenses: int = 0
    used_licenses: int = 0
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    features: List[str] = []
    is_active: bool = True


class OrganizationSettings(AIRBaseModel):
    """Organization settings model."""
    
    organization_id: int
    retention_policy: Dict[str, Any] = {}
    security_settings: Dict[str, Any] = {}
    notification_settings: Dict[str, Any] = {}
    api_settings: Dict[str, Any] = {}
    custom_settings: Dict[str, Any] = {}


class OrganizationFilter(Filter):
    """Filter for organization queries with complete parameter support."""
    
    name: Optional[str] = None
    search_term: Optional[str] = None
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters."""
        params = {}
        if self.name:
            params["filter[name]"] = self.name
        if self.search_term:
            params["filter[searchTerm]"] = self.search_term
        return params


class OrganizationsPaginatedResponse(AIRBaseModel):
    """Complete paginated response for organizations list endpoint."""
    
    entities: List[Organization]
    filters: List[FilterOption] = []
    sortables: List[str] = []
    total_entity_count: int = Field(default=0, alias="totalEntityCount")
    current_page: int = Field(default=1, alias="currentPage")
    page_size: int = Field(default=10, alias="pageSize")
    previous_page: int = Field(default=0, alias="previousPage")
    total_page_count: int = Field(default=1, alias="totalPageCount")
    next_page: int = Field(default=2, alias="nextPage")


# Request models for organization operations
class CreateOrganizationRequest(AIRBaseModel):
    """Create organization request model with complete field mapping."""
    
    name: str
    shareable_deployment_enabled: bool = Field(default=True, alias="shareableDeploymentEnabled")
    note: Optional[str] = None
    contact: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class UpdateOrganizationRequest(AIRBaseModel):
    """Update organization request model with complete field mapping."""
    
    name: Optional[str] = None
    note: Optional[str] = None
    owner: Optional[str] = None  # Added missing owner field
    contact: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class AddUserToOrganizationRequest(AIRBaseModel):
    """Add user to organization request model."""
    
    user_id: str
    email: str
    username: str
    role: Optional[str] = None


class AssignUsersToOrganizationRequest(AIRBaseModel):
    """Assign multiple users to organization request model."""
    
    user_ids: List[str] = Field(alias="userIds")


class AddTagsToOrganizationRequest(AIRBaseModel):
    """Add tags to organization request model."""
    
    tags: List[str]


class DeleteTagsFromOrganizationRequest(AIRBaseModel):
    """Delete tags from organization request model."""
    
    tags: List[str]


class UpdateShareableDeploymentSettingsRequest(AIRBaseModel):
    """Update shareable deployment settings request model."""
    
    status: bool


class UpdateDeploymentTokenRequest(AIRBaseModel):
    """Update deployment token request model."""
    
    # Empty request body - the API generates a new token automatically
    pass


class CheckOrganizationNameExistsResponse(AIRBaseModel):
    """Response model for checking if organization name exists."""
    
    success: bool
    result: bool
    status_code: int = Field(alias="statusCode")
    errors: List[str] = []


class ShareableDeploymentInfoResponse(AIRBaseModel):
    """Response model for shareable deployment information."""
    
    success: bool
    result: Optional[Dict[str, Any]] = None
    status_code: int = Field(alias="statusCode")
    errors: List[str] = []


class DeploymentTokenUpdateResponse(AIRBaseModel):
    """Response model for deployment token update."""
    
    success: bool
    result: Optional[Dict[str, str]] = None  # Contains new token
    status_code: int = Field(alias="statusCode")
    errors: List[str] = [] 