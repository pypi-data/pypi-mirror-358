"""
Auth API for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..http_client import HTTPClient
from ..models.auth import AuthStatus, LoginRequest, LoginResponse
from ..queries.auth import CheckAuthStatusQuery
from ..commands.auth import LoginCommand


class AuthAPI:
    """Auth API with CQRS pattern - separated queries and commands."""

    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client

    # QUERIES (Read operations)
    def check_status(self) -> AuthStatus:
        """Check current authentication status."""
        query = CheckAuthStatusQuery(self.http_client)
        return query.execute()

    # COMMANDS (Write operations)
    def login(self, request: Union[LoginRequest, Dict[str, Any]]) -> LoginResponse:
        """Login user with credentials."""
        command = LoginCommand(self.http_client, request)
        return command.execute()
