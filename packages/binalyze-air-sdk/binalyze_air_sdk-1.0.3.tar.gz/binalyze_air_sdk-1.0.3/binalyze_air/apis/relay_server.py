"""
Relay Server API for the Binalyze AIR SDK.
"""

from typing import Optional, Union, Dict, Any

from ..http_client import HTTPClient
from ..models.relay_server import (
    RelayServer, RelayServersList, RelayServersFilter,
    RebootTaskRequest, ShutdownTaskRequest, LogRetrievalTaskRequest, VersionUpdateTaskRequest,
    UpdateTagsRequest, UpdateLabelRequest, UpdateAddressRequest
)
from ..queries.relay_server import GetRelayServersQuery, GetRelayServerByIdQuery
from ..commands.relay_server import (
    AssignRebootTaskCommand, AssignShutdownTaskCommand, AssignLogRetrievalTaskCommand,
    AssignVersionUpdateTaskCommand, DeleteRelayServerCommand, UpdateTagsCommand,
    UpdateLabelCommand, UpdateAddressCommand
)


class RelayServerAPI:
    """Relay Server API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def get_relay_servers(self, filter_params: Optional[RelayServersFilter] = None) -> RelayServersList:
        """Get relay servers with optional filtering."""
        query = GetRelayServersQuery(self.http_client, filter_params)
        return query.execute()
    
    def get_relay_server_by_id(self, server_id: Union[int, str]) -> Optional[RelayServer]:
        """Get a specific relay server by ID."""
        query = GetRelayServerByIdQuery(self.http_client, str(server_id))
        return query.execute()
    
    # Convenience methods for common queries
    def get_relay_servers_by_organization(self, organization_id: Union[int, str]) -> RelayServersList:
        """Get relay servers by organization ID."""
        filter_params = RelayServersFilter()
        filter_params.organization_id = int(organization_id)
        return self.get_relay_servers(filter_params)
    
    def get_online_relay_servers(self, organization_id: Optional[Union[int, str]] = None) -> RelayServersList:
        """Get online relay servers."""
        filter_params = RelayServersFilter()
        filter_params.online_status = "online"
        if organization_id is not None:
            filter_params.organization_id = int(organization_id)
        return self.get_relay_servers(filter_params)
    
    # COMMANDS (Write operations - Task assignments)
    def assign_reboot_task(self, relay_server_id: Union[int, str], task_request: RebootTaskRequest) -> Dict[str, Any]:
        """Assign reboot task to relay server."""
        command = AssignRebootTaskCommand(self.http_client, str(relay_server_id), task_request)
        return command.execute()
    
    def assign_shutdown_task(self, relay_server_id: Union[int, str], task_request: ShutdownTaskRequest) -> Dict[str, Any]:
        """Assign shutdown task to relay server."""
        command = AssignShutdownTaskCommand(self.http_client, str(relay_server_id), task_request)
        return command.execute()
    
    def assign_log_retrieval_task(self, relay_server_id: Union[int, str], task_request: LogRetrievalTaskRequest) -> Dict[str, Any]:
        """Assign log retrieval task to relay server."""
        command = AssignLogRetrievalTaskCommand(self.http_client, str(relay_server_id), task_request)
        return command.execute()
    
    def assign_version_update_task(self, relay_server_id: Union[int, str], task_request: VersionUpdateTaskRequest) -> Dict[str, Any]:
        """Assign version update task to relay server."""
        command = AssignVersionUpdateTaskCommand(self.http_client, str(relay_server_id), task_request)
        return command.execute()
    
    # COMMANDS (Write operations - Server management)
    def delete_relay_server(self, server_id: Union[int, str]) -> Dict[str, Any]:
        """Delete a relay server by ID."""
        command = DeleteRelayServerCommand(self.http_client, str(server_id))
        return command.execute()
    
    def update_tags(self, relay_server_id: Union[int, str], tags_request: UpdateTagsRequest) -> Dict[str, Any]:
        """Update tags for a relay server."""
        command = UpdateTagsCommand(self.http_client, str(relay_server_id), tags_request)
        return command.execute()
    
    def update_label(self, relay_server_id: Union[int, str], label_request: UpdateLabelRequest) -> Dict[str, Any]:
        """Update label for a relay server."""
        command = UpdateLabelCommand(self.http_client, str(relay_server_id), label_request)
        return command.execute()
    
    def update_address(self, relay_server_id: Union[int, str], address_request: UpdateAddressRequest) -> Dict[str, Any]:
        """Update address for a relay server."""
        command = UpdateAddressCommand(self.http_client, str(relay_server_id), address_request)
        return command.execute()
    
    # Convenience methods
    def get_relay_servers_count(self, organization_id: Optional[Union[int, str]] = None) -> int:
        """Get total relay servers count."""
        filter_params = RelayServersFilter()
        if organization_id is not None:
            filter_params.organization_id = int(organization_id)
        filter_params.page_size = 1  # We only need the count
        
        result = self.get_relay_servers(filter_params)
        return result.total_entity_count or 0 