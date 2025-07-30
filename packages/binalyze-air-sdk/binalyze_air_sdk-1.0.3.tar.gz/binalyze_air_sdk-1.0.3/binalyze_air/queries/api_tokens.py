"""
API Tokens queries for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any

from ..base import Query
from ..models.api_tokens import APIToken, APITokensPaginatedResponse, APITokenFilter
from ..http_client import HTTPClient


class ListAPITokensQuery(Query[APITokensPaginatedResponse]):
    """Query to list API tokens with optional filtering."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[APITokenFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params or APITokenFilter()
    
    def execute(self) -> APITokensPaginatedResponse:
        """Execute the query."""
        params = {}
        
        if self.filter_params.page_size is not None:
            params["pageSize"] = self.filter_params.page_size
        if self.filter_params.page_number is not None:
            params["pageNumber"] = self.filter_params.page_number
        if self.filter_params.sort_type is not None:
            params["sortType"] = self.filter_params.sort_type
        if self.filter_params.sort_by is not None:
            params["sortBy"] = self.filter_params.sort_by
        
        response = self.http_client.get("api-tokens", params=params)
        return APITokensPaginatedResponse(**response["result"])


class GetAPITokenQuery(Query[APIToken]):
    """Query to get a specific API token by ID."""
    
    def __init__(self, http_client: HTTPClient, token_id: str):
        self.http_client = http_client
        self.token_id = token_id
    
    def execute(self) -> APIToken:
        """Execute the query."""
        response = self.http_client.get(f"api-tokens/{self.token_id}")
        return APIToken(**response["result"]) 