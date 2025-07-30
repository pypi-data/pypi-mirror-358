"""
Webhook API for the Binalyze AIR SDK.
Provides webhook trigger functionality for programmatically calling webhook endpoints,
plus complete webhook management (CRUD operations).
"""

from typing import Dict, Any, Optional, List, Union
import json

from ..http_client import HTTPClient


class WebhookAPI:
    """Webhook API for triggering webhook endpoints programmatically and managing webhooks."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # WEBHOOK MANAGEMENT METHODS (CRUD Operations)
    def get_param_parsers(self) -> List[Dict[str, Any]]:
        """Get available webhook parameter parsers."""
        try:
            response = self.http_client.get("webhooks/param-parsers")
            if isinstance(response, dict) and response.get("result"):
                return response["result"]
            return []
        except Exception as e:
            return []
    
    def get_webhooks(self, organization_ids: Optional[List[int]] = None, **filter_params) -> Dict[str, Any]:
        """Get webhooks with optional filtering."""
        try:
            # Build query parameters
            params = {}
            
            # Add organization filter
            if organization_ids:
                params["filter[organizationIds]"] = ",".join([str(x) for x in organization_ids])
            else:
                params["filter[organizationIds]"] = "0"  # Default to organization 0
            
            # Add other filters
            for key, value in filter_params.items():
                if value is not None:
                    params[f"filter[{key}]"] = str(value)
            
            response = self.http_client.get("webhooks", params=params)
            return response
        except Exception as e:
            return {
                "success": False,
                "result": {"entities": [], "totalEntityCount": 0},
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def get_webhook_by_id(self, webhook_id: str) -> Dict[str, Any]:
        """Get a specific webhook by ID."""
        try:
            response = self.http_client.get(f"webhooks/{webhook_id}")
            return response
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def create_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new webhook."""
        try:
            response = self.http_client.post("webhooks", json_data=webhook_data)
            return response
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def update_webhook_by_id(self, webhook_id: str, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing webhook by ID."""
        try:
            response = self.http_client.put(f"webhooks/{webhook_id}", json_data=webhook_data)
            return response
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    def delete_webhook_by_id(self, webhook_id: str) -> Dict[str, Any]:
        """Delete a webhook by ID."""
        try:
            response = self.http_client.delete(f"webhooks/{webhook_id}")
            return response
        except Exception as e:
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    # WEBHOOK TRIGGERING METHODS (Legacy functionality preserved)
    def trigger_get(
        self, 
        slug: str, 
        data: str, 
        token: str,
        use_webhook_endpoint: bool = True
    ) -> Dict[str, Any]:
        """
        Trigger a webhook via GET request.
        
        Args:
            slug: Webhook slug/name
            data: Comma-separated hostnames or IP addresses  
            token: Webhook token
            use_webhook_endpoint: If True, use webhook endpoint directly (no auth needed)
                                If False, use authenticated API endpoint
        
        Returns:
            Dict containing task details and URLs
        """
        if use_webhook_endpoint:
            # Direct webhook call - no authentication needed, just token
            endpoint = f"webhook/{slug}/{data}"
            params = {"token": token}
            
            # Use raw HTTP client for webhook endpoints (they don't use standard API auth)
            import requests
            base_url = self.http_client.config.host
            url = f"{base_url}/api/{endpoint}"
            
            response = requests.get(
                url,
                params=params,
                verify=self.http_client.config.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                return {
                    "success": False,
                    "error": "Forbidden",
                    "message": "Invalid webhook token",
                    "statusCode": 403
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Not Found", 
                    "message": "Webhook not found",
                    "statusCode": 404
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text,
                    "statusCode": response.status_code
                }
        else:
            # Use authenticated API endpoint (if available)
            endpoint = f"webhook/{slug}/{data}"
            params = {"token": token}
            return self.http_client.get(endpoint, params=params)
    
    def trigger_post(
        self, 
        slug: str, 
        token: str,
        payload: Optional[Dict[str, Any]] = None,
        use_webhook_endpoint: bool = True
    ) -> Dict[str, Any]:
        """
        Trigger a webhook via POST request.
        
        Args:
            slug: Webhook slug/name
            token: Webhook token
            payload: Optional POST data/payload
            use_webhook_endpoint: If True, use webhook endpoint directly (no auth needed)
                                If False, use authenticated API endpoint
        
        Returns:
            Dict containing task details and URLs
        """
        if payload is None:
            payload = {}
            
        if use_webhook_endpoint:
            # Direct webhook call - no authentication needed, just token
            endpoint = f"webhook/{slug}"
            params = {"token": token}
            
            # Use raw HTTP client for webhook endpoints
            import requests
            base_url = self.http_client.config.host
            url = f"{base_url}/api/{endpoint}"
            
            response = requests.post(
                url,
                params=params,
                json=payload,
                verify=self.http_client.config.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                return {
                    "success": False,
                    "error": "Forbidden",
                    "message": "Invalid webhook token",
                    "statusCode": 403
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Not Found",
                    "message": "Webhook not found", 
                    "statusCode": 404
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text,
                    "statusCode": response.status_code
                }
        else:
            # Use authenticated API endpoint (if available)
            endpoint = f"webhook/{slug}"
            params = {"token": token}
            return self.http_client.post(endpoint, json_data=payload, params=params)
    
    def get_task_details(
        self, 
        slug: str, 
        token: str, 
        task_id: str,
        use_webhook_endpoint: bool = True
    ) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Get task assignment details from a webhook.
        
        Args:
            slug: Webhook slug/name
            token: Webhook token
            task_id: Task ID returned from webhook trigger
            use_webhook_endpoint: If True, use webhook endpoint directly (no auth needed)
                                If False, use authenticated API endpoint
        
        Returns:
            List of task assignment details or Dict with error info
        """
        if use_webhook_endpoint:
            # Direct webhook call - no authentication needed, just token
            endpoint = f"webhook/{slug}/assignments"
            params = {"token": token, "taskId": task_id}
            
            # Use raw HTTP client for webhook endpoints
            import requests
            base_url = self.http_client.config.host
            url = f"{base_url}/api/{endpoint}"
            
            response = requests.get(
                url,
                params=params,
                verify=self.http_client.config.verify_ssl,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                return {
                    "success": False,
                    "error": "Forbidden",
                    "message": "Invalid webhook token",
                    "statusCode": 403
                }
            elif response.status_code == 404:
                return {
                    "success": False,
                    "error": "Not Found",
                    "message": "Task not found or invalid task ID",
                    "statusCode": 404
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text,
                    "statusCode": response.status_code
                }
        else:
            # Use authenticated API endpoint (if available)
            endpoint = f"webhook/{slug}/assignments"
            params = {"token": token, "taskId": task_id}
            return self.http_client.get(endpoint, params=params)
    
    # CONVENIENCE METHODS (Aliases for backward compatibility)
    def call_webhook_get(self, slug: str, data: str, token: str) -> Dict[str, Any]:
        """Alias for trigger_get - backward compatibility."""
        return self.trigger_get(slug, data, token)
    
    def call_webhook_post(self, slug: str, token: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Alias for trigger_post - backward compatibility."""
        return self.trigger_post(slug, token, payload)
    
    def get_webhook_task_data(self, slug: str, token: str, task_id: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Alias for get_task_details - backward compatibility."""
        return self.get_task_details(slug, token, task_id) 