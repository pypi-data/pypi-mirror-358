"""
Tasks API for the Binalyze AIR SDK using CQRS pattern.
"""

from typing import List, Optional, Dict, Any, Union
from ..http_client import HTTPClient
from ..models.tasks import Task, TaskFilter, TaskAssignment, CancelTaskByFilterRequest, GenerateOffNetworkZipPasswordRequest
from ..queries.tasks import (
    ListTasksQuery,
    GetTaskQuery,
    GetTaskAssignmentsQuery,
)
from ..commands.tasks import (
    CancelTaskCommand,
    CancelTaskAssignmentCommand,
    DeleteTaskAssignmentCommand,
    DeleteTaskCommand,
    CancelTaskByFilterCommand,
    GenerateOffNetworkZipPasswordCommand,
)


class TasksAPI:
    """Tasks API with CQRS pattern - separated queries and commands."""

    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client

    # QUERIES (Read operations)
    def list(self, filter_params: Optional[TaskFilter] = None, organization_ids: Optional[List[int]] = None) -> List[Task]:
        """List tasks with optional filtering."""
        query = ListTasksQuery(self.http_client, filter_params, organization_ids)
        return query.execute()

    def get(self, task_id: str) -> Task:
        """Get a specific task by ID."""
        query = GetTaskQuery(self.http_client, task_id)
        return query.execute()

    def get_assignments(self, task_id: str) -> List[TaskAssignment]:
        """Get task assignments for a specific task."""
        query = GetTaskAssignmentsQuery(self.http_client, task_id)
        return query.execute()

    # COMMANDS (Write operations)
    def cancel(self, task_id: str) -> Dict[str, Any]:
        """Cancel a task."""
        command = CancelTaskCommand(self.http_client, task_id)
        return command.execute()

    def cancel_assignment(self, assignment_id: str) -> Dict[str, Any]:
        """Cancel a task assignment."""
        command = CancelTaskAssignmentCommand(self.http_client, assignment_id)
        return command.execute()

    def delete_assignment(self, assignment_id: str) -> Dict[str, Any]:
        """Delete a task assignment."""
        command = DeleteTaskAssignmentCommand(self.http_client, assignment_id)
        return command.execute()

    def delete(self, task_id: str) -> Dict[str, Any]:
        """Delete a task."""
        command = DeleteTaskCommand(self.http_client, task_id)
        return command.execute()

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """Delete a task (alias for delete)."""
        return self.delete(task_id)

    def cancel_by_filter(self, request_data: Union[CancelTaskByFilterRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Cancel tasks by filter criteria."""
        command = CancelTaskByFilterCommand(self.http_client, request_data)
        return command.execute()

    def generate_off_network_zip_password(
        self, request_data: Union[GenerateOffNetworkZipPasswordRequest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate off-network zip password."""
        command = GenerateOffNetworkZipPasswordCommand(self.http_client, request_data)
        return command.execute()
