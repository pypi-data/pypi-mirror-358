"""
Case-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.cases import (
    Case, CaseActivity, CaseEndpoint, CaseTask, User, CaseFilter, CaseActivityFilter,
    CaseEndpointFilter, CaseTaskFilter, CaseUserFilter
)
from ..http_client import HTTPClient


class ListCasesQuery(Query[List[Case]]):
    """Query to list cases with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[CaseFilter] = None, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.filter_params = filter_params or CaseFilter()
        self.organization_ids = organization_ids or [0]
    
    def execute(self) -> List[Case]:
        """Execute the query to list cases."""
        params = self.filter_params.to_params()
        
        # Add organization IDs
        params["filter[organizationIds]"] = ",".join(map(str, self.organization_ids))
        
        # Ensure consistent sorting to match API defaults
        if "sortBy" not in params:
            params["sortBy"] = "createdAt"
        if "sortType" not in params:
            params["sortType"] = "ASC"
        
        response = self.http_client.get("cases", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing
        return [Case.model_validate(entity_data) for entity_data in entities]


class GetCaseQuery(Query[Case]):
    """Query to get a specific case by ID."""
    
    def __init__(self, http_client: HTTPClient, case_id: str):
        self.http_client = http_client
        self.case_id = case_id
    
    def execute(self) -> Case:
        """Execute the query to get case details."""
        response = self.http_client.get(f"cases/{self.case_id}")
        
        entity_data = response.get("result", {})
        
        # Use Pydantic parsing with proper field aliasing
        return Case.model_validate(entity_data)


class GetCaseActivitiesQuery(Query[List[CaseActivity]]):
    """Query to get activities for a specific case."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, filter_params: Optional[CaseActivityFilter] = None):
        self.http_client = http_client
        self.case_id = case_id
        self.filter_params = filter_params or CaseActivityFilter()
    
    def execute(self) -> List[CaseActivity]:
        """Execute the query to get case activities."""
        params = {}
        
        # Add pagination parameters
        if self.filter_params.page_number is not None:
            params["pageNumber"] = self.filter_params.page_number
        if self.filter_params.page_size is not None:
            params["pageSize"] = self.filter_params.page_size
            
        # Add sorting parameters
        if self.filter_params.sort_by is not None:
            params["sortBy"] = self.filter_params.sort_by
        if self.filter_params.sort_type is not None:
            params["sortType"] = self.filter_params.sort_type
            
        # Add filter parameters
        if self.filter_params.performed_by is not None:
            params["filter[performedBy]"] = ",".join(self.filter_params.performed_by)
        if self.filter_params.types is not None:
            params["filter[types]"] = ",".join(self.filter_params.types)
        if self.filter_params.search_term is not None:
            params["filter[searchTerm]"] = self.filter_params.search_term
        if self.filter_params.occurred_at is not None:
            params["filter[occurredAt]"] = self.filter_params.occurred_at
        
        response = self.http_client.get(f"cases/{self.case_id}/activities", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing
        return [CaseActivity.model_validate(entity_data) for entity_data in entities]


class GetCaseEndpointsQuery(Query[List[CaseEndpoint]]):
    """Query to get endpoints for a specific case."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, filter_params: Optional[CaseEndpointFilter] = None):
        self.http_client = http_client
        self.case_id = case_id
        self.filter_params = filter_params or CaseEndpointFilter()
    
    def execute(self) -> List[CaseEndpoint]:
        """Execute the query to get case endpoints."""
        params = {}
        
        # Add pagination parameters
        if self.filter_params.page_number is not None:
            params["pageNumber"] = self.filter_params.page_number
        if self.filter_params.page_size is not None:
            params["pageSize"] = self.filter_params.page_size
            
        # Add sorting parameters
        if self.filter_params.sort_by is not None:
            params["sortBy"] = self.filter_params.sort_by
        if self.filter_params.sort_type is not None:
            params["sortType"] = self.filter_params.sort_type
            
        # Add filter parameters
        if self.filter_params.organization_ids is not None:
            params["filter[organizationIds]"] = ",".join(map(str, self.filter_params.organization_ids))
        else:
            # Default to organization 0 if not specified
            params["filter[organizationIds]"] = "0"
            
        if self.filter_params.search_term is not None:
            params["filter[searchTerm]"] = self.filter_params.search_term
        if self.filter_params.name is not None:
            params["filter[name]"] = self.filter_params.name
        if self.filter_params.ip_address is not None:
            params["filter[ipAddress]"] = self.filter_params.ip_address
        if self.filter_params.group_id is not None:
            params["filter[groupId]"] = self.filter_params.group_id
        if self.filter_params.group_full_path is not None:
            params["filter[groupFullPath]"] = self.filter_params.group_full_path
        if self.filter_params.label is not None:
            params["filter[label]"] = self.filter_params.label
        if self.filter_params.last_seen is not None:
            params["filter[lastSeen]"] = self.filter_params.last_seen
        if self.filter_params.managed_status is not None:
            params["filter[managedStatus]"] = ",".join(self.filter_params.managed_status)
        if self.filter_params.isolation_status is not None:
            params["filter[isolationStatus]"] = ",".join(self.filter_params.isolation_status)
        if self.filter_params.platform is not None:
            params["filter[platform]"] = ",".join(self.filter_params.platform)
        if self.filter_params.issue is not None:
            params["filter[issue]"] = ",".join(self.filter_params.issue)
        if self.filter_params.online_status is not None:
            params["filter[onlineStatus]"] = ",".join(self.filter_params.online_status)
        if self.filter_params.tags is not None:
            params["filter[tags]"] = ",".join(self.filter_params.tags)
        if self.filter_params.version is not None:
            params["filter[version]"] = self.filter_params.version
        if self.filter_params.policy is not None:
            params["filter[policy]"] = self.filter_params.policy
        if self.filter_params.included_endpoint_ids is not None:
            params["filter[includedEndpointIds]"] = ",".join(self.filter_params.included_endpoint_ids)
        if self.filter_params.excluded_endpoint_ids is not None:
            params["filter[excludedEndpointIds]"] = ",".join(self.filter_params.excluded_endpoint_ids)
        if self.filter_params.aws_regions is not None:
            params["filter[awsRegions]"] = ",".join(self.filter_params.aws_regions)
        if self.filter_params.azure_regions is not None:
            params["filter[azureRegions]"] = ",".join(self.filter_params.azure_regions)
        
        response = self.http_client.get(f"cases/{self.case_id}/endpoints", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing
        return [CaseEndpoint.model_validate(entity_data) for entity_data in entities]


class GetCaseTasksQuery(Query[List[CaseTask]]):
    """Query to get tasks for a specific case."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, filter_params: Optional[CaseTaskFilter] = None):
        self.http_client = http_client
        self.case_id = case_id
        self.filter_params = filter_params or CaseTaskFilter()
    
    def execute(self) -> List[CaseTask]:
        """Execute the query to get case tasks."""
        params = {}
        
        # Add pagination parameters
        if self.filter_params.page_number is not None:
            params["pageNumber"] = self.filter_params.page_number
        if self.filter_params.page_size is not None:
            params["pageSize"] = self.filter_params.page_size
            
        # Add sorting parameters
        if self.filter_params.sort_by is not None:
            params["sortBy"] = self.filter_params.sort_by
        if self.filter_params.sort_type is not None:
            params["sortType"] = self.filter_params.sort_type
            
        # Add filter parameters
        if self.filter_params.organization_ids is not None:
            params["filter[organizationIds]"] = ",".join(map(str, self.filter_params.organization_ids))
        else:
            # Default to organization 0 if not specified
            params["filter[organizationIds]"] = "0"
            
        if self.filter_params.search_term is not None:
            params["filter[searchTerm]"] = self.filter_params.search_term
        if self.filter_params.name is not None:
            params["filter[name]"] = self.filter_params.name
        if self.filter_params.endpoint_ids is not None:
            params["filter[endpointIds]"] = ",".join(self.filter_params.endpoint_ids)
        if self.filter_params.execution_type is not None:
            params["filter[executionType]"] = self.filter_params.execution_type
        if self.filter_params.status is not None:
            params["filter[status]"] = self.filter_params.status
        if self.filter_params.type is not None:
            params["filter[type]"] = self.filter_params.type
        if self.filter_params.asset_names is not None:
            params["filter[assetNames]"] = self.filter_params.asset_names
        if self.filter_params.started_by is not None:
            params["filter[startedBy]"] = self.filter_params.started_by
        
        response = self.http_client.get(f"cases/{self.case_id}/tasks", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing
        return [CaseTask.model_validate(entity_data) for entity_data in entities]


class GetCaseUsersQuery(Query[List[User]]):
    """Query to get users for a specific case."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, filter_params: Optional[CaseUserFilter] = None):
        self.http_client = http_client
        self.case_id = case_id
        self.filter_params = filter_params or CaseUserFilter()
    
    def execute(self) -> List[User]:
        """Execute the query to get case users."""
        params = {}
        
        # Add pagination parameters
        if self.filter_params.page_number is not None:
            params["pageNumber"] = self.filter_params.page_number
        if self.filter_params.page_size is not None:
            params["pageSize"] = self.filter_params.page_size
            
        # Add sorting parameters
        if self.filter_params.sort_by is not None:
            params["sortBy"] = self.filter_params.sort_by
        if self.filter_params.sort_type is not None:
            params["sortType"] = self.filter_params.sort_type
            
        # Add filter parameters
        if self.filter_params.organization_ids is not None:
            params["filter[organizationIds]"] = ",".join(map(str, self.filter_params.organization_ids))
        else:
            # Default to organization 0 if not specified
            params["filter[organizationIds]"] = "0"
            
        if self.filter_params.search_term is not None:
            params["filter[searchTerm]"] = self.filter_params.search_term
        
        response = self.http_client.get(f"cases/{self.case_id}/users", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing
        return [User.model_validate(entity_data) for entity_data in entities]


class CheckCaseNameQuery(Query[bool]):
    """Query to check if a case name is available."""
    
    def __init__(self, http_client: HTTPClient, name: str):
        self.http_client = http_client
        self.name = name
    
    def execute(self) -> bool:
        """Execute the query to check case name availability."""
        params = {"name": self.name}
        
        response = self.http_client.get("cases/check", params=params)
        
        # Return the actual result (whether name is taken/available)
        return response.get("result", False) 