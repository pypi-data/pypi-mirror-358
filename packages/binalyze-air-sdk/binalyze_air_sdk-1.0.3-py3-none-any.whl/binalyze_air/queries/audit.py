"""
Audit-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from ..base import Query
from ..models.audit import (
    AuditLog, AuditSummary, AuditUserActivity, AuditSystemEvent, 
    AuditRetentionPolicy, AuditFilter, AuditLogsFilter, AuditLevel, AuditCategory, AuditAction
)
from ..http_client import HTTPClient


class ListAuditLogsQuery(Query[List[AuditLog]]):
    """Query to list audit logs with optional filtering - UPDATED for new POST-based API."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[AuditLogsFilter] = None, organization_ids: Optional[int] = None):
        self.http_client = http_client
        # Initialize filter with default organization IDs if not provided
        if filter_params is None:
            filter_params = AuditLogsFilter()
        
        # Set organization parameters if not already set in filter
        # Changed from List[int] to int to match new API spec
        if filter_params.organization_ids is None and organization_ids is not None:
            filter_params.organization_ids = organization_ids
        elif filter_params.organization_ids is None:
            filter_params.organization_ids = 0  # Default to organization 0
        
        self.filter_params = filter_params
    
    def execute(self) -> List[AuditLog]:
        """Execute the query to list audit logs using GET method with query parameters."""
        # Use GET method with query parameters as per API specification
        params = self.filter_params.to_params()
        
        print(f"[INFO] Using GET /audit-logs with params: {params}")
        
        try:
            response = self.http_client.get("audit-logs", params=params)
            
            # Handle response structure
            if isinstance(response, dict):
                entities = (
                    response.get("result", {}).get("entities", []) or  # Standard structure
                    response.get("entities", []) or  # Direct entities
                    response.get("data", []) or  # Alternative structure
                    response.get("logs", []) or  # Logs structure
                    []
                )
            else:
                entities = []
                
            print(f"[INFO] GET /audit-logs returned {len(entities)} audit logs")
            
        except Exception as e:
            print(f"[WARN] GET /audit-logs failed: {e}")
            return []
        
        logs = []
        for entity_data in entities:
            mapped_data = {
                "id": entity_data.get("_id") or entity_data.get("id"),
                "timestamp": entity_data.get("createdAt") or entity_data.get("timestamp"),
                "user_id": entity_data.get("userId"),
                "username": entity_data.get("performedBy") or entity_data.get("username"),
                "organization_id": entity_data.get("organizationId", 0),
                "category": entity_data.get("type") or entity_data.get("category"),
                "action": entity_data.get("action"),
                "resource_type": entity_data.get("resourceType"),
                "resource_id": entity_data.get("resourceId"),
                "resource_name": entity_data.get("resourceName"),
                "level": entity_data.get("level", "info"),
                "message": entity_data.get("description") or entity_data.get("message"),
                "details": entity_data.get("details", {}),
                "ip_address": entity_data.get("ipAddress"),
                "user_agent": entity_data.get("userAgent"),
                "session_id": entity_data.get("sessionId"),
                "correlation_id": entity_data.get("correlationId"),
                "success": entity_data.get("success", True),
                "error_code": entity_data.get("errorCode"),
                "duration": entity_data.get("duration"),
                "tags": entity_data.get("tags", []),
            }
            
            # Remove None values
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            logs.append(AuditLog(**mapped_data))
        
        return logs


class GetAuditLogQuery(Query[AuditLog]):
    """Query to get a specific audit log by ID."""
    
    def __init__(self, http_client: HTTPClient, log_id: str):
        self.http_client = http_client
        self.log_id = log_id
    
    def execute(self) -> AuditLog:
        """Execute the query to get audit log details."""
        response = self.http_client.get(f"audit-logs/{self.log_id}")
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "timestamp": entity_data.get("createdAt"),
            "user_id": entity_data.get("userId"),
            "username": entity_data.get("performedBy"),
            "organization_id": entity_data.get("organizationId", 0),
            "category": entity_data.get("type"),
            "action": entity_data.get("action"),
            "resource_type": entity_data.get("resourceType"),
            "resource_id": entity_data.get("resourceId"),
            "resource_name": entity_data.get("resourceName"),
            "level": entity_data.get("level", "info"),
            "message": entity_data.get("description"),
            "details": entity_data.get("details", {}),
            "ip_address": entity_data.get("ipAddress"),
            "user_agent": entity_data.get("userAgent"),
            "session_id": entity_data.get("sessionId"),
            "correlation_id": entity_data.get("correlationId"),
            "success": entity_data.get("success", True),
            "error_code": entity_data.get("errorCode"),
            "duration": entity_data.get("duration"),
            "tags": entity_data.get("tags", []),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return AuditLog(**mapped_data)


class GetAuditSummaryQuery(Query[AuditSummary]):
    """Query to get audit summary for a date range."""
    
    def __init__(self, http_client: HTTPClient, organization_id: int, start_date: datetime, end_date: datetime):
        self.http_client = http_client
        self.organization_id = organization_id
        self.start_date = start_date
        self.end_date = end_date
    
    def execute(self) -> AuditSummary:
        """Execute the query to get audit summary."""
        params = {
            "organizationId": str(self.organization_id),
            "startDate": self.start_date.isoformat(),
            "endDate": self.end_date.isoformat()
        }
        
        response = self.http_client.get("audit/summary", params=params)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "organization_id": entity_data.get("organizationId", self.organization_id),
            "date": entity_data.get("date", self.start_date),
            "total_events": entity_data.get("totalEvents", 0),
            "successful_events": entity_data.get("successfulEvents", 0),
            "failed_events": entity_data.get("failedEvents", 0),
            "authentication_events": entity_data.get("authenticationEvents", 0),
            "authorization_events": entity_data.get("authorizationEvents", 0),
            "data_access_events": entity_data.get("dataAccessEvents", 0),
            "system_change_events": entity_data.get("systemChangeEvents", 0),
            "user_action_events": entity_data.get("userActionEvents", 0),
            "api_call_events": entity_data.get("apiCallEvents", 0),
            "unique_users": entity_data.get("uniqueUsers", 0),
            "unique_ips": entity_data.get("uniqueIps", 0),
            "top_users": entity_data.get("topUsers", []),
            "top_actions": entity_data.get("topActions", []),
            "error_summary": entity_data.get("errorSummary", []),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return AuditSummary(**mapped_data)


class GetUserActivityQuery(Query[List[AuditUserActivity]]):
    """Query to get user activity audit logs."""
    
    def __init__(self, http_client: HTTPClient, organization_id: int, start_date: datetime, end_date: datetime, user_id: Optional[str] = None):
        self.http_client = http_client
        self.organization_id = organization_id
        self.start_date = start_date
        self.end_date = end_date
        self.user_id = user_id
    
    def execute(self) -> List[AuditUserActivity]:
        """Execute the query to get user activity."""
        params = {
            "organizationId": str(self.organization_id),
            "startDate": self.start_date.isoformat(),
            "endDate": self.end_date.isoformat()
        }
        
        if self.user_id:
            params["userId"] = self.user_id
        
        response = self.http_client.get("audit/user-activity", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        activities = []
        for entity_data in entities:
            mapped_data = {
                "user_id": entity_data.get("userId"),
                "username": entity_data.get("username"),
                "organization_id": entity_data.get("organizationId", self.organization_id),
                "date": entity_data.get("date"),
                "login_count": entity_data.get("loginCount", 0),
                "action_count": entity_data.get("actionCount", 0),
                "failed_login_count": entity_data.get("failedLoginCount", 0),
                "last_login": entity_data.get("lastLogin"),
                "last_action": entity_data.get("lastAction"),
                "unique_ips": entity_data.get("uniqueIps", []),
                "actions_by_category": entity_data.get("actionsByCategory", {}),
                "risk_score": entity_data.get("riskScore", 0.0),
            }
            
            # Remove None values
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            activities.append(AuditUserActivity(**mapped_data))
        
        return activities


class GetSystemEventsQuery(Query[List[AuditSystemEvent]]):
    """Query to get system events audit logs."""
    
    def __init__(self, http_client: HTTPClient, organization_id: int, start_date: datetime, end_date: datetime, severity: Optional[AuditLevel] = None):
        self.http_client = http_client
        self.organization_id = organization_id
        self.start_date = start_date
        self.end_date = end_date
        self.severity = severity
    
    def execute(self) -> List[AuditSystemEvent]:
        """Execute the query to get system events."""
        params = {
            "organizationId": str(self.organization_id),
            "startDate": self.start_date.isoformat(),
            "endDate": self.end_date.isoformat()
        }
        
        if self.severity:
            # Handle both enum and string values - FIXED
            if hasattr(self.severity, 'value'):
                params["severity"] = self.severity.value
            else:
                params["severity"] = self.severity
        
        response = self.http_client.get("audit/system-events", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        events = []
        for entity_data in entities:
            mapped_data = {
                "id": entity_data.get("_id"),
                "timestamp": entity_data.get("timestamp"),
                "event_type": entity_data.get("eventType"),
                "severity": entity_data.get("severity", "info"),
                "component": entity_data.get("component"),
                "message": entity_data.get("message"),
                "details": entity_data.get("details", {}),
                "organization_id": entity_data.get("organizationId", self.organization_id),
                "resolved": entity_data.get("resolved", False),
                "resolved_by": entity_data.get("resolvedBy"),
                "resolved_at": entity_data.get("resolvedAt"),
            }
            
            # Remove None values
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            events.append(AuditSystemEvent(**mapped_data))
        
        return events


class GetAuditRetentionPolicyQuery(Query[AuditRetentionPolicy]):
    """Query to get audit retention policy."""
    
    def __init__(self, http_client: HTTPClient, organization_id: int):
        self.http_client = http_client
        self.organization_id = organization_id
    
    def execute(self) -> AuditRetentionPolicy:
        """Execute the query to get audit retention policy."""
        response = self.http_client.get(f"audit/retention-policy/{self.organization_id}")
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "organization_id": entity_data.get("organizationId", self.organization_id),
            "retention_days": entity_data.get("retentionDays", 365),
            "auto_archive": entity_data.get("autoArchive", True),
            "archive_location": entity_data.get("archiveLocation"),
            "compress_archives": entity_data.get("compressArchives", True),
            "delete_after_archive": entity_data.get("deleteAfterArchive", False),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return AuditRetentionPolicy(**mapped_data)


class ExportAuditLogsQuery(Query[Dict[str, Any]]):
    """Query to export audit logs with filtering - UPDATED for new API."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[AuditLogsFilter] = None, format: str = "json", organization_ids: Optional[int] = None):
        self.http_client = http_client
        # Initialize filter with default organization IDs if not provided
        if filter_params is None:
            filter_params = AuditLogsFilter()
        
        # Set organization parameters if not already set in filter
        # Changed from List[int] to int to match new API spec
        if filter_params.organization_ids is None and organization_ids is not None:
            filter_params.organization_ids = organization_ids
        elif filter_params.organization_ids is None:
            filter_params.organization_ids = 0  # Default to organization 0
            
        self.filter_params = filter_params
        self.format = format
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query to export audit logs."""
        # Use filter's parameter generation
        params = self.filter_params.to_params()
        
        # Export endpoint returns binary data, not JSON - handle appropriately
        try:
            # Use raw HTTP request for binary data
            import requests
            url = f"{self.http_client.config.host}/api/public/audit-logs/export"
            headers = {
                "Authorization": f"Bearer {self.http_client.config.api_token}",
                "User-Agent": "binalyze-air-sdk/1.0.0"
            }
            
            raw_response = requests.get(
                url, 
                headers=headers, 
                params=params, 
                verify=self.http_client.config.verify_ssl,
                timeout=self.http_client.config.timeout
            )
            
            if raw_response.status_code == 200:
                # For binary/compressed data, return metadata about the export
                content_type = raw_response.headers.get("content-type", "application/octet-stream")
                content_length = len(raw_response.content) if raw_response.content else 0
                
                return {
                    "success": True,
                    "statusCode": 200,
                    "errors": [],
                    "result": {
                        "exported": True,
                        "format": "binary",
                        "content_type": content_type,
                        "content_length": content_length,
                        "data_preview": raw_response.content[:100].decode('utf-8', errors='ignore') if raw_response.content else ""
                    }
                }
            else:
                try:
                    error_data = raw_response.json()
                    return {
                        "success": False,
                        "statusCode": raw_response.status_code,
                        "errors": error_data.get("errors", [f"Export failed with status {raw_response.status_code}"]),
                        "result": None
                    }
                except:
                    return {
                        "success": False,
                        "statusCode": raw_response.status_code,
                        "errors": [f"Export failed with status {raw_response.status_code}: {raw_response.text}"],
                        "result": None
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "statusCode": 500,
                "errors": [f"Export request failed: {str(e)}"],
                "result": None
            } 