"""
Auth-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.auth import LoginRequest, LoginResponse
from ..http_client import HTTPClient


class LoginCommand(Command[LoginResponse]):
    """Command to login user."""
    
    def __init__(self, http_client: HTTPClient, request: Union[LoginRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> LoginResponse:
        """Execute the login command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = {
                "username": self.request.username,
                "password": self.request.password
            }
        
        response = self.http_client.post("auth/login", json_data=payload)
        
        if response.get("success"):
            result = response.get("result", {})
            return LoginResponse(**result)
        else:
            # This will typically raise an exception via http_client error handling
            raise Exception(f"Login failed: {response.get('error', 'Unknown error')}") 