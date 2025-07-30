"""
Organization-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.organizations import (
    Organization, OrganizationUser, OrganizationRole, OrganizationLicense,
    OrganizationSettings, OrganizationFilter, OrganizationsPaginatedResponse,
    FilterOption, OrganizationUsersPaginatedResponse, CheckOrganizationNameExistsResponse,
    ShareableDeploymentInfoResponse
)
from ..http_client import HTTPClient


class ListOrganizationsQuery(Query[OrganizationsPaginatedResponse]):
    """Query to list organizations with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, page: int = 1, page_size: int = 10, 
                 sort_by: str = "name", order: str = "asc", filter_params: Optional[OrganizationFilter] = None):
        self.http_client = http_client
        self.page = page
        self.page_size = page_size
        self.sort_by = sort_by
        self.order = order
        self.filter_params = filter_params or OrganizationFilter()
    
    def execute(self) -> OrganizationsPaginatedResponse:
        """Execute the query to list organizations with complete parameter support."""
        # Build query parameters
        params = {
            "pageNumber": self.page,
            "pageSize": self.page_size,
            "sortBy": self.sort_by,
            "sortType": self.order.upper(),  # ASC or DESC
        }
        
        # Add filter parameters using proper API structure
        filter_params = self.filter_params.to_params()
        params.update(filter_params)
        
        response = self.http_client.get("organizations", params=params)
        
        result = response.get("result", {})
        
        # Use Pydantic model_validate for automatic field mapping
        return OrganizationsPaginatedResponse.model_validate(result)


class GetOrganizationQuery(Query[Organization]):
    """Query to get a specific organization by ID."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str):
        self.http_client = http_client
        self.organization_id = organization_id
    
    def execute(self) -> Organization:
        """Execute the query to get organization details."""
        response = self.http_client.get(f"organizations/{self.organization_id}")
        
        entity_data = response.get("result", {})
        
        # Use Pydantic model_validate for automatic field mapping via aliases
        return Organization.model_validate(entity_data)


class GetOrganizationUsersQuery(Query[OrganizationUsersPaginatedResponse]):
    """Query to get users for a specific organization with complete field mapping."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str, page: int = 1, page_size: int = 10):
        self.http_client = http_client
        self.organization_id = organization_id
        self.page = page
        self.page_size = page_size
    
    def execute(self) -> OrganizationUsersPaginatedResponse:
        """Execute the query to get organization users with complete field mapping."""
        # Add pagination parameters
        params = {
            "pageNumber": self.page,
            "pageSize": self.page_size
        }
        
        response = self.http_client.get(f"organizations/{self.organization_id}/users", params=params)
        
        result = response.get("result", {})
        
        # Use Pydantic model_validate for automatic field mapping
        return OrganizationUsersPaginatedResponse.model_validate(result)


class CheckOrganizationNameExistsQuery(Query[CheckOrganizationNameExistsResponse]):
    """Query to check if an organization name exists."""
    
    def __init__(self, http_client: HTTPClient, name: str):
        self.http_client = http_client
        self.name = name
    
    def execute(self) -> CheckOrganizationNameExistsResponse:
        """Execute the query to check organization name availability."""
        params = {"name": self.name}
        
        response = self.http_client.get("organizations/check", params=params)
        
        # Use Pydantic model_validate for automatic field mapping
        return CheckOrganizationNameExistsResponse.model_validate(response)


class GetShareableDeploymentInfoQuery(Query[ShareableDeploymentInfoResponse]):
    """Query to get shareable deployment information by token."""
    
    def __init__(self, http_client: HTTPClient, token: str):
        self.http_client = http_client
        self.token = token
    
    def execute(self) -> ShareableDeploymentInfoResponse:
        """Execute the query to get shareable deployment information."""
        params = {"token": self.token}
        
        response = self.http_client.get("organizations/shareable-deployment", params=params)
        
        # Use Pydantic model_validate for automatic field mapping
        return ShareableDeploymentInfoResponse.model_validate(response)


class GetOrganizationRolesQuery(Query[List[OrganizationRole]]):
    """Query to get roles for a specific organization."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str):
        self.http_client = http_client
        self.organization_id = organization_id
    
    def execute(self) -> List[OrganizationRole]:
        """Execute the query to get organization roles."""
        response = self.http_client.get(f"organizations/{self.organization_id}/roles")
        
        entities = response.get("result", {}).get("entities", [])
        
        roles = []
        for entity_data in entities:
            mapped_data = {
                "id": entity_data.get("_id"),
                "name": entity_data.get("name"),
                "description": entity_data.get("description"),
                "organization_id": entity_data.get("organizationId"),
                "permissions": entity_data.get("permissions", []),
                "created_at": entity_data.get("createdAt"),
                "updated_at": entity_data.get("updatedAt"),
                "created_by": entity_data.get("createdBy"),
                "is_system": entity_data.get("isSystem", False),
                "user_count": entity_data.get("userCount", 0),
            }
            
            # Remove None values
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            roles.append(OrganizationRole(**mapped_data))
        
        return roles


class GetOrganizationLicensesQuery(Query[List[OrganizationLicense]]):
    """Query to get licenses for a specific organization."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str):
        self.http_client = http_client
        self.organization_id = organization_id
    
    def execute(self) -> List[OrganizationLicense]:
        """Execute the query to get organization licenses."""
        response = self.http_client.get(f"organizations/{self.organization_id}/licenses")
        
        entities = response.get("result", {}).get("entities", [])
        
        licenses = []
        for entity_data in entities:
            mapped_data = {
                "id": entity_data.get("_id"),
                "organization_id": entity_data.get("organizationId"),
                "license_type": entity_data.get("licenseType"),
                "total_licenses": entity_data.get("totalLicenses", 0),
                "used_licenses": entity_data.get("usedLicenses", 0),
                "valid_from": entity_data.get("validFrom"),
                "valid_until": entity_data.get("validUntil"),
                "features": entity_data.get("features", []),
                "is_active": entity_data.get("isActive", True),
            }
            
            # Remove None values
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            licenses.append(OrganizationLicense(**mapped_data))
        
        return licenses


class GetOrganizationSettingsQuery(Query[OrganizationSettings]):
    """Query to get settings for a specific organization."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str):
        self.http_client = http_client
        self.organization_id = organization_id
    
    def execute(self) -> OrganizationSettings:
        """Execute the query to get organization settings."""
        response = self.http_client.get(f"organizations/{self.organization_id}/settings")
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "organization_id": entity_data.get("organizationId"),
            "retention_policy": entity_data.get("retentionPolicy", {}),
            "security_settings": entity_data.get("securitySettings", {}),
            "notification_settings": entity_data.get("notificationSettings", {}),
            "api_settings": entity_data.get("apiSettings", {}),
            "custom_settings": entity_data.get("customSettings", {}),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return OrganizationSettings(**mapped_data) 