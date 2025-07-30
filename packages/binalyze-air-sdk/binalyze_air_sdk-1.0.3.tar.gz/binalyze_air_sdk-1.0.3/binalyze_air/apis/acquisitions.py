"""
Acquisitions API for the Binalyze AIR SDK using CQRS pattern.
"""

from typing import List, Optional, Dict, Any
from ..http_client import HTTPClient
from ..models.acquisitions import (
    AcquisitionProfile, AcquisitionProfileDetails, AcquisitionFilter,
    AcquisitionTaskRequest, ImageAcquisitionTaskRequest, CreateAcquisitionProfileRequest
)
from ..queries.acquisitions import (
    ListAcquisitionProfilesQuery,
    GetAcquisitionProfileQuery,
)
from ..commands.acquisitions import (
    CreateAcquisitionCommand,
    CreateImageAcquisitionCommand,
    CreateAcquisitionProfileCommand,
    AssignAcquisitionTaskCommand,
    AssignImageAcquisitionTaskCommand,
    UpdateAcquisitionProfileCommand,
    DeleteAcquisitionProfileCommand,
    CreateOffNetworkAcquisitionCommand,
    UpdateScheduledEvidenceAcquisitionCommand,
    UpdateScheduledImageAcquisitionCommand,
    ValidateOsqueryCommand,
)


class AcquisitionsAPI:
    """Acquisitions API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def list_profiles(
        self, 
        filter_params: Optional[AcquisitionFilter] = None,
        organization_ids: Optional[List[int]] = None,
        all_organizations: bool = False
    ) -> List[AcquisitionProfile]:
        """List acquisition profiles with optional filtering."""
        query = ListAcquisitionProfilesQuery(self.http_client, filter_params, organization_ids, all_organizations)
        return query.execute()
    
    def get_profile(self, profile_id: str) -> AcquisitionProfileDetails:
        """Get a specific acquisition profile by ID."""
        query = GetAcquisitionProfileQuery(self.http_client, profile_id)
        return query.execute()
    
    # COMMANDS (Write operations)
    def acquire(self, request) -> Dict[str, Any]:
        """Assign evidence acquisition task by filter."""
        command = CreateAcquisitionCommand(self.http_client, request)
        return command.execute()
    
    def acquire_image(self, request) -> Dict[str, Any]:
        """Assign image acquisition task by filter."""
        command = CreateImageAcquisitionCommand(self.http_client, request)
        return command.execute()
    
    def create_profile(self, request: CreateAcquisitionProfileRequest) -> Dict[str, Any]:
        """Create acquisition profile."""
        command = CreateAcquisitionProfileCommand(self.http_client, request)
        return command.execute()

    def update_profile(self, profile_id: str, request: CreateAcquisitionProfileRequest) -> Dict[str, Any]:
        """Update acquisition profile by ID."""
        command = UpdateAcquisitionProfileCommand(self.http_client, profile_id, request)
        return command.execute()
    
    def delete_profile(self, profile_id: str) -> Dict[str, Any]:
        """Delete acquisition profile by ID."""
        command = DeleteAcquisitionProfileCommand(self.http_client, profile_id)
        return command.execute()
    
    def acquire_off_network(self, request) -> Dict[str, Any]:
        """Create evidence acquisition off-network task."""
        command = CreateOffNetworkAcquisitionCommand(self.http_client, request)
        return command.execute()
    
    def update_scheduled_evidence_acquisition(self, task_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update scheduled evidence acquisition."""
        command = UpdateScheduledEvidenceAcquisitionCommand(self.http_client, task_id, request)
        return command.execute()
    
    def update_scheduled_image_acquisition(self, task_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update scheduled image acquisition."""
        command = UpdateScheduledImageAcquisitionCommand(self.http_client, task_id, request)
        return command.execute()
    
    def validate_osquery(self, request: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate osquery."""
        command = ValidateOsqueryCommand(self.http_client, request)
        return command.execute()

    # Legacy method aliases for backwards compatibility
    def assign_task(self, request: AcquisitionTaskRequest) -> List[Dict[str, Any]]:
        """Legacy alias for acquire method."""
        command = AssignAcquisitionTaskCommand(self.http_client, request)
        return command.execute()
    
    def assign_image_task(self, request: ImageAcquisitionTaskRequest) -> List[Dict[str, Any]]:
        """Legacy alias for acquire_image method."""
        command = AssignImageAcquisitionTaskCommand(self.http_client, request)
        return command.execute() 