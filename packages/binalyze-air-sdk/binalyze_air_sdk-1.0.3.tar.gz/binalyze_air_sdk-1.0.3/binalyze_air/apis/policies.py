"""
Policies API for the Binalyze AIR SDK using CQRS pattern.
"""

from typing import List, Optional, Dict, Any, Union
from ..http_client import HTTPClient
from ..models.policies import (
    Policy, PolicyFilter, PolicyAssignment, PolicyExecution,
    CreatePolicyRequest, UpdatePolicyRequest, AssignPolicyRequest
)
from ..queries.policies import (
    ListPoliciesQuery,
    GetPolicyQuery,
    GetPolicyAssignmentsQuery,
    GetPolicyExecutionsQuery,
)
from ..commands.policies import (
    CreatePolicyCommand,
    UpdatePolicyCommand,
    DeletePolicyCommand,
    ActivatePolicyCommand,
    DeactivatePolicyCommand,
    AssignPolicyCommand,
    UnassignPolicyCommand,
    ExecutePolicyCommand,
)


class PoliciesAPI:
    """Policies API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list(self, filter_params: Optional[PolicyFilter] = None, organization_ids: Optional[List[int]] = None) -> List[Policy]:
        """List policies with optional filtering."""
        query = ListPoliciesQuery(self.http_client, filter_params, organization_ids)
        result = query.execute()
        # Extract the policies list from the paginated response
        if hasattr(result, 'entities'):
            return result.entities
        elif isinstance(result, list):
            return result
        else:
            return []
    
    def get(self, policy_id: str) -> Policy:
        """Get a specific policy by ID."""
        query = GetPolicyQuery(self.http_client, policy_id)
        return query.execute()
    
    def get_assignments(self, policy_id: str) -> List[PolicyAssignment]:
        """Get policy assignments."""
        query = GetPolicyAssignmentsQuery(self.http_client, policy_id)
        return query.execute()
    
    def get_executions(self, policy_id: str) -> List[PolicyExecution]:
        """Get policy executions."""
        query = GetPolicyExecutionsQuery(self.http_client, policy_id)
        return query.execute()
    
    def get_match_stats(self, filter_params: Optional[Dict[str, Any]] = None, organization_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Get policy match statistics with filtering.
        
        Args:
            filter_params: Optional filter parameters (name, platform, tags, etc.)
            organization_ids: List of organization IDs (defaults to [0])
        
        Returns:
            Dictionary containing policy match statistics
        """
        try:
            # Fix API-001: Ensure organizationIds are provided to prevent errors
            if organization_ids is None or len(organization_ids) == 0:
                organization_ids = [0]  # Default to organization 0
            
            # Build payload with default filter structure
            payload = {
                "name": "",
                "searchTerm": "",
                "ipAddress": "",
                "groupId": "",
                "groupFullPath": "",
                "managedStatus": [],
                "isolationStatus": [],
                "platform": [],
                "issue": "",
                "onlineStatus": [],
                "tags": [],
                "version": "",
                "policy": "",
                "includedEndpointIds": [],
                "excludedEndpointIds": [],
                "organizationIds": organization_ids
            }
            
            # Apply custom filter parameters if provided
            if filter_params:
                for key, value in filter_params.items():
                    if key in payload:
                        payload[key] = value
            
            # Use correct API endpoint: POST policies/match-stats (not GET policies/stats)
            response = self.http_client.post("policies/match-stats", json_data=payload)
            return response
            
        except Exception as e:
            # Return a simulated response for testing
            return {
                "success": False,
                "error": str(e),
                "result": []
            }
    
    # COMMANDS (Write operations)
    def create(self, policy_data: Union[CreatePolicyRequest, Dict[str, Any]]) -> Policy:
        """Create a new policy."""
        command = CreatePolicyCommand(self.http_client, policy_data)
        return command.execute()
    
    def update(self, policy_id: str, update_data: Union[UpdatePolicyRequest, Dict[str, Any]]) -> Policy:
        """Update an existing policy."""
        command = UpdatePolicyCommand(self.http_client, policy_id, update_data)
        return command.execute()
    
    def delete(self, policy_id: str) -> Dict[str, Any]:
        """Delete a policy."""
        command = DeletePolicyCommand(self.http_client, policy_id)
        return command.execute()
    
    def activate(self, policy_id: str) -> Policy:
        """Activate a policy."""
        command = ActivatePolicyCommand(self.http_client, policy_id)
        return command.execute()
    
    def deactivate(self, policy_id: str) -> Policy:
        """Deactivate a policy."""
        command = DeactivatePolicyCommand(self.http_client, policy_id)
        return command.execute()
    
    def assign(self, assignment_data: Union[AssignPolicyRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Assign policy to endpoints."""
        command = AssignPolicyCommand(self.http_client, assignment_data)
        return command.execute()
    
    def unassign(self, policy_id: str, endpoint_ids: List[str]) -> Dict[str, Any]:
        """Unassign policy from endpoints."""
        command = UnassignPolicyCommand(self.http_client, policy_id, endpoint_ids)
        return command.execute()
    
    def execute(self, policy_id: str, endpoint_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Execute a policy on assigned endpoints."""
        command = ExecutePolicyCommand(self.http_client, policy_id, endpoint_ids)
        return command.execute()
    
    def update_priorities(self, policy_ids: List[str], organization_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Update policy priorities.
        
        Args:
            policy_ids: List of policy IDs in priority order (System policy must be first)
            organization_ids: List of organization IDs (defaults to [0])
        
        Returns:
            Response dictionary with success status
        """
        try:
            # Fix API-001: Ensure organizationIds are provided to prevent issues
            if organization_ids is None or len(organization_ids) == 0:
                organization_ids = [0]  # Default to organization 0
            
            # Use correct API parameter names according to specification
            payload = {
                "ids": policy_ids,  # API expects 'ids', not 'policyIds'
                "organizationIds": organization_ids  # Required parameter
            }
            
            response = self.http_client.put("policies/priorities", json_data=payload)
            return response
        except Exception as e:
            # Return a simulated response for testing
            return {
                "success": False,
                "error": str(e),
                "updated_policies": []
            } 