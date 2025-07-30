"""
HTTP client for Binalyze AIR API communications.
"""

import time
import requests
import urllib3
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

from .config import AIRConfig
from .exceptions import (
    AIRAPIError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    NetworkError,
)


class HTTPClient:
    """HTTP client for AIR API communications."""
    
    def __init__(self, config: AIRConfig):
        """Initialize the HTTP client with configuration."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config.api_token}",
            "User-Agent": "binalyze-air-sdk/1.0.0",
        })
        self.session.verify = config.verify_ssl
        
        # Disable SSL warnings when SSL verification is disabled
        if not config.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        # Remove leading slash if present
        endpoint = endpoint.lstrip("/")
        # Build full URL with API prefix
        return f"{self.config.host}/{self.config.api_prefix}/{endpoint}"
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        try:
            data = response.json()
        except ValueError:
            # If response is not JSON, create a basic structure
            data = {
                "success": False,
                "result": None,
                "statusCode": response.status_code,
                "errors": [response.text or "Unknown error"]
            }
        
        # Treat HTTP 204 No Content as a successful response with empty result
        if response.status_code == 204:
            return {
                "success": True,
                "result": None,
                "statusCode": response.status_code,
                "errors": []
            }
        
        # Handle specific known API bugs with better error messages
        if response.status_code == 500:
            error_message = data.get("errors", [""])[0] if data.get("errors") else ""
            
            # API-001: Policies endpoint parameter validation bug
            if "GET: /api/public/policies route has internal server error" in error_message:
                raise ValidationError(
                    "Missing required 'organizationIds' filter parameter. "
                    "Please provide organization IDs to filter policies. "
                    "(Note: This is a known API server bug that returns 500 instead of 400)",
                    status_code=400,  # What it should be
                    response_data=data
                )
            
            # API-002: Auto asset tags update endpoint bug  
            if "auto-asset-tag" in response.url and response.request.method == "PUT":
                raise ServerError(
                    "Auto asset tag update is currently unavailable due to a server bug. "
                    "Workaround: Delete the existing tag and create a new one with updated values. "
                    "(Note: This is a known API server issue)",
                    status_code=response.status_code,
                    response_data=data
                )
            
            # Generic 500 error with detailed message
            errors = data.get("errors", [f"Server error: {response.status_code}"])
            error_text = '; '.join(str(e) for e in errors)
            raise ServerError(
                f"Server error: {error_text}",
                status_code=response.status_code,
                response_data=data
            )
        
        elif response.status_code == 400:
            # Show detailed validation errors instead of generic "HTTP 400"
            errors = data.get("errors", [f"Bad request: {response.status_code}"])
            error_text = '; '.join(str(e) for e in errors)
            raise ValidationError(
                f"Validation error: {error_text}",
                status_code=response.status_code,
                response_data=data
            )
        
        elif response.status_code == 422:
            errors = data.get("errors", ["Validation failed"])
            # Handle complex error objects (like OSQuery validation errors)
            if errors and isinstance(errors[0], dict):
                error_messages = []
                for error in errors:
                    if isinstance(error, dict):
                        if 'message' in error:
                            error_messages.append(error['message'])
                        elif 'errors' in error and isinstance(error['errors'], list):
                            for nested_error in error['errors']:
                                if isinstance(nested_error, dict) and 'message' in nested_error:
                                    error_messages.append(nested_error['message'])
                                else:
                                    error_messages.append(str(nested_error))
                        else:
                            error_messages.append(str(error))
                    else:
                        error_messages.append(str(error))
                error_text = '; '.join(error_messages) if error_messages else "Validation failed"
            else:
                error_text = '; '.join(str(e) for e in errors)
            
            raise ValidationError(
                f"Validation error: {error_text}",
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code == 429:
            raise RateLimitError(
                "Rate limit exceeded. Please try again later.",
                status_code=response.status_code,
                response_data=data
            )
        elif response.status_code >= 500:
            raise ServerError(
                f"Server error: {response.status_code}",
                status_code=response.status_code,
                response_data=data
            )
        elif not response.ok:
            errors = data.get("errors", [f"HTTP {response.status_code}"])
            # Handle complex error objects (like OSQuery validation errors)
            if errors and isinstance(errors[0], dict):
                error_messages = []
                for error in errors:
                    if isinstance(error, dict):
                        # Extract meaningful error information from complex objects
                        if 'message' in error:
                            error_messages.append(error['message'])
                        elif 'errors' in error and isinstance(error['errors'], list):
                            # Handle nested error structures (like OSQuery validation)
                            for nested_error in error['errors']:
                                if isinstance(nested_error, dict) and 'message' in nested_error:
                                    error_messages.append(nested_error['message'])
                                else:
                                    error_messages.append(str(nested_error))
                        else:
                            error_messages.append(str(error))
                    else:
                        error_messages.append(str(error))
                error_text = '; '.join(error_messages) if error_messages else f"HTTP {response.status_code}"
            else:
                # Handle simple string errors with detailed error messages
                error_text = '; '.join(str(e) for e in errors)
            
            raise AIRAPIError(
                f"API error: {error_text}",
                status_code=response.status_code,
                response_data=data
            )
        
        return data
    
    def _handle_binary_response(self, response: requests.Response) -> requests.Response:
        """Handle binary file response without JSON parsing."""
        # Check for specific error status codes
        if response.status_code == 401:
            raise AuthenticationError(
                "Authentication failed. Check your API token.",
                status_code=response.status_code
            )
        elif response.status_code == 403:
            raise AuthorizationError(
                "Authorization failed. Insufficient permissions.",
                status_code=response.status_code
            )
        elif response.status_code == 404:
            raise NotFoundError(
                "Resource not found.",
                status_code=response.status_code
            )
        elif response.status_code == 422:
            raise ValidationError(
                "Validation error",
                status_code=response.status_code
            )
        elif response.status_code == 429:
            raise RateLimitError(
                "Rate limit exceeded. Please try again later.",
                status_code=response.status_code
            )
        elif response.status_code >= 500:
            raise ServerError(
                f"Server error: {response.status_code}",
                status_code=response.status_code
            )
        elif not response.ok:
            raise AIRAPIError(
                f"API error: HTTP {response.status_code}",
                status_code=response.status_code
            )
        
        return response
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic."""
        url = self._build_url(endpoint)
        last_exception = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    timeout=self.config.timeout
                )
                return self._handle_response(response)
                
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exception = NetworkError(f"Network error: {str(e)}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                raise last_exception
            
            except (RateLimitError, ServerError) as e:
                last_exception = e
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise
            
            except (AuthenticationError, AuthorizationError, NotFoundError, ValidationError) as e:
                # Don't retry these errors
                raise
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        
        raise AIRAPIError("All retry attempts failed")
    
    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        return self._make_request("GET", endpoint, params=params)
    
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make POST request."""
        return self._make_request("POST", endpoint, params=params, data=data, json_data=json_data)
    
    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make PUT request."""
        return self._make_request("PUT", endpoint, params=params, data=data, json_data=json_data)
    
    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make PATCH request."""
        return self._make_request("PATCH", endpoint, params=params, data=data, json_data=json_data)
    
    def delete(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make DELETE request."""
        return self._make_request("DELETE", endpoint, params=params, json_data=json_data)
    
    def get_binary(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make GET request for binary file downloads."""
        url = self._build_url(endpoint)
        last_exception = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = self.session.request(
                    method="GET",
                    url=url,
                    params=params,
                    timeout=self.config.timeout
                )
                return self._handle_binary_response(response)
                
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exception = NetworkError(f"Network error: {str(e)}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                raise last_exception
            
            except (RateLimitError, ServerError) as e:
                last_exception = e
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise
            
            except (AuthenticationError, AuthorizationError, NotFoundError, ValidationError) as e:
                # Don't retry these errors
                raise
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        
        raise AIRAPIError("All retry attempts failed")

    def upload_multipart(
        self,
        endpoint: str,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        method: str = "POST"
    ) -> Dict[str, Any]:
        """Make multipart file upload request.
        
        Args:
            endpoint: API endpoint
            files: Dictionary with file data for upload
            data: Form data fields
            params: Query parameters
            method: HTTP method (POST or PUT)
            
        Returns:
            Parsed JSON response
        """
        url = self._build_url(endpoint)
        last_exception = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                # Temporarily remove Content-Type from session headers
                # to let requests library set the appropriate multipart/form-data header
                original_content_type = self.session.headers.pop('Content-Type', None)
                
                try:
                    response = self.session.request(
                        method=method,
                        url=url,
                        params=params,
                        data=data,
                        files=files,
                        timeout=self.config.timeout
                    )
                    result = self._handle_response(response)
                finally:
                    # Restore original Content-Type header
                    if original_content_type:
                        self.session.headers['Content-Type'] = original_content_type
                
                return result
                
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exception = NetworkError(f"Network error: {str(e)}")
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                raise last_exception
            
            except (RateLimitError, ServerError) as e:
                last_exception = e
                if attempt < self.config.retry_attempts - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise
            
            except (AuthenticationError, AuthorizationError, NotFoundError, ValidationError) as e:
                # Don't retry these errors
                raise
        
        # If we get here, all retries failed
        if last_exception:
            raise last_exception
        
        raise AIRAPIError("All retry attempts failed") 