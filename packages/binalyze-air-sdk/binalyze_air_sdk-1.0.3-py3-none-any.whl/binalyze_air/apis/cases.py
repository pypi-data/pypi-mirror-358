"""
Cases API for the Binalyze AIR SDK using CQRS pattern.
"""

from typing import List, Optional, Dict, Any
from ..http_client import HTTPClient
from ..models.cases import (
    Case, CaseActivity, CaseEndpoint, CaseTask, User, CaseFilter, CaseActivityFilter,
    CreateCaseRequest, UpdateCaseRequest, CaseNote, CaseEndpointFilter, CaseTaskFilter, CaseUserFilter
)
from ..models.assets import AssetFilter
from ..queries.cases import (
    ListCasesQuery,
    GetCaseQuery,
    GetCaseActivitiesQuery,
    GetCaseEndpointsQuery,
    GetCaseTasksQuery,
    GetCaseUsersQuery,
    CheckCaseNameQuery,
)
from ..commands.cases import (
    CreateCaseCommand,
    UpdateCaseCommand,
    CloseCaseCommand,
    OpenCaseCommand,
    ArchiveCaseCommand,
    ChangeCaseOwnerCommand,
    RemoveEndpointsFromCaseCommand,
    RemoveTaskAssignmentFromCaseCommand,
    ImportTaskAssignmentsToCaseCommand,
    AddNoteToCaseCommand,
    UpdateNoteToCaseCommand,
    DeleteNoteToCaseCommand,
    ExportCaseNotesCommand,
    ExportCasesCommand,
    ExportCaseEndpointsCommand,
    ExportCaseActivitiesCommand,
)


class CasesAPI:
    """Cases API with CQRS pattern - separated queries and commands."""

    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client

    # QUERIES (Read operations)
    def list(self, filter_params: Optional[CaseFilter] = None, organization_ids: Optional[List[int]] = None) -> List[Case]:
        """List cases with optional filtering."""
        query = ListCasesQuery(self.http_client, filter_params, organization_ids)
        return query.execute()

    def get(self, case_id: str) -> Case:
        """Get a specific case by ID."""
        query = GetCaseQuery(self.http_client, case_id)
        return query.execute()

    def get_activities(self, case_id: str, filter_params: Optional[CaseActivityFilter] = None) -> List[CaseActivity]:
        """Get activities for a specific case with optional filtering, pagination, and sorting."""
        query = GetCaseActivitiesQuery(self.http_client, case_id, filter_params)
        return query.execute()

    def get_endpoints(
        self, case_id: str, filter_params: Optional[CaseEndpointFilter] = None, organization_ids: Optional[List[int]] = None
    ) -> List[CaseEndpoint]:
        """Get endpoints for a specific case with comprehensive filtering support.

        Args:
            case_id: The case ID to get endpoints for
            filter_params: Optional CaseEndpointFilter with comprehensive filtering options
            organization_ids: Optional list of organization IDs (for backward compatibility)

        Returns:
            List of CaseEndpoint objects

        Note: If both filter_params and organization_ids are provided, organization_ids in filter_params takes precedence.
        """
        # Handle backward compatibility
        if filter_params is None:
            filter_params = CaseEndpointFilter()

        # If organization_ids is provided and not set in filter_params, use it
        if organization_ids is not None and filter_params.organization_ids is None:
            filter_params.organization_ids = organization_ids

        query = GetCaseEndpointsQuery(self.http_client, case_id, filter_params)
        return query.execute()

    def get_tasks(
        self, case_id: str, filter_params: Optional[CaseTaskFilter] = None, organization_ids: Optional[List[int]] = None
    ) -> List[CaseTask]:
        """Get tasks for a specific case with comprehensive filtering support.

        Args:
            case_id: The case ID to get tasks for
            filter_params: Optional CaseTaskFilter with comprehensive filtering options
            organization_ids: Optional list of organization IDs (for backward compatibility)

        Returns:
            List of CaseTask objects

        Note: If both filter_params and organization_ids are provided, organization_ids in filter_params takes precedence.
        """
        # Handle backward compatibility
        if filter_params is None:
            filter_params = CaseTaskFilter()

        # If organization_ids is provided and not set in filter_params, use it
        if organization_ids is not None and filter_params.organization_ids is None:
            filter_params.organization_ids = organization_ids

        query = GetCaseTasksQuery(self.http_client, case_id, filter_params)
        return query.execute()

    def get_users(
        self, case_id: str, filter_params: Optional[CaseUserFilter] = None, organization_ids: Optional[List[int]] = None
    ) -> List[User]:
        """Get users for a specific case with comprehensive filtering support.

        Args:
            case_id: The case ID to get users for
            filter_params: Optional CaseUserFilter with comprehensive filtering options
            organization_ids: Optional list of organization IDs (for backward compatibility)

        Returns:
            List of User objects

        Note: If both filter_params and organization_ids are provided, organization_ids in filter_params takes precedence.
        """
        # Handle backward compatibility
        if filter_params is None:
            filter_params = CaseUserFilter()

        # If organization_ids is provided and not set in filter_params, use it
        if organization_ids is not None and filter_params.organization_ids is None:
            filter_params.organization_ids = organization_ids

        query = GetCaseUsersQuery(self.http_client, case_id, filter_params)
        return query.execute()

    def check_name(self, name: str) -> bool:
        """Check if a case name is available."""
        query = CheckCaseNameQuery(self.http_client, name)
        return query.execute()

    # COMMANDS (Write operations)
    def create(self, case_data: CreateCaseRequest) -> Case:
        """Create a new case."""
        command = CreateCaseCommand(self.http_client, case_data)
        return command.execute()

    def update(self, case_id: str, update_data: UpdateCaseRequest) -> Case:
        """Update an existing case."""
        command = UpdateCaseCommand(self.http_client, case_id, update_data)
        return command.execute()

    def close(self, case_id: str) -> Case:
        """Close a case."""
        command = CloseCaseCommand(self.http_client, case_id)
        return command.execute()

    def open(self, case_id: str) -> Case:
        """Open a case."""
        command = OpenCaseCommand(self.http_client, case_id)
        return command.execute()

    def archive(self, case_id: str) -> Case:
        """Archive a case."""
        command = ArchiveCaseCommand(self.http_client, case_id)
        return command.execute()

    def change_owner(self, case_id: str, new_owner_id: str) -> Case:
        """Change case owner."""
        command = ChangeCaseOwnerCommand(self.http_client, case_id, new_owner_id)
        return command.execute()

    def remove_endpoints(self, case_id: str, filter_params: AssetFilter) -> Dict[str, Any]:
        """Remove endpoints from a case."""
        command = RemoveEndpointsFromCaseCommand(self.http_client, case_id, filter_params)
        return command.execute()

    def remove_task_assignment(self, case_id: str, task_assignment_id: str) -> Dict[str, Any]:
        """Remove task assignment from a case."""
        command = RemoveTaskAssignmentFromCaseCommand(self.http_client, case_id, task_assignment_id)
        return command.execute()

    def import_task_assignments(self, case_id: str, task_assignment_ids: List[str]) -> Dict[str, Any]:
        """Import task assignments to a case."""
        command = ImportTaskAssignmentsToCaseCommand(self.http_client, case_id, task_assignment_ids)
        return command.execute()

    def add_note(self, case_id: str, note_value: str) -> CaseNote:
        """Add a note to a case."""
        command = AddNoteToCaseCommand(self.http_client, case_id, note_value)
        return command.execute()

    def update_note(self, case_id: str, note_id: str, note_value: str) -> CaseNote:
        """Update a note in a case."""
        command = UpdateNoteToCaseCommand(self.http_client, case_id, note_id, note_value)
        return command.execute()

    def delete_note(self, case_id: str, note_id: str) -> Dict[str, Any]:
        """Delete a note from a case."""
        command = DeleteNoteToCaseCommand(self.http_client, case_id, note_id)
        return command.execute()

    def export_notes(self, case_id: str) -> Dict[str, Any]:
        """Export case notes as a file download (ZIP/CSV format)."""
        command = ExportCaseNotesCommand(self.http_client, case_id)
        return command.execute()

    def export_cases(self, filter_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export cases as a CSV file download."""
        command = ExportCasesCommand(self.http_client, filter_params)
        return command.execute()

    def export_endpoints(self, case_id: str, filter_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export case endpoints as a CSV file download with optional filtering."""
        command = ExportCaseEndpointsCommand(self.http_client, case_id, filter_params)
        return command.execute()

    def export_activities(self, case_id: str, filter_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Export case activities as a CSV file download with optional filtering and pagination."""
        command = ExportCaseActivitiesCommand(self.http_client, case_id, filter_params)
        return command.execute()
