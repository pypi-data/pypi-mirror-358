"""
Baseline-related queries for the Binalyze AIR SDK.
"""

from typing import Dict, Any

from ..base import Query
from ..http_client import HTTPClient


class GetBaselineComparisonReportQuery(Query[Dict[str, Any]]):
    """Query to get baseline comparison report by endpoint ID and task ID."""
    
    def __init__(self, http_client: HTTPClient, endpoint_id: str, task_id: str):
        self.http_client = http_client
        self.endpoint_id = endpoint_id
        self.task_id = task_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query to get baseline comparison report."""
        return self.http_client.get(f"baseline/comparison/report/{self.endpoint_id}/{self.task_id}") 