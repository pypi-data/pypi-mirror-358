"""
Organizations API for the Binalyze AIR SDK using CQRS pattern.
"""

from typing import List, Optional, Dict, Any
from ..http_client import HTTPClient
from ..models.organizations import (
    Organization, OrganizationsPaginatedResponse, OrganizationUsersPaginatedResponse,
    OrganizationUser, OrganizationSettings, CreateOrganizationRequest, UpdateOrganizationRequest,
    AddUserToOrganizationRequest, AssignUsersToOrganizationRequest
)
from ..queries.organizations import (
    ListOrganizationsQuery,
    GetOrganizationQuery,
    GetOrganizationUsersQuery,
)
from ..commands.organizations import (
    CreateOrganizationCommand,
    UpdateOrganizationCommand,
    AssignUsersToOrganizationCommand,
    RemoveUserFromOrganizationCommand,
    UpdateOrganizationSettingsCommand,
)


class OrganizationsAPI:
    """Organizations API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, page: int = 1, page_size: int = 10, 
             sort_by: str = "name", order: str = "asc") -> OrganizationsPaginatedResponse:
        """List organizations with pagination and sorting."""
        query = ListOrganizationsQuery(self.http_client, page, page_size, sort_by, order, None)
        return query.execute()
    
    def get(self, organization_id: str) -> Organization:
        """Get organization by ID."""
        query = GetOrganizationQuery(self.http_client, organization_id)
        return query.execute()
    
    def get_users(self, organization_id: str, page: int = 1, page_size: int = 10) -> OrganizationUsersPaginatedResponse:
        """Get users in organization."""
        query = GetOrganizationUsersQuery(self.http_client, organization_id, page, page_size)
        return query.execute()
    
    def check_name(self, name: str) -> bool:
        """Check if organization name exists."""
        try:
            params = {"name": name}
            response = self.http_client.get("organizations/check", params=params)
            return response.get("result", False)
        except Exception:
            return False
    
    def get_shareable_deployment_info(self, deployment_token: str) -> Dict[str, Any]:
        """Get shareable deployment information by token."""
        try:
            response = self.http_client.get(f"organizations/shareable-deployment-info/{deployment_token}")
            
            if response.get("success"):
                return response.get("result", {})
            else:
                # Return error information
                return {
                    "error": True,
                    "errors": response.get("errors", []),
                    "statusCode": response.get("statusCode", 500)
                }
        except Exception as e:
            return {
                "error": True,
                "errors": [str(e)],
                "statusCode": 500
            }
    
    # COMMANDS (Write operations)
    def create(self, request: CreateOrganizationRequest) -> Organization:
        """Create organization."""
        command = CreateOrganizationCommand(self.http_client, request)
        return command.execute()
    
    def update(self, organization_id: str, request: UpdateOrganizationRequest) -> Organization:
        """Update organization."""
        command = UpdateOrganizationCommand(self.http_client, organization_id, request)
        return command.execute()
    
    def add_user(self, organization_id: str, user_ids: List[str]) -> bool:
        """Add users to organization using the modern assign users endpoint."""
        return self.assign_users(organization_id, user_ids)
    
    def assign_users(self, organization_id: str, user_ids: List[str]) -> bool:
        """Assign users to organization using the /assign-users endpoint."""
        # Create the proper request object with correct field name
        request = AssignUsersToOrganizationRequest(userIds=user_ids)
        command = AssignUsersToOrganizationCommand(self.http_client, organization_id, request)
        return command.execute()
    
    def remove_user(self, organization_id: str, user_id: str) -> Dict[str, Any]:
        """Remove user from organization using the /remove-user endpoint."""
        command = RemoveUserFromOrganizationCommand(self.http_client, organization_id, user_id)
        return command.execute()
    
    def update_settings(self, organization_id: str, settings: Dict[str, Any]) -> OrganizationSettings:
        """Update organization settings."""
        command = UpdateOrganizationSettingsCommand(self.http_client, organization_id, settings)
        return command.execute()
    
    def update_shareable_deployment_settings(self, organization_id: int, status: bool) -> Dict[str, Any]:
        """Update organization shareable deployment settings."""
        try:
            # Prepare the payload according to API specification
            payload = {"status": status}
            
            # Make the API call
            response = self.http_client.post(f"organizations/{organization_id}/shareable-deployment", json_data=payload)
            return response
            
        except Exception as e:
            # Check if it's a 409 conflict (expected behavior when setting to same state)
            error_msg = str(e)
            if "409" in error_msg or "already" in error_msg.lower():
                # Return success for 409 conflicts (expected behavior)
                return {
                    "success": True,
                    "result": None,
                    "statusCode": 409,
                    "message": "Shareable deployment setting already in desired state"
                }
            
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def update_deployment_token(self, organization_id: int, deployment_token: str) -> Dict[str, Any]:
        """Update organization deployment token."""
        try:
            # Prepare the payload according to API specification
            payload = {"deploymentToken": deployment_token}
            
            # Make the API call
            response = self.http_client.post(f"organizations/{organization_id}/deployment-token", json_data=payload)
            return response
            
        except Exception as e:
            # Check if it's a 409 conflict (expected behavior when setting to same token)
            error_msg = str(e)
            if "409" in error_msg or "same token" in error_msg.lower() or "cannot be updated with same" in error_msg.lower():
                # Return success for 409 conflicts (expected behavior)
                return {
                    "success": True,
                    "result": None,
                    "statusCode": 409,
                    "message": "Deployment token already set to this value"
                }
            
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def delete(self, organization_id: int) -> Dict[str, Any]:
        """Delete organization by ID."""
        try:
            # Make the API call
            response = self.http_client.delete(f"organizations/{organization_id}")
            return response
            
        except Exception as e:
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def add_tags(self, organization_id: int, tags: List[str]) -> Dict[str, Any]:
        """Add tags to organization."""
        try:
            # Prepare the payload according to API specification
            payload = {"tags": tags}
            
            # Make the API call using PATCH method
            response = self.http_client.patch(f"organizations/{organization_id}/tags", json_data=payload)
            return response
            
        except Exception as e:
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def delete_tags(self, organization_id: int, tags: List[str]) -> Dict[str, Any]:
        """Delete tags from organization."""
        try:
            # Prepare the payload according to API specification
            payload = {"tags": tags}
            
            # Make the API call using DELETE method
            response = self.http_client.delete(f"organizations/{organization_id}/tags", json_data=payload)
            return response
            
        except Exception as e:
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def remove_tags(self, organization_id: int, tags: List[str]) -> Dict[str, Any]:
        """Remove tags from organization (alias for delete_tags)."""
        return self.delete_tags(organization_id, tags)

    # ------------------------------------------------------------------
    # New endpoints: user invitation & activation toggles
    # ------------------------------------------------------------------

    def resend_invitation(self, organization_id: int, user_id: str) -> Dict[str, Any]:
        """Resend organization invitation email to a user.

        Mirrors POST /organizations/{orgId}/resend-invitation/{userId}
        """
        try:
            return self.http_client.post(
                f"organizations/{organization_id}/resend-invitation/{user_id}",
                json_data={},
            )
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)],
            }

    def toggle_user_activation(self, organization_id: int, user_id: str) -> Dict[str, Any]:
        """Toggle active / inactive status for a user in the organization.

        Endpoint: POST /organizations/{orgId}/toggle-user-activation/{userId}
        """
        try:
            return self.http_client.post(
                f"organizations/{organization_id}/toggle-user-activation/{user_id}",
                json_data={},
            )
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)],
            } 