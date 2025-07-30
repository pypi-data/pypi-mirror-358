"""
Preset Filters API for the Binalyze AIR SDK.
"""

from typing import Optional, Union, Dict, Any, List

from ..http_client import HTTPClient
from ..models.preset_filters import (
    PresetFilter, PresetFiltersList, PresetFiltersFilter, CreatePresetFilterRequest, UpdatePresetFilterRequest
)
from ..queries.preset_filters import GetPresetFiltersQuery, GetPresetFilterByIdQuery
from ..commands.preset_filters import CreatePresetFilterCommand, UpdatePresetFilterCommand, DeletePresetFilterCommand


class PresetFiltersAPI:
    """Preset Filters API with CQRS pattern - separated queries and commands."""

    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client

    # QUERIES (Read operations)
    def get_preset_filters(self, filter_params: Optional[PresetFiltersFilter] = None) -> PresetFiltersList:
        """Get preset filters with optional filtering."""
        query = GetPresetFiltersQuery(self.http_client, filter_params)
        return query.execute()

    def get_preset_filter_by_id(self, filter_id: Union[int, str]) -> Optional[PresetFilter]:
        """Get a specific preset filter by ID."""
        query = GetPresetFilterByIdQuery(self.http_client, str(filter_id))
        return query.execute()

    # Convenience methods for common queries
    def get_preset_filters_by_organization(self, organization_id: Union[int, str]) -> PresetFiltersList:
        """Get preset filters by organization ID."""
        filter_params = PresetFiltersFilter()
        filter_params.organization_id = int(organization_id)
        return self.get_preset_filters(filter_params)

    def get_preset_filters_by_type(self, filter_type: str, organization_id: Optional[Union[int, str]] = None) -> PresetFiltersList:
        """Get preset filters by type (e.g., 'ENDPOINT')."""
        filter_params = PresetFiltersFilter()
        filter_params.type = filter_type
        if organization_id is not None:
            filter_params.organization_id = int(organization_id)
        return self.get_preset_filters(filter_params)

    # COMMANDS (Write operations)
    def create_preset_filter(self, preset_filter_data: CreatePresetFilterRequest) -> PresetFilter:
        """Create a new preset filter."""
        command = CreatePresetFilterCommand(self.http_client, preset_filter_data)
        return command.execute()

    def update_preset_filter(self, filter_id: Union[int, str], preset_filter_data: UpdatePresetFilterRequest) -> PresetFilter:
        """Update an existing preset filter."""
        command = UpdatePresetFilterCommand(self.http_client, str(filter_id), preset_filter_data)
        return command.execute()

    def delete_preset_filter(self, filter_id: Union[int, str]) -> Dict[str, Any]:
        """Delete a preset filter by ID."""
        command = DeletePresetFilterCommand(self.http_client, str(filter_id))
        return command.execute()

    # Convenience methods
    def create_endpoint_filter(
        self, name: str, organization_id: Union[int, str], filter_criteria: List[Dict[str, Any]], created_by: str
    ) -> PresetFilter:
        """Create an endpoint preset filter."""
        preset_filter_data = CreatePresetFilterRequest(
            name=name,
            organizationId=int(organization_id),
            type="ENDPOINT",
            filter=filter_criteria,
            createdBy=created_by
        )
        return self.create_preset_filter(preset_filter_data)

    def get_endpoint_filters(self, organization_id: Optional[Union[int, str]] = None) -> PresetFiltersList:
        """Get all endpoint preset filters."""
        return self.get_preset_filters_by_type("ENDPOINT", organization_id)
