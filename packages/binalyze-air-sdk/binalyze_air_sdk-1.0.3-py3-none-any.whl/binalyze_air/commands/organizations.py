"""
Organization-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, List

from ..base import Command
from ..models.organizations import (
    Organization, OrganizationUser, CreateOrganizationRequest, 
    UpdateOrganizationRequest, AddUserToOrganizationRequest, OrganizationSettings,
    AssignUsersToOrganizationRequest, AddTagsToOrganizationRequest,
    DeleteTagsFromOrganizationRequest, UpdateShareableDeploymentSettingsRequest,
    UpdateDeploymentTokenRequest, DeploymentTokenUpdateResponse
)
from ..http_client import HTTPClient


class CreateOrganizationCommand(Command[Organization]):
    """Command to create a new organization."""
    
    def __init__(self, http_client: HTTPClient, request: CreateOrganizationRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Organization:
        """Execute the command to create an organization."""
        data = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.post("organizations", json_data=data)
        
        entity_data = response.get("result", {})
        
        # Use Pydantic model_validate for automatic field mapping via aliases
        return Organization.model_validate(entity_data)


class UpdateOrganizationCommand(Command[Organization]):
    """Command to update an existing organization."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str, request: UpdateOrganizationRequest):
        self.http_client = http_client
        self.organization_id = organization_id
        self.request = request
    
    def execute(self) -> Organization:
        """Execute the command to update an organization."""
        data = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.patch(f"organizations/{self.organization_id}", json_data=data)
        
        entity_data = response.get("result", {})
        
        # Use Pydantic model_validate for automatic field mapping via aliases
        return Organization.model_validate(entity_data)


class DeleteOrganizationCommand(Command[Dict[str, Any]]):
    """Command to delete an organization."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str):
        self.http_client = http_client
        self.organization_id = organization_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to delete an organization."""
        response = self.http_client.delete(f"organizations/{self.organization_id}")
        return response


class AssignUsersToOrganizationCommand(Command[bool]):
    """Command to assign multiple users to an organization using the /assign-users endpoint."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str, request: AssignUsersToOrganizationRequest):
        self.http_client = http_client
        self.organization_id = organization_id
        self.request = request
    
    def execute(self) -> bool:
        """Execute the command to assign users to organization."""
        data = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.post(f"organizations/{self.organization_id}/assign-users", json_data=data)
        
        return response.get("success", False)


class RemoveUserFromOrganizationCommand(Command[Dict[str, Any]]):
    """Command to remove a user from an organization using the /remove-user/{userId} endpoint."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str, user_id: str):
        self.http_client = http_client
        self.organization_id = organization_id
        self.user_id = user_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to remove user from organization."""
        response = self.http_client.delete(f"organizations/{self.organization_id}/remove-user/{self.user_id}")
        
        return response


class AddTagsToOrganizationCommand(Command[Organization]):
    """Command to add tags to an organization."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str, request: AddTagsToOrganizationRequest):
        self.http_client = http_client
        self.organization_id = organization_id
        self.request = request
    
    def execute(self) -> Organization:
        """Execute the command to add tags to organization."""
        data = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.patch(f"organizations/{self.organization_id}/tags", json_data=data)
        
        entity_data = response.get("result", {})
        
        # Use Pydantic model_validate for automatic field mapping
        return Organization.model_validate(entity_data)


class DeleteTagsFromOrganizationCommand(Command[Organization]):
    """Command to delete tags from an organization."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str, request: DeleteTagsFromOrganizationRequest):
        self.http_client = http_client
        self.organization_id = organization_id
        self.request = request
    
    def execute(self) -> Organization:
        """Execute the command to delete tags from organization."""
        data = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.delete(f"organizations/{self.organization_id}/tags", json_data=data)
        
        entity_data = response.get("result", {})
        
        # Use Pydantic model_validate for automatic field mapping
        return Organization.model_validate(entity_data)


class UpdateShareableDeploymentSettingsCommand(Command[bool]):
    """Command to update organization shareable deployment settings."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str, request: UpdateShareableDeploymentSettingsRequest):
        self.http_client = http_client
        self.organization_id = organization_id
        self.request = request
    
    def execute(self) -> bool:
        """Execute the command to update shareable deployment settings."""
        data = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.post(f"organizations/{self.organization_id}/shareable-deployment", json_data=data)
        
        return response.get("success", False)


class UpdateDeploymentTokenCommand(Command[DeploymentTokenUpdateResponse]):
    """Command to update organization deployment token."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str):
        self.http_client = http_client
        self.organization_id = organization_id
    
    def execute(self) -> DeploymentTokenUpdateResponse:
        """Execute the command to update deployment token."""
        response = self.http_client.post(f"organizations/{self.organization_id}/deployment-token")
        
        # Use Pydantic model_validate for automatic field mapping
        return DeploymentTokenUpdateResponse.model_validate(response)


class UpdateOrganizationSettingsCommand(Command[OrganizationSettings]):
    """Command to update organization settings."""
    
    def __init__(self, http_client: HTTPClient, organization_id: str, settings: Dict[str, Any]):
        self.http_client = http_client
        self.organization_id = organization_id
        self.settings = settings
    
    def execute(self) -> OrganizationSettings:
        """Execute the command to update organization settings."""
        response = self.http_client.put(f"organizations/{self.organization_id}/settings", json_data=self.settings)
        
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