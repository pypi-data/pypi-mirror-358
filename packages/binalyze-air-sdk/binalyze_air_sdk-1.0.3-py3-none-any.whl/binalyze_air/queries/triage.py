"""
Triage-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any

from ..base import Query
from ..models.triage import (
    TriageRule, TriageTag, TriageFilter, TriageRuleType, TriageSeverity, TriageStatus
)
from ..http_client import HTTPClient


class ListTriageRulesQuery(Query[List[TriageRule]]):
    """Query to list triage rules with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[TriageFilter] = None, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.filter_params = filter_params or TriageFilter()
        self.organization_ids = organization_ids or [0]
    
    def execute(self) -> List[TriageRule]:
        """Execute the query to list triage rules."""
        params = self.filter_params.to_params()
        
        # Add organization IDs
        params["filter[organizationIds]"] = ",".join(map(str, self.organization_ids))
        
        response = self.http_client.get("triages/rules", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        rules = []
        for entity_data in entities:
            mapped_data = {
                "id": entity_data.get("_id"),
                "name": entity_data.get("description", ""),  # Use description as name
                "description": entity_data.get("description"),
                "type": entity_data.get("engine", "yara"),  # Use engine as type
                "rule_content": entity_data.get("rule", ""),  # Try "rule" field
                "enabled": entity_data.get("enabled", True),
                "severity": entity_data.get("severity", "medium"),
                "tags": entity_data.get("tags", []),
                "search_in": entity_data.get("searchIn"),  # Map searchIn field
                "organization_id": entity_data.get("organizationId", 0),
                "organization_ids": entity_data.get("organizationIds", []),  # Map organizationIds array
                "created_at": entity_data.get("createdAt"),
                "updated_at": entity_data.get("updatedAt"),
                "created_by": entity_data.get("createdBy", "Unknown"),
                "updated_by": entity_data.get("updatedBy"),
                "match_count": entity_data.get("matchCount", 0),
                "last_match": entity_data.get("lastMatch"),
                "deletable": entity_data.get("deletable"),  # Map deletable field
            }
            
            # Remove None values
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            rules.append(TriageRule(**mapped_data))
        
        return rules


class GetTriageRuleQuery(Query[TriageRule]):
    """Query to get a specific triage rule by ID."""
    
    def __init__(self, http_client: HTTPClient, rule_id: str):
        self.http_client = http_client
        self.rule_id = rule_id
    
    def execute(self) -> TriageRule:
        """Execute the query to get triage rule details."""
        response = self.http_client.get(f"triages/rules/{self.rule_id}")
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("description", ""),  # Use description as name
            "description": entity_data.get("description"),
            "type": entity_data.get("engine", "yara"),  # Use engine as type
            "rule_content": entity_data.get("rule", ""),  # Try "rule" field
            "enabled": entity_data.get("enabled", True),
            "severity": entity_data.get("severity", "medium"),
            "tags": entity_data.get("tags", []),
            "search_in": entity_data.get("searchIn"),  # Map searchIn field
            "organization_id": entity_data.get("organizationId", 0),
            "organization_ids": entity_data.get("organizationIds", []),  # Map organizationIds array
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy", "Unknown"),
            "updated_by": entity_data.get("updatedBy"),
            "match_count": entity_data.get("matchCount", 0),
            "last_match": entity_data.get("lastMatch"),
            "deletable": entity_data.get("deletable"),  # Map deletable field
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return TriageRule(**mapped_data)


class GetTriageResultsQuery(Query[Dict[str, Any]]):
    """Query to get triage results for a specific task or rule."""
    
    def __init__(self, http_client: HTTPClient, task_id: Optional[str] = None, rule_id: Optional[str] = None):
        self.http_client = http_client
        self.task_id = task_id
        self.rule_id = rule_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query to get triage results."""
        params = {}
        
        if self.task_id:
            params["taskId"] = self.task_id
        if self.rule_id:
            params["ruleId"] = self.rule_id
        
        response = self.http_client.get("triages/results", params=params)
        return response.get("result", {})


class GetTriageMatchesQuery(Query[Dict[str, Any]]):
    """Query to get triage matches for analysis."""
    
    def __init__(self, http_client: HTTPClient, endpoint_id: str, task_id: str):
        self.http_client = http_client
        self.endpoint_id = endpoint_id
        self.task_id = task_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query to get triage matches."""
        params = {
            "endpointId": self.endpoint_id,
            "taskId": self.task_id
        }
        
        response = self.http_client.get("triages/matches", params=params)
        return response.get("result", {})


class ListTriageTagsQuery(Query[List[TriageTag]]):
    """Query to list triage tags."""
    
    def __init__(self, http_client: HTTPClient, organization_id: Optional[int] = None):
        self.http_client = http_client
        self.organization_id = organization_id or 0
    
    def execute(self) -> List[TriageTag]:
        """Execute the query to list triage tags."""
        # Use singular organizationId as per API documentation
        params = {"filter[organizationId]": str(self.organization_id)}
        
        response = self.http_client.get("triages/tags", params=params)
        
        # Handle different response formats: direct list or wrapped in result
        if isinstance(response, list):
            # Direct list response format
            entities = response
        elif isinstance(response, dict):
            # Wrapped response format - check if result is list or dict
            result_data = response.get("result", [])
            if isinstance(result_data, list):
                # result is a direct list of entities
                entities = result_data
            elif isinstance(result_data, dict):
                # result is a dict with entities inside
                entities = result_data.get("entities", [])
            else:
                entities = []
                
            # Fallback: if no entities found, try direct entities field
            if not entities and "entities" in response:
                entities = response.get("entities", [])
        else:
            # Unknown format
            entities = []
        
        tags = []
        for entity_data in entities:
            # Ensure entity_data is a dictionary
            if not isinstance(entity_data, dict):
                continue
                
            mapped_data = {
                "id": entity_data.get("id") or entity_data.get("_id"),  # Handle both id and _id
                "name": entity_data.get("name"),
                "description": entity_data.get("description"),
                "color": entity_data.get("color", "#3498db"),
                "created_at": entity_data.get("createdAt"),
                "created_by": entity_data.get("createdBy", "Unknown"),  # Provide default for required field
                "organization_id": entity_data.get("organizationId", 0),
                "usage_count": entity_data.get("usageCount") or entity_data.get("count", 0),  # Handle both count and usageCount
            }
            
            # Remove None values but keep defaults for required fields
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            tags.append(TriageTag(**mapped_data))
        
        return tags


class ListTriageProfilesQuery(Query[List[Dict[str, Any]]]):
    """Query to list triage profiles."""
    
    def __init__(self, http_client: HTTPClient, organization_id: Optional[int] = None):
        self.http_client = http_client
        self.organization_id = organization_id or 0
    
    def execute(self) -> List[Dict[str, Any]]:
        """Execute the query to list triage profiles."""
        params = {"filter[organizationId]": str(self.organization_id)}
        
        response = self.http_client.get("triages/profiles", params=params)
        return response.get("result", {}).get("entities", [])


class GetTriageProfileQuery(Query[Dict[str, Any]]):
    """Query to get a specific triage profile by ID."""
    
    def __init__(self, http_client: HTTPClient, profile_id: str):
        self.http_client = http_client
        self.profile_id = profile_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query to get triage profile details."""
        response = self.http_client.get(f"triages/profiles/{self.profile_id}")
        return response.get("result", {}) 