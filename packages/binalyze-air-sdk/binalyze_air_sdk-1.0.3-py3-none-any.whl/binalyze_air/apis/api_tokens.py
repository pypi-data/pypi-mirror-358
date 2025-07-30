"""
API Tokens API for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any

from ..http_client import HTTPClient
from ..models.api_tokens import (
    APIToken, APITokensPaginatedResponse, APITokenFilter,
    CreateAPITokenRequest, UpdateAPITokenRequest
)
from ..queries.api_tokens import ListAPITokensQuery, GetAPITokenQuery
from ..commands.api_tokens import (
    CreateAPITokenCommand, UpdateAPITokenCommand, DeleteAPITokenCommand
)


class APITokensAPI:
    """API Tokens API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, filter_params: Optional[APITokenFilter] = None) -> APITokensPaginatedResponse:
        """List API tokens with optional filtering."""
        query = ListAPITokensQuery(self.http_client, filter_params)
        return query.execute()
    
    def get(self, token_id: str) -> APIToken:
        """Get a specific API token by ID."""
        query = GetAPITokenQuery(self.http_client, token_id)
        return query.execute()
    
    # COMMANDS (Write operations)
    def create(self, request: CreateAPITokenRequest) -> APIToken:
        """Create a new API token."""
        command = CreateAPITokenCommand(self.http_client, request)
        return command.execute()
    
    def update(self, token_id: str, request: UpdateAPITokenRequest) -> APIToken:
        """Update an existing API token."""
        command = UpdateAPITokenCommand(self.http_client, token_id, request)
        return command.execute()
    
    def delete(self, token_id: str) -> Dict[str, Any]:
        """Delete an API token."""
        command = DeleteAPITokenCommand(self.http_client, token_id)
        return command.execute() 