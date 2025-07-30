"""
User Management-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.user_management import (
    UserManagementUser, AIUser, APIUser, UserFilter,
    Role, Privilege, UserGroup, UserGroupFilter
)
from ..http_client import HTTPClient


class ListUsersQuery(Query[List[UserManagementUser]]):
    """Query to list users."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[UserFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> List[UserManagementUser]:
        """Execute the list users query."""
        params = {}
        if self.filter_params:
            params = self.filter_params.model_dump(exclude_none=True)
        
        # FIX: Add default organization ID handling to prevent validation errors
        # API requires organizationIds parameter to be non-empty
        if "filter[organizationIds]" not in params and "organizationIds" not in params:
            params["filter[organizationIds]"] = "0"  # Default to organization 0
        
        response = self.http_client.get("user-management/users", params=params)
        
        if response.get("success"):
            users_data = response.get("result", {}).get("entities", [])
            return [UserManagementUser(**user) for user in users_data]
        
        return []


class GetUserQuery(Query[UserManagementUser]):
    """Query to get user by ID."""
    
    def __init__(self, http_client: HTTPClient, user_id: str):
        self.http_client = http_client
        self.user_id = user_id
    
    def execute(self) -> UserManagementUser:
        """Execute the get user query."""
        response = self.http_client.get(f"user-management/users/{self.user_id}")
        
        if response.get("success"):
            user_data = response.get("result", {})
            return UserManagementUser(**user_data)
        
        raise Exception(f"User not found: {self.user_id}")


class GetAIUserQuery(Query[AIUser]):
    """Query to get AI user."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> AIUser:
        """Execute the get AI user query."""
        response = self.http_client.get("user-management/users/ai-user")
        
        if response.get("success"):
            ai_user_data = response.get("result", {})
            return AIUser(**ai_user_data)
        
        raise Exception("AI user not found")


class GetAPIUserQuery(Query[APIUser]):
    """Query to get API user."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> APIUser:
        """Execute the get API user query."""
        response = self.http_client.get("user-management/users/api-user")
        
        if response.get("success"):
            api_user_data = response.get("result", {})
            return APIUser(**api_user_data)
        
        raise Exception("API user not found")


# Privilege Queries
class GetPrivilegesQuery(Query[List[Privilege]]):
    """Query to get privileges."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> List[Privilege]:
        """Execute the get privileges query."""
        response = self.http_client.get("user-management/roles")  # Note: privileges endpoint shares same path
        
        if response.get("success"):
            # Extract privileges from the response - they're typically embedded in role data
            privileges_data = response.get("result", [])
            # This might need adjustment based on actual API response structure
            return [Privilege(**privilege) for privilege in privileges_data]
        
        return []


# Role Queries
class ListRolesQuery(Query[List[Role]]):
    """Query to list roles."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> List[Role]:
        """Execute the list roles query."""
        response = self.http_client.get("user-management/roles")
        
        if response.get("success"):
            roles_data = response.get("result", [])
            return [Role(**role) for role in roles_data]
        
        return []


class GetRoleQuery(Query[Role]):
    """Query to get role by ID."""
    
    def __init__(self, http_client: HTTPClient, role_id: str):
        self.http_client = http_client
        self.role_id = role_id
    
    def execute(self) -> Role:
        """Execute the get role query."""
        response = self.http_client.get(f"user-management/roles/{self.role_id}")
        
        if response.get("success"):
            role_data = response.get("result", {})
            return Role(**role_data)
        
        raise Exception(f"Role not found: {self.role_id}")


# User Group Queries
class ListUserGroupsQuery(Query[List[UserGroup]]):
    """Query to list user groups."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[UserGroupFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> List[UserGroup]:
        """Execute the list user groups query."""
        params = {}
        if self.filter_params:
            params = self.filter_params.model_dump(exclude_none=True)
        
        # FIX: Add default organization ID handling to prevent validation errors
        # API requires organizationIds parameter to be non-empty
        if "filter[organizationIds]" not in params and "organizationIds" not in params:
            params["filter[organizationIds]"] = "0"  # Default to organization 0
        
        response = self.http_client.get("user-management/user-groups", params=params)
        
        if response.get("success"):
            groups_data = response.get("result", {}).get("entities", [])
            return [UserGroup(**group) for group in groups_data]
        
        return []


class GetUserGroupQuery(Query[UserGroup]):
    """Query to get user group by ID."""
    
    def __init__(self, http_client: HTTPClient, group_id: str):
        self.http_client = http_client
        self.group_id = group_id
    
    def execute(self) -> UserGroup:
        """Execute the get user group query."""
        response = self.http_client.get(f"user-management/user-groups/{self.group_id}")
        
        if response.get("success"):
            group_data = response.get("result", {})
            return UserGroup(**group_data)
        
        raise Exception(f"User group not found: {self.group_id}") 