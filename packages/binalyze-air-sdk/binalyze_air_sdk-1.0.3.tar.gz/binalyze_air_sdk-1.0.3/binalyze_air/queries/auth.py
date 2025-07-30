"""
Auth-related queries for the Binalyze AIR SDK.
"""

from ..base import Query
from ..models.auth import AuthStatus, User, UserProfile, UserRole
from ..http_client import HTTPClient


class CheckAuthStatusQuery(Query[AuthStatus]):
    """Query to check authentication status."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> AuthStatus:
        """Execute the auth status check query."""
        # Try different endpoint patterns since auth endpoints may vary
        endpoints_to_try = [
            "auth/check",  # Original pattern
            # Note: /api/public/auth/check may not exist in all API versions
            # The HTTP client will add the api_prefix automatically
        ]
        
        last_exception = None
        
        for endpoint in endpoints_to_try:
            try:
                response = self.http_client.get(endpoint)
                
                if response.get("success"):
                    result = response.get("result", {})
                    
                    # Use Pydantic to parse the User data with proper field aliasing
                    user = User.model_validate(result)
                    return AuthStatus(authenticated=True, user=user)
                else:
                    # Return unauthenticated status for failed responses
                    return AuthStatus(authenticated=False)
                    
            except Exception as e:
                last_exception = e
                continue  # Try next endpoint
        
        # If all endpoints failed, check if it's because auth features are disabled
        if last_exception and "auth-management-via-api" in str(last_exception):
            # Auth features are disabled - this is a configuration issue, not authentication failure
            # We can't determine auth status, so return a special state
            return AuthStatus(authenticated=False)
        
        # If we get here, all endpoints failed
        if last_exception:
            raise last_exception
        
        # Return unauthenticated status as fallback
        return AuthStatus(authenticated=False) 