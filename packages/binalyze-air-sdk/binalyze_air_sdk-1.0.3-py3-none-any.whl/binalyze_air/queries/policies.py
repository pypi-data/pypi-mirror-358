"""
Policy-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.policies import (
    Policy, PolicyFilter, PolicyAssignment, PolicyExecution,
    PolicyRule, PolicyCondition, PolicyAction,
    PoliciesPaginatedResponse, PolicyMatchStats
)
from ..http_client import HTTPClient


class ListPoliciesQuery(Query[PoliciesPaginatedResponse]):
    """Query to list policies with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[PolicyFilter] = None, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.filter_params = filter_params or PolicyFilter()
        
        # Fix API-001: Ensure organizationIds are always provided to prevent 500 error
        if organization_ids is None or len(organization_ids) == 0:
            self.organization_ids = [0]  # Default to organization 0
        else:
            self.organization_ids = organization_ids
    
    def execute(self) -> PoliciesPaginatedResponse:
        """Execute the query to list policies."""
        # Validate organization_ids before making API call
        if not self.organization_ids or len(self.organization_ids) == 0:
            from ..exceptions import ValidationError
            raise ValidationError(
                "organizationIds parameter is required for listing policies. "
                "Please provide at least one organization ID."
            )
        
        params = self.filter_params.to_params()
        
        # Add organization IDs
        params["filter[organizationIds]"] = ",".join(map(str, self.organization_ids))
        
        response = self.http_client.get("policies", params=params)
        
        # Parse using Pydantic models with automatic field mapping
        return PoliciesPaginatedResponse.model_validate(response.get("result", {}))


class GetPolicyQuery(Query[Policy]):
    """Query to get a specific policy by ID."""
    
    def __init__(self, http_client: HTTPClient, policy_id: str):
        self.http_client = http_client
        self.policy_id = policy_id
    
    def execute(self) -> Policy:
        """Execute the query to get policy details."""
        response = self.http_client.get(f"policies/{self.policy_id}")
        
        # Parse using Pydantic models with automatic field mapping
        return Policy.model_validate(response.get("result", {}))


class GetPolicyAssignmentsQuery(Query[List[PolicyAssignment]]):
    """Query to get policy assignments."""
    
    def __init__(self, http_client: HTTPClient, policy_id: str):
        self.http_client = http_client
        self.policy_id = policy_id
    
    def execute(self) -> List[PolicyAssignment]:
        """Execute the query to get policy assignments."""
        response = self.http_client.get(f"policies/{self.policy_id}/assignments")
        
        entities = response.get("result", {}).get("entities", [])
        
        assignments = []
        for entity_data in entities:
            mapped_data = {
                "id": entity_data.get("_id"),
                "policy_id": entity_data.get("policyId"),
                "endpoint_id": entity_data.get("endpointId"),
                "assigned_at": entity_data.get("assignedAt"),
                "assigned_by": entity_data.get("assignedBy"),
                "status": entity_data.get("status", "active"),
            }
            
            # Remove None values
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            assignments.append(PolicyAssignment(**mapped_data))
        
        return assignments


class GetPolicyExecutionsQuery(Query[List[PolicyExecution]]):
    """Query to get policy execution history."""
    
    def __init__(self, http_client: HTTPClient, policy_id: str, limit: Optional[int] = None):
        self.http_client = http_client
        self.policy_id = policy_id
        self.limit = limit
    
    def execute(self) -> List[PolicyExecution]:
        """Execute the query to get policy executions."""
        params = {}
        if self.limit:
            params["limit"] = str(self.limit)
        
        response = self.http_client.get(f"policies/{self.policy_id}/executions", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        executions = []
        for entity_data in entities:
            mapped_data = {
                "id": entity_data.get("_id"),
                "policy_id": entity_data.get("policyId"),
                "endpoint_id": entity_data.get("endpointId"),
                "executed_at": entity_data.get("executedAt"),
                "status": entity_data.get("status"),
                "result": entity_data.get("result", {}),
                "errors": entity_data.get("errors", []),
                "duration": entity_data.get("duration"),
            }
            
            # Remove None values
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            executions.append(PolicyExecution(**mapped_data))
        
        return executions


class GetPolicyMatchStatsQuery(Query[PolicyMatchStats]):
    """Query to get policy match statistics."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[PolicyFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or PolicyFilter()
    
    def execute(self) -> PolicyMatchStats:
        """Execute the query to get policy match statistics."""
        params = self.filter_params.to_params()
        
        response = self.http_client.get("policies/match-stats", params=params)
        
        # Parse using Pydantic models with automatic field mapping
        return PolicyMatchStats.model_validate(response.get("result", {})) 