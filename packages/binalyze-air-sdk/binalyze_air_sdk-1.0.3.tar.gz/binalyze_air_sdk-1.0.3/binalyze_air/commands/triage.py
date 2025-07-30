"""
Triage-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.triage import (
    TriageRule, TriageTag, TriageProfile, CreateTriageRuleRequest,
    UpdateTriageRuleRequest, CreateTriageTagRequest, CreateTriageProfileRequest
)
from ..http_client import HTTPClient


class CreateTriageRuleCommand(Command[TriageRule]):
    """Command to create a new triage rule."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateTriageRuleRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> TriageRule:
        """Execute the command to create a triage rule."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            data = self.request.copy()
        else:
            # Convert SDK model fields to API fields
            request_dict = self.request.model_dump(exclude_none=True)
            data = {
                "description": request_dict.get("description") or request_dict.get("name", ""),
                "rule": request_dict.get("rule_content", ""),
                "engine": request_dict.get("type", "yara"),
                "searchIn": request_dict.get("search_in", "filesystem"),
                "organizationIds": [request_dict.get("organization_id", 0)]
            }
        
        response = self.http_client.post("triages/rules", json_data=data)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("description", ""),  # API uses description as name
            "description": entity_data.get("description"),
            "type": entity_data.get("engine"),  # API uses engine field
            "rule_content": entity_data.get("rule", ""),
            "search_in": entity_data.get("searchIn"),
            "enabled": entity_data.get("enabled", True),
            "severity": entity_data.get("severity", "medium"),
            "tags": entity_data.get("tags", []),
            "organization_id": entity_data.get("organizationIds", [0])[0] if entity_data.get("organizationIds") else 0,
            "organization_ids": entity_data.get("organizationIds", []),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
            "updated_by": entity_data.get("updatedBy"),
            "match_count": entity_data.get("matchCount", 0),
            "last_match": entity_data.get("lastMatch"),
            "deletable": entity_data.get("deletable"),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return TriageRule(**mapped_data)


class UpdateTriageRuleCommand(Command[TriageRule]):
    """Command to update an existing triage rule."""
    
    def __init__(self, http_client: HTTPClient, rule_id: str, request: Union[UpdateTriageRuleRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.rule_id = rule_id
        self.request = request
    
    def execute(self) -> TriageRule:
        """Execute the command to update a triage rule."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            data = self.request.copy()
        else:
            # Convert SDK model fields to API fields
            request_dict = self.request.model_dump(exclude_none=True)
            data = {}
            
            # Map SDK fields to API fields for update
            if "description" in request_dict or "name" in request_dict:
                data["description"] = request_dict.get("description") or request_dict.get("name", "")
            if "rule_content" in request_dict:
                data["rule"] = request_dict.get("rule_content")
            if "type" in request_dict:
                data["engine"] = request_dict.get("type")
            if "search_in" in request_dict:
                data["searchIn"] = request_dict.get("search_in")
            if "organization_id" in request_dict:
                data["organizationIds"] = [request_dict.get("organization_id")]
            if "enabled" in request_dict:
                data["enabled"] = request_dict.get("enabled")
        
        response = self.http_client.put(f"triages/rules/{self.rule_id}", json_data=data)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("description", ""),  # API uses description as name
            "description": entity_data.get("description"),
            "type": entity_data.get("engine"),  # API uses engine field
            "rule_content": entity_data.get("rule", ""),
            "search_in": entity_data.get("searchIn"),
            "enabled": entity_data.get("enabled", True),
            "severity": entity_data.get("severity", "medium"),
            "tags": entity_data.get("tags", []),
            "organization_id": entity_data.get("organizationIds", [0])[0] if entity_data.get("organizationIds") else 0,
            "organization_ids": entity_data.get("organizationIds", []),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
            "updated_by": entity_data.get("updatedBy"),
            "match_count": entity_data.get("matchCount", 0),
            "last_match": entity_data.get("lastMatch"),
            "deletable": entity_data.get("deletable"),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return TriageRule(**mapped_data)


class DeleteTriageRuleCommand(Command[Dict[str, Any]]):
    """Command to delete a triage rule."""
    
    def __init__(self, http_client: HTTPClient, rule_id: str):
        self.http_client = http_client
        self.rule_id = rule_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to delete a triage rule."""
        response = self.http_client.delete(f"triages/rules/{self.rule_id}")
        return response


class EnableTriageRuleCommand(Command[TriageRule]):
    """Command to enable a triage rule."""
    
    def __init__(self, http_client: HTTPClient, rule_id: str):
        self.http_client = http_client
        self.rule_id = rule_id
    
    def execute(self) -> TriageRule:
        """Execute the command to enable a triage rule."""
        data = {"enabled": True}
        
        response = self.http_client.put(f"triages/rules/{self.rule_id}", json_data=data)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("name"),
            "description": entity_data.get("description"),
            "type": entity_data.get("type"),
            "rule_content": entity_data.get("ruleContent", ""),
            "enabled": entity_data.get("enabled", True),
            "severity": entity_data.get("severity", "medium"),
            "tags": entity_data.get("tags", []),
            "organization_id": entity_data.get("organizationId", 0),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
            "updated_by": entity_data.get("updatedBy"),
            "match_count": entity_data.get("matchCount", 0),
            "last_match": entity_data.get("lastMatch"),
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return TriageRule(**mapped_data)





class CreateTriageTagCommand(Command[TriageTag]):
    """Command to create a new triage tag."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateTriageTagRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> TriageTag:
        """Execute the command to create a triage tag."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            data = self.request
        else:
            data = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.post("triages/tags", json_data=data)
        
        entity_data = response.get("result", {})
        
        mapped_data = {
            "id": entity_data.get("id") or entity_data.get("_id"),  # Handle both id and _id
            "name": entity_data.get("name"),
            "description": entity_data.get("description"),
            "color": entity_data.get("color", "#3498db"),
            "organization_id": entity_data.get("organizationId", 0),
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy", "Unknown"),  # Provide default for required field
            "usage_count": entity_data.get("usageCount") or entity_data.get("count", 0),  # Handle both count and usageCount
        }
        
        # Remove None values but keep defaults for required fields
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return TriageTag(**mapped_data)


 