"""
Policy-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, List, Optional, Union, cast

from ..base import Command
from ..models.policies import (
    CreatePolicyRequest, UpdatePolicyRequest, UpdatePoliciesPrioritiesRequest, 
    Policy, PolicyPriority, AssignPolicyRequest
)
from ..http_client import HTTPClient


class CreatePolicyCommand(Command[Policy]):
    """Command to create a new policy."""
    
    def __init__(self, http_client: HTTPClient, policy_data: Union[CreatePolicyRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.policy_data = policy_data
    
    def execute(self) -> Policy:
        """Execute the create policy command."""
        # Handle both dict and model objects
        if isinstance(self.policy_data, dict):
            payload = self.policy_data.copy()
        else:
            # Convert model to dict using model_dump with aliases
            payload = self.policy_data.model_dump(by_alias=True, exclude_none=True)
        
        response = self.http_client.post("policies", json_data=payload)
        
        # Parse using Pydantic models with automatic field mapping
        return Policy.model_validate(response.get("result", {}))


class UpdatePolicyCommand(Command[Policy]):
    """Command to update an existing policy."""
    
    def __init__(self, http_client: HTTPClient, policy_id: str, update_data: Union[UpdatePolicyRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.policy_id = policy_id
        self.update_data = update_data
    
    def execute(self) -> Policy:
        """Execute the update policy command."""
        # Handle both dict and model objects
        if isinstance(self.update_data, dict):
            payload = self.update_data.copy()
        else:
            # Convert model to dict using model_dump with aliases
            payload = self.update_data.model_dump(by_alias=True, exclude_none=True)
        
        response = self.http_client.put(f"policies/{self.policy_id}", json_data=payload)
        
        # Parse using Pydantic models with automatic field mapping
        return Policy.model_validate(response.get("result", {}))


class UpdatePoliciesPrioritiesCommand(Command[Dict[str, Any]]):
    """Command to update policy priorities."""
    
    def __init__(self, http_client: HTTPClient, priorities_data: Union[UpdatePoliciesPrioritiesRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.priorities_data = priorities_data
    
    def execute(self) -> Dict[str, Any]:
        """Execute the update policy priorities command."""
        # Handle both dict and model objects
        if isinstance(self.priorities_data, dict):
            payload = self.priorities_data.copy()
        else:
            # Convert model to dict using model_dump with aliases
            payload = self.priorities_data.model_dump(by_alias=True, exclude_none=True)
        
        return self.http_client.put("policies/priorities", json_data=payload)


class DeletePolicyCommand(Command[Dict[str, Any]]):
    """Command to delete a policy."""
    
    def __init__(self, http_client: HTTPClient, policy_id: str):
        self.http_client = http_client
        self.policy_id = policy_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete policy command."""
        return self.http_client.delete(f"policies/{self.policy_id}")


class AssignPolicyCommand(Command[Dict[str, Any]]):
    """Command to assign policy to endpoints."""
    
    def __init__(self, http_client: HTTPClient, assignment_data: Union[AssignPolicyRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.assignment_data = assignment_data
    
    def execute(self) -> Dict[str, Any]:
        """Execute the assign policy command."""
        # Handle both dict and model objects
        if isinstance(self.assignment_data, dict):
            payload = self.assignment_data.copy()
        else:
            # Use model_dump method to properly serialize the request object
            payload = self.assignment_data.model_dump(by_alias=True, exclude_none=True)
        
        return self.http_client.post("policies/assign", json_data=payload)


class UnassignPolicyCommand(Command[Dict[str, Any]]):
    """Command to unassign policy from endpoints."""
    
    def __init__(self, http_client: HTTPClient, policy_id: str, endpoint_ids: List[str]):
        self.http_client = http_client
        self.policy_id = policy_id
        self.endpoint_ids = endpoint_ids
    
    def execute(self) -> Dict[str, Any]:
        """Execute the unassign policy command."""
        payload: Dict[str, Any] = {}
        payload["policyId"] = self.policy_id
        payload["endpointIds"] = self.endpoint_ids
        
        return self.http_client.post("policies/unassign", json_data=payload)


class ExecutePolicyCommand(Command[Dict[str, Any]]):
    """Command to execute a policy on assigned endpoints."""
    
    def __init__(self, http_client: HTTPClient, policy_id: str, endpoint_ids: Optional[List[str]] = None):
        self.http_client = http_client
        self.policy_id = policy_id
        self.endpoint_ids = endpoint_ids
    
    def execute(self) -> Dict[str, Any]:
        """Execute the policy execution command."""
        payload: Dict[str, Any] = {}
        payload["policyId"] = self.policy_id
        
        if self.endpoint_ids:
            payload["endpointIds"] = self.endpoint_ids
        
        return self.http_client.post("policies/execute", json_data=payload)


class ActivatePolicyCommand(Command[Policy]):
    """Command to activate a policy."""
    
    def __init__(self, http_client: HTTPClient, policy_id: str):
        self.http_client = http_client
        self.policy_id = policy_id
    
    def execute(self) -> Policy:
        """Execute the activate policy command."""
        payload = {"status": "active"}
        response = self.http_client.put(f"policies/{self.policy_id}", json_data=payload)
        
        entity_data = response.get("result", {})
        return Policy.model_validate(entity_data)


class DeactivatePolicyCommand(Command[Policy]):
    """Command to deactivate a policy."""
    
    def __init__(self, http_client: HTTPClient, policy_id: str):
        self.http_client = http_client
        self.policy_id = policy_id
    
    def execute(self) -> Policy:
        """Execute the deactivate policy command."""
        payload = {"status": "inactive"}
        response = self.http_client.put(f"policies/{self.policy_id}", json_data=payload)
        
        entity_data = response.get("result", {})
        return Policy.model_validate(entity_data) 