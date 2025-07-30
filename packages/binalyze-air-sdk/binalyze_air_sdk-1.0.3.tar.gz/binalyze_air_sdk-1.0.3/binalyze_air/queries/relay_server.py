"""
Relay Server queries for the Binalyze AIR SDK.
"""

from typing import Optional

from ..base import Query
from ..models.relay_server import RelayServer, RelayServersList, RelayServersFilter
from ..http_client import HTTPClient


class GetRelayServersQuery(Query[RelayServersList]):
    """Query to get relay servers."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[RelayServersFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or RelayServersFilter()
    
    def execute(self) -> RelayServersList:
        """Execute the query to get relay servers."""
        # Use the filter's to_params() method to ensure proper parameter formatting
        # including required organizationId parameter
        params = self.filter_params.to_params()
        
        response = self.http_client.get('/relay-servers', params=params)
        return RelayServersList(**response['result'])


class GetRelayServerByIdQuery(Query[Optional[RelayServer]]):
    """Query to get a specific relay server by ID."""
    
    def __init__(self, http_client: HTTPClient, server_id: str):
        self.http_client = http_client
        self.server_id = server_id
    
    def execute(self) -> Optional[RelayServer]:
        """Execute the query to get a relay server by ID."""
        try:
            response = self.http_client.get(f'/relay-servers/{self.server_id}')
            return RelayServer(**response['result'])
        except Exception:
            return None 