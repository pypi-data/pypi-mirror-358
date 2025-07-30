"""
User Management API for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any

from ..http_client import HTTPClient
from ..models.user_management import (
    UserManagementUser, UserFilter, CreateUserRequest, UpdateUserRequest,
    AIUser, CreateAIUserRequest, APIUser, CreateAPIUserRequest,
    ChangePasswordRequest, SetAPIUserPasswordRequest, ResetPasswordRequest,
    Role, CreateRoleRequest, UpdateRoleRequest, Privilege,
    UserGroup, CreateUserGroupRequest, UpdateUserGroupRequest, UserGroupFilter
)
from ..queries.user_management import (
    ListUsersQuery, GetUserQuery, GetAIUserQuery, GetAPIUserQuery,
    GetPrivilegesQuery, ListRolesQuery, GetRoleQuery,
    ListUserGroupsQuery, GetUserGroupQuery
)
from ..commands.user_management import (
    CreateUserCommand, UpdateUserCommand, DeleteUserCommand,
    CreateAIUserCommand, CreateAPIUserCommand,
    ChangeCurrentUserPasswordCommand, SetAPIUserPasswordCommand, 
    ResetPasswordCommand, ResetTFACommand,
    CreateRoleCommand, UpdateRoleCommand, DeleteRoleCommand,
    CreateUserGroupCommand, UpdateUserGroupCommand, DeleteUserGroupCommand
)


class UserManagementAPI:
    """User Management API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # USER QUERIES (Read operations)
    def list_users(self, filter_params: Optional[UserFilter] = None) -> List[UserManagementUser]:
        """List users with optional filtering."""
        query = ListUsersQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_user(self, user_id: str) -> UserManagementUser:
        """Get a specific user by ID."""
        query = GetUserQuery(self.http_client, user_id)
        return query.execute()
    
    # USER COMMANDS (Write operations)
    def create_user(self, request: CreateUserRequest) -> UserManagementUser:
        """Create a new user."""
        command = CreateUserCommand(self.http_client, request)
        return command.execute()
    
    def update_user(self, user_id: str, request: UpdateUserRequest) -> UserManagementUser:
        """Update an existing user."""
        command = UpdateUserCommand(self.http_client, user_id, request)
        return command.execute()
    
    def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete a user."""
        command = DeleteUserCommand(self.http_client, user_id)
        return command.execute()
    
    # PASSWORD MANAGEMENT COMMANDS
    def change_current_user_password(self, request: ChangePasswordRequest) -> Dict[str, Any]:
        """Change current user password."""
        command = ChangeCurrentUserPasswordCommand(self.http_client, request)
        return command.execute()
    
    def set_current_api_user_password_by_id(self, request: SetAPIUserPasswordRequest) -> Dict[str, Any]:
        """Set current API user password by ID."""
        command = SetAPIUserPasswordCommand(self.http_client, request)
        return command.execute()
    
    def reset_password_by_id(self, user_id: str, request: ResetPasswordRequest) -> Dict[str, Any]:
        """Reset password by user ID."""
        command = ResetPasswordCommand(self.http_client, user_id, request)
        return command.execute()
    
    def reset_tfa(self, user_id: str) -> Dict[str, Any]:
        """Reset TFA for user."""
        command = ResetTFACommand(self.http_client, user_id)
        return command.execute()
    
    # AI USER OPERATIONS
    def get_ai_user(self) -> AIUser:
        """Get the AI user."""
        query = GetAIUserQuery(self.http_client)
        return query.execute()
    
    def create_ai_user(self, request: CreateAIUserRequest) -> AIUser:
        """Create a new AI user."""
        command = CreateAIUserCommand(self.http_client, request)
        return command.execute()
    
    # API USER OPERATIONS
    def get_api_user(self) -> APIUser:
        """Get the API user."""
        query = GetAPIUserQuery(self.http_client)
        return query.execute()
    
    def create_api_user(self, request: CreateAPIUserRequest) -> APIUser:
        """Create a new API user."""
        command = CreateAPIUserCommand(self.http_client, request)
        return command.execute()
    
    # PRIVILEGE MANAGEMENT
    def get_privileges(self) -> List[Privilege]:
        """Get all privileges."""
        query = GetPrivilegesQuery(self.http_client)
        return query.execute()
    
    # ROLE MANAGEMENT OPERATIONS
    def get_roles(self) -> List[Role]:
        """Get all roles."""
        query = ListRolesQuery(self.http_client)
        return query.execute()
    
    def create_role(self, request: CreateRoleRequest) -> Role:
        """Create a new role."""
        command = CreateRoleCommand(self.http_client, request)
        return command.execute()
    
    def get_role_by_id(self, role_id: str) -> Role:
        """Get a specific role by ID."""
        query = GetRoleQuery(self.http_client, role_id)
        return query.execute()
    
    def update_role_by_id(self, role_id: str, request: UpdateRoleRequest) -> Role:
        """Update an existing role."""
        command = UpdateRoleCommand(self.http_client, role_id, request)
        return command.execute()
    
    def delete_role_by_id(self, role_id: str) -> Dict[str, Any]:
        """Delete a role."""
        command = DeleteRoleCommand(self.http_client, role_id)
        return command.execute()
    
    # USER GROUP MANAGEMENT OPERATIONS
    def get_user_groups(self, filter_params: Optional[UserGroupFilter] = None) -> List[UserGroup]:
        """Get all user groups with optional filtering."""
        query = ListUserGroupsQuery(self.http_client, filter_params)
        return query.execute()
    
    def create_user_group(self, request: CreateUserGroupRequest) -> UserGroup:
        """Create a new user group."""
        command = CreateUserGroupCommand(self.http_client, request)
        return command.execute()
    
    def get_user_group_by_id(self, group_id: str) -> UserGroup:
        """Get a specific user group by ID."""
        query = GetUserGroupQuery(self.http_client, group_id)
        return query.execute()
    
    def delete_user_group_by_id(self, group_id: str) -> Dict[str, Any]:
        """Delete a user group."""
        command = DeleteUserGroupCommand(self.http_client, group_id)
        return command.execute()
    
    def update_user_group_by_id(self, group_id: str, request: UpdateUserGroupRequest) -> UserGroup:
        """Update an existing user group."""
        command = UpdateUserGroupCommand(self.http_client, group_id, request)
        return command.execute()
    
    # CONVENIENCE ALIASES
    def list(self, filter_params: Optional[UserFilter] = None) -> List[UserManagementUser]:
        """Alias for list_users."""
        return self.list_users(filter_params)
    
    def get(self, user_id: str) -> UserManagementUser:
        """Alias for get_user."""
        return self.get_user(user_id)
    
    def create(self, request: CreateUserRequest) -> UserManagementUser:
        """Alias for create_user."""
        return self.create_user(request)
    
    def update(self, user_id: str, request: UpdateUserRequest) -> UserManagementUser:
        """Alias for update_user."""
        return self.update_user(user_id, request)
    
    def delete(self, user_id: str) -> Dict[str, Any]:
        """Alias for delete_user."""
        return self.delete_user(user_id) 