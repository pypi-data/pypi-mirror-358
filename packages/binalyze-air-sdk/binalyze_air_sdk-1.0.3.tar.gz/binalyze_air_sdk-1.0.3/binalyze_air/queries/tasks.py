"""
Task-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query, ensure_organization_ids, format_organization_ids_param
from ..models.tasks import Task, TaskFilter, TaskData, PlatformEvidenceConfig, TaskConfig, DroneConfig, TaskAssignment
from ..http_client import HTTPClient


class ListTasksQuery(Query[List[Task]]):
    """Query to list tasks with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[TaskFilter] = None, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.filter_params = filter_params or TaskFilter()
        self.organization_ids = ensure_organization_ids(organization_ids)
    
    def execute(self) -> List[Task]:
        """Execute the query to list tasks."""
        params = self.filter_params.to_params()
        
        # Add organization IDs using utility function
        org_params = format_organization_ids_param(self.organization_ids)
        params.update(org_params)
        
        # Ensure consistent sorting to match API defaults
        if "sortBy" not in params:
            params["sortBy"] = "createdAt"
        if "sortType" not in params:
            params["sortType"] = "ASC"
        
        response = self.http_client.get("tasks", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing and error handling
        tasks = []
        for i, entity_data in enumerate(entities):
            try:
                # Validate data field structure before parsing
                if "data" in entity_data and isinstance(entity_data["data"], list):
                    # Fix: API sometimes returns data as list instead of object
                    if len(entity_data["data"]) == 1:
                        entity_data["data"] = entity_data["data"][0]
                    elif len(entity_data["data"]) == 0:
                        entity_data["data"] = None
                    # If multiple items, keep as is and let validation handle it
                
                task = Task.model_validate(entity_data)
                tasks.append(task)
            except Exception as e:
                # Log validation error but continue processing other tasks
                print(f"[WARN] Failed to parse task {i}: {e}")
                print(f"[DEBUG] Task data structure: {type(entity_data.get('data', 'missing'))}")
                # Create a minimal task object to avoid complete failure
                try:
                    minimal_data = {
                        "_id": entity_data.get("_id", f"unknown-{i}"),
                        "name": entity_data.get("name", "Unknown Task"),
                        "type": entity_data.get("type", "unknown"),
                        "status": entity_data.get("status", "unknown"),
                        "createdBy": entity_data.get("createdBy", "unknown"),
                        "organizationId": entity_data.get("organizationId", 0),
                        # Skip the problematic data field
                        "data": None
                    }
                    task = Task.model_validate(minimal_data)
                    tasks.append(task)
                except Exception as inner_e:
                    print(f"[ERROR] Could not create minimal task object: {inner_e}")
                    continue
        
        return tasks


class GetTaskQuery(Query[Task]):
    """Query to get a specific task by ID."""
    
    def __init__(self, http_client: HTTPClient, task_id: str):
        self.http_client = http_client
        self.task_id = task_id
    
    def execute(self) -> Task:
        """Execute the query to get a task."""
        response = self.http_client.get(f"tasks/{self.task_id}")
        
        task_data = response.get("result", {})
        
        # Validate and fix data field structure if needed
        if "data" in task_data and isinstance(task_data["data"], list):
            if len(task_data["data"]) == 1:
                task_data["data"] = task_data["data"][0]
            elif len(task_data["data"]) == 0:
                task_data["data"] = None
        
        # Use Pydantic parsing with proper field aliasing
        return Task.model_validate(task_data)


class GetTaskAssignmentsQuery(Query[List[TaskAssignment]]):
    """Query to get task assignments for a specific task."""
    
    def __init__(self, http_client: HTTPClient, task_id: str):
        self.http_client = http_client
        self.task_id = task_id
    
    def execute(self) -> List[TaskAssignment]:
        """Execute the query to get task assignments."""
        response = self.http_client.get(f"tasks/{self.task_id}/assignments")
        
        entities = response.get("result", {}).get("entities", [])
        
        # Use Pydantic parsing with proper field aliasing and error handling
        assignments = []
        for i, entity_data in enumerate(entities):
            try:
                assignment = TaskAssignment.model_validate(entity_data)
                assignments.append(assignment)
            except Exception as e:
                print(f"[WARN] Failed to parse task assignment {i}: {e}")
                # Continue processing other assignments
                continue
        
        return assignments 