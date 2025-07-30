"""
Baseline-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any

from ..base import Command
from ..http_client import HTTPClient


class AcquireBaselineByFilterCommand(Command[Dict[str, Any]]):
    """Command to acquire baselines by asset filter criteria."""
    
    def __init__(self, http_client: HTTPClient, payload: Dict[str, Any]):
        self.http_client = http_client
        self.payload = payload
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to acquire baselines by filter."""
        return self.http_client.post("baseline/acquire", json_data=self.payload)


class CompareBaselineByEndpointCommand(Command[Dict[str, Any]]):
    """Command to compare baseline acquisition tasks by endpoint ID."""
    
    def __init__(self, http_client: HTTPClient, payload: Dict[str, Any]):
        self.http_client = http_client
        self.payload = payload
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to compare baseline tasks."""
        return self.http_client.post("baseline/compare", json_data=self.payload) 