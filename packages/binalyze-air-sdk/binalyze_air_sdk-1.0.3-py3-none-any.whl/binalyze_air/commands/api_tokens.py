"""
API Tokens commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any

from ..base import Command
from ..models.api_tokens import APIToken, CreateAPITokenRequest, UpdateAPITokenRequest
from ..http_client import HTTPClient


class CreateAPITokenCommand(Command[APIToken]):
    """Command to create a new API token."""
    
    def __init__(self, http_client: HTTPClient, request: CreateAPITokenRequest):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> APIToken:
        """Execute the command."""
        response = self.http_client.post(
            "api-tokens",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True, mode='json')
        )
        return APIToken(**response["result"])


class UpdateAPITokenCommand(Command[APIToken]):
    """Command to update an existing API token."""
    
    def __init__(self, http_client: HTTPClient, token_id: str, request: UpdateAPITokenRequest):
        self.http_client = http_client
        self.token_id = token_id
        self.request = request
    
    def execute(self) -> APIToken:
        """Execute the command."""
        response = self.http_client.put(
            f"api-tokens/{self.token_id}",
            json_data=self.request.model_dump()
        )
        return APIToken(**response["result"])


class DeleteAPITokenCommand(Command[Dict[str, Any]]):
    """Command to delete an API token."""
    
    def __init__(self, http_client: HTTPClient, token_id: str):
        self.http_client = http_client
        self.token_id = token_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.delete(f"api-tokens/{self.token_id}")
        return response 