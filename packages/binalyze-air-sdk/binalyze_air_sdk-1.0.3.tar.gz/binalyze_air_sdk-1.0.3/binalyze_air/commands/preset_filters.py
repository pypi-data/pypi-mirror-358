"""
Preset Filters commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any

from ..base import Command
from ..models.preset_filters import PresetFilter, CreatePresetFilterRequest, UpdatePresetFilterRequest
from ..http_client import HTTPClient


class CreatePresetFilterCommand(Command[PresetFilter]):
    """Command to create a preset filter."""
    
    def __init__(self, http_client: HTTPClient, preset_filter_data: CreatePresetFilterRequest):
        self.http_client = http_client
        self.preset_filter_data = preset_filter_data
    
    def execute(self) -> PresetFilter:
        """Execute the command to create a preset filter."""
        response = self.http_client.post(
            '/preset-filters',
            json_data=self.preset_filter_data.to_dict()
        )
        return PresetFilter(**response['result'])


class UpdatePresetFilterCommand(Command[PresetFilter]):
    """Command to update a preset filter."""
    
    def __init__(self, http_client: HTTPClient, filter_id: str, preset_filter_data: UpdatePresetFilterRequest):
        self.http_client = http_client
        self.filter_id = filter_id
        self.preset_filter_data = preset_filter_data
    
    def execute(self) -> PresetFilter:
        """Execute the command to update a preset filter."""
        response = self.http_client.put(
            f'/preset-filters/{self.filter_id}',
            json_data=self.preset_filter_data.to_dict()
        )
        return PresetFilter(**response['result'])


class DeletePresetFilterCommand(Command[Dict[str, Any]]):
    """Command to delete a preset filter."""
    
    def __init__(self, http_client: HTTPClient, filter_id: str):
        self.http_client = http_client
        self.filter_id = filter_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command to delete a preset filter."""
        response = self.http_client.delete(f'/preset-filters/{self.filter_id}')
        return response 