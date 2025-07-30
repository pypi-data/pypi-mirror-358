"""
User Management-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.user_management import (
    UserManagementUser, CreateUserRequest, UpdateUserRequest,
    AIUser, CreateAIUserRequest, APIUser, CreateAPIUserRequest,
    ChangePasswordRequest, SetAPIUserPasswordRequest, ResetPasswordRequest,
    Role, CreateRoleRequest, UpdateRoleRequest,
    UserGroup, CreateUserGroupRequest, UpdateUserGroupRequest
)
from ..http_client import HTTPClient


class CreateUserCommand(Command[UserManagementUser]):
    """Command to create user."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> UserManagementUser:
        """Execute the create user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("user-management/users", json_data=payload)
        
        if response.get("success"):
            user_data = response.get("result", {})
            return UserManagementUser(**user_data)
        
        raise Exception(f"Failed to create user: {response.get('error', 'Unknown error')}")


class UpdateUserCommand(Command[UserManagementUser]):
    """Command to update user."""
    
    def __init__(self, http_client: HTTPClient, user_id: str, request: Union[UpdateUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.user_id = user_id
        self.request = request
    
    def execute(self) -> UserManagementUser:
        """Execute the update user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.put(f"user-management/users/{self.user_id}", json_data=payload)
        
        if response.get("success"):
            user_data = response.get("result", {})
            return UserManagementUser(**user_data)
        
        raise Exception(f"Failed to update user: {response.get('error', 'Unknown error')}")


class DeleteUserCommand(Command[Dict[str, Any]]):
    """Command to delete user."""
    
    def __init__(self, http_client: HTTPClient, user_id: str):
        self.http_client = http_client
        self.user_id = user_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete user command."""
        response = self.http_client.delete(f"user-management/users/{self.user_id}")
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to delete user: {response.get('error', 'Unknown error')}")


class CreateAIUserCommand(Command[AIUser]):
    """Command to create AI user."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateAIUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> AIUser:
        """Execute the create AI user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("user-management/users/ai-user", json_data=payload)
        
        if response.get("success"):
            ai_user_data = response.get("result", {})
            return AIUser(**ai_user_data)
        
        raise Exception(f"Failed to create AI user: {response.get('error', 'Unknown error')}")


class CreateAPIUserCommand(Command[APIUser]):
    """Command to create API user."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateAPIUserRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> APIUser:
        """Execute the create API user command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("user-management/users/api-user", json_data=payload)
        
        if response.get("success"):
            api_user_data = response.get("result", {})
            return APIUser(**api_user_data)
        
        raise Exception(f"Failed to create API user: {response.get('error', 'Unknown error')}")


# Password Management Commands
class ChangeCurrentUserPasswordCommand(Command[Dict[str, Any]]):
    """Command to change current user password."""
    
    def __init__(self, http_client: HTTPClient, request: Union[ChangePasswordRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the change current user password command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.put("user-management/users/change-password", json_data=payload)
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to change password: {response.get('error', 'Unknown error')}")


class SetAPIUserPasswordCommand(Command[Dict[str, Any]]):
    """Command to set API user password."""
    
    def __init__(self, http_client: HTTPClient, request: Union[SetAPIUserPasswordRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the set API user password command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.put("user-management/users/set-api-user-password", json_data=payload)
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to set API user password: {response.get('error', 'Unknown error')}")


class ResetPasswordCommand(Command[Dict[str, Any]]):
    """Command to reset user password."""
    
    def __init__(self, http_client: HTTPClient, user_id: str, request: Union[ResetPasswordRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.user_id = user_id
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the reset password command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post(f"user-management/users/{self.user_id}/reset-password", json_data=payload)
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to reset password: {response.get('error', 'Unknown error')}")


class ResetTFACommand(Command[Dict[str, Any]]):
    """Command to reset TFA for user."""
    
    def __init__(self, http_client: HTTPClient, user_id: str):
        self.http_client = http_client
        self.user_id = user_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the reset TFA command."""
        response = self.http_client.post(f"user-management/users/{self.user_id}/reset-tfa")
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to reset TFA: {response.get('error', 'Unknown error')}")


# Role Management Commands
class CreateRoleCommand(Command[Role]):
    """Command to create role."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateRoleRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Role:
        """Execute the create role command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("user-management/roles", json_data=payload)
        
        if response.get("success"):
            role_data = response.get("result", {})
            return Role(**role_data)
        
        raise Exception(f"Failed to create role: {response.get('error', 'Unknown error')}")


class UpdateRoleCommand(Command[Role]):
    """Command to update role."""
    
    def __init__(self, http_client: HTTPClient, role_id: str, request: Union[UpdateRoleRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.role_id = role_id
        self.request = request
    
    def execute(self) -> Role:
        """Execute the update role command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.put(f"user-management/roles/{self.role_id}", json_data=payload)
        
        if response.get("success"):
            role_data = response.get("result", {})
            return Role(**role_data)
        
        raise Exception(f"Failed to update role: {response.get('error', 'Unknown error')}")


class DeleteRoleCommand(Command[Dict[str, Any]]):
    """Command to delete role."""
    
    def __init__(self, http_client: HTTPClient, role_id: str):
        self.http_client = http_client
        self.role_id = role_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete role command."""
        response = self.http_client.delete(f"user-management/roles/{self.role_id}")
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to delete role: {response.get('error', 'Unknown error')}")


# User Group Management Commands
class CreateUserGroupCommand(Command[UserGroup]):
    """Command to create user group."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateUserGroupRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> UserGroup:
        """Execute the create user group command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.post("user-management/user-groups", json_data=payload)
        
        if response.get("success"):
            group_data = response.get("result", {})
            return UserGroup(**group_data)
        
        raise Exception(f"Failed to create user group: {response.get('error', 'Unknown error')}")


class UpdateUserGroupCommand(Command[UserGroup]):
    """Command to update user group."""
    
    def __init__(self, http_client: HTTPClient, group_id: str, request: Union[UpdateUserGroupRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.group_id = group_id
        self.request = request
    
    def execute(self) -> UserGroup:
        """Execute the update user group command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(exclude_none=True)
        
        response = self.http_client.put(f"user-management/user-groups/{self.group_id}", json_data=payload)
        
        if response.get("success"):
            group_data = response.get("result", {})
            return UserGroup(**group_data)
        
        raise Exception(f"Failed to update user group: {response.get('error', 'Unknown error')}")


class DeleteUserGroupCommand(Command[Dict[str, Any]]):
    """Command to delete user group."""
    
    def __init__(self, http_client: HTTPClient, group_id: str):
        self.http_client = http_client
        self.group_id = group_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete user group command."""
        response = self.http_client.delete(f"user-management/user-groups/{self.group_id}")
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to delete user group: {response.get('error', 'Unknown error')}") 