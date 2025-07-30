"""
Baseline API for the Binalyze AIR SDK using CQRS pattern.
"""

from typing import List, Optional, Dict, Any
from ..http_client import HTTPClient
from ..commands.baseline import (
    AcquireBaselineByFilterCommand,
    CompareBaselineByEndpointCommand,
)
from ..queries.baseline import (
    GetBaselineComparisonReportQuery,
)


class BaselineAPI:
    """Baseline API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # COMMANDS (Write operations)
    def acquire_by_filter(self, filter_data: Dict[str, Any], case_id: Optional[str] = None) -> Dict[str, Any]:
        """Acquire baselines by asset filter criteria."""
        payload = {
            "filter": filter_data,
            "caseId": case_id
        }
        
        command = AcquireBaselineByFilterCommand(self.http_client, payload)
        return command.execute()

    def compare_by_endpoint(self, endpoint_id: str, baseline_task_ids: List[str]) -> Dict[str, Any]:
        """Compare baseline acquisition tasks by endpoint ID."""
        payload = {
            "endpointId": endpoint_id,
            "taskIds": baseline_task_ids
        }
        
        command = CompareBaselineByEndpointCommand(self.http_client, payload)
        return command.execute()

    def get_comparison_report(self, endpoint_id: str, task_id: str) -> Dict[str, Any]:
        """Get comparison report by endpoint ID and task ID."""
        query = GetBaselineComparisonReportQuery(self.http_client, endpoint_id, task_id)
        return query.execute() 