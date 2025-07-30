"""
Triage API for the Binalyze AIR SDK using CQRS pattern.
"""

from typing import List, Optional, Dict, Any, Union
from ..http_client import HTTPClient
from ..models.triage import (
    TriageRule, TriageTag, TriageFilter,
    CreateTriageRuleRequest, UpdateTriageRuleRequest, CreateTriageTagRequest
)
from ..queries.triage import (
    ListTriageRulesQuery,
    GetTriageRuleQuery,
    ListTriageTagsQuery,
)
from ..commands.triage import (
    CreateTriageRuleCommand,
    UpdateTriageRuleCommand,
    DeleteTriageRuleCommand,
    CreateTriageTagCommand,
)


class TriageAPI:
    """Triage API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list_rules(self, filter_params: Optional[TriageFilter] = None, organization_ids: Optional[List[int]] = None) -> List[TriageRule]:
        """List triage rules with optional filtering."""
        query = ListTriageRulesQuery(self.http_client, filter_params, organization_ids)
        return query.execute()
    
    def get_rule(self, rule_id: str) -> TriageRule:
        """Get a specific triage rule by ID."""
        query = GetTriageRuleQuery(self.http_client, rule_id)
        return query.execute()
    
    def get_rule_by_id(self, rule_id: str) -> TriageRule:
        """Get a specific triage rule by ID - alias for get_rule."""
        return self.get_rule(rule_id)
    
    def list_tags(self, organization_id: Optional[int] = None) -> List[TriageTag]:
        """List triage tags."""
        query = ListTriageTagsQuery(self.http_client, organization_id)
        return query.execute()
    
    def validate_rule(self, rule_content: str, engine: str = "yara") -> Dict[str, Any]:
        """Validate triage rule syntax."""
        try:
            # Prepare validation data
            validation_data = {
                "rule": rule_content,
                "engine": engine
            }
            
            # Call the API validation endpoint
            response = self.http_client.post("triages/rules/validate", json_data=validation_data)
            return response
            
        except Exception as e:
            # Return error response format matching API
            return {
                "success": False,
                "result": None,
                "statusCode": 500,
                "errors": [str(e)]
            }
    
    # COMMANDS (Write operations)
    def create_rule(self, request: Union[CreateTriageRuleRequest, Dict[str, Any]]) -> TriageRule:
        """Create a new triage rule."""
        command = CreateTriageRuleCommand(self.http_client, request)
        return command.execute()
    
    def update_rule(self, rule_id_or_data: Union[str, Dict[str, Any]], request: Optional[Union[UpdateTriageRuleRequest, Dict[str, Any]]] = None) -> TriageRule:
        """Update an existing triage rule."""
        # Handle both signatures: update_rule(rule_id, request) and update_rule(data_dict)
        if isinstance(rule_id_or_data, str) and request is not None:
            # Traditional signature: update_rule(rule_id, request)
            command = UpdateTriageRuleCommand(self.http_client, rule_id_or_data, request)
        elif isinstance(rule_id_or_data, dict):
            # Dict signature: update_rule(data_dict) where data_dict contains 'id'
            rule_id = rule_id_or_data.get('id')
            if not rule_id:
                raise ValueError("Rule ID must be provided in data dict or as separate parameter")
            command = UpdateTriageRuleCommand(self.http_client, rule_id, rule_id_or_data)
        else:
            raise ValueError("Invalid arguments for update_rule")
        
        return command.execute()
    
    def delete_rule(self, rule_id: str) -> Dict[str, Any]:
        """Delete a triage rule."""
        command = DeleteTriageRuleCommand(self.http_client, rule_id)
        return command.execute()
    
    def create_tag(self, request: Union[CreateTriageTagRequest, Dict[str, Any]]) -> TriageTag:
        """Create a new triage tag."""
        command = CreateTriageTagCommand(self.http_client, request)
        return command.execute()
    
    def assign_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a triage task to endpoints."""
        try:
            # Call the correct API endpoint for triage task assignment
            response = self.http_client.post("triages/triage", json_data=task_data)
            return response
        except Exception as e:
            # Import specific exception types
            from ..exceptions import AuthorizationError, AuthenticationError, ValidationError, AIRAPIError
            
            # Handle specific API errors and preserve status codes
            if isinstance(e, (AuthorizationError, AuthenticationError, ValidationError, AIRAPIError)):
                # Return the actual API error response if available
                if hasattr(e, 'response_data') and e.response_data:
                    return e.response_data
                else:
                    # Create response matching API format with actual status code
                    return {
                        "success": False,
                        "result": None,
                        "statusCode": getattr(e, 'status_code', 500),
                        "errors": [str(e)]
                    }
            else:
                # For unexpected errors, use 500
                return {
                    "success": False,
                    "result": None,
                    "statusCode": 500,
                    "errors": [str(e)]
                }
    
    def update_scheduled_triage(self, triage_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a scheduled triage task."""
        try:
            response = self.http_client.put(f"triages/schedule/triage/{triage_id}", json_data=update_data)
            return response
        except Exception as e:
            # Import specific exception types
            from ..exceptions import AuthorizationError, AuthenticationError, ValidationError, AIRAPIError
            
            # Handle specific API errors and preserve status codes
            if isinstance(e, (AuthorizationError, AuthenticationError, ValidationError, AIRAPIError)):
                # Return the actual API error response if available
                if hasattr(e, 'response_data') and e.response_data:
                    return e.response_data
                else:
                    # Create response matching API format with actual status code
                    return {
                        "success": False,
                        "result": None,
                        "statusCode": getattr(e, 'status_code', 500),
                        "errors": [str(e)]
                    }
            else:
                # For unexpected errors, use 500
                return {
                    "success": False,
                    "result": None,
                    "statusCode": 500,
                    "errors": [str(e)]
                }
    
    def create_off_network_triage_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an off-network triage task file."""
        try:
            response = self.http_client.post("triages/triage/off-network", json_data=task_data)
            return response
        except Exception as e:
            # Import specific exception types
            from ..exceptions import AuthorizationError, AuthenticationError, ValidationError, AIRAPIError
            
            # Handle specific API errors and preserve status codes
            if isinstance(e, (AuthorizationError, AuthenticationError, ValidationError, AIRAPIError)):
                # Return the actual API error response if available
                if hasattr(e, 'response_data') and e.response_data:
                    return e.response_data
                else:
                    # Create response matching API format with actual status code
                    return {
                        "success": False,
                        "result": None,
                        "statusCode": getattr(e, 'status_code', 500),
                        "errors": [str(e)]
                    }
            else:
                # For unexpected errors, use 500
                return {
                    "success": False,
                    "result": None,
                    "statusCode": 500,
                    "errors": [str(e)]
                } 