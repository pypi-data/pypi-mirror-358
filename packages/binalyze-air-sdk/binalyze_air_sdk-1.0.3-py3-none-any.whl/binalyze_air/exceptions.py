"""
Custom exceptions for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any


class AIRAPIError(Exception):
    """Base exception for all AIR API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class AuthenticationError(AIRAPIError):
    """Raised when authentication fails."""
    pass


class AuthorizationError(AIRAPIError):
    """Raised when authorization fails."""
    pass


class NotFoundError(AIRAPIError):
    """Raised when a resource is not found."""
    pass


class ValidationError(AIRAPIError):
    """Raised when request validation fails."""
    pass


class RateLimitError(AIRAPIError):
    """Raised when rate limit is exceeded."""
    pass


class ServerError(AIRAPIError):
    """Raised when server returns 5xx status codes."""
    pass


class NetworkError(AIRAPIError):
    """Raised when network-related errors occur."""
    pass 