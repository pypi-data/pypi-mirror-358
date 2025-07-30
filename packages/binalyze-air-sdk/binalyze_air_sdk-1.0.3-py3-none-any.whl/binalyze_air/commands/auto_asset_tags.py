"""
Auto Asset Tags-related commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.auto_asset_tags import (
    AutoAssetTag, CreateAutoAssetTagRequest, UpdateAutoAssetTagRequest,
    StartTaggingRequest, TaggingResult, TaggingResponse
)
from ..http_client import HTTPClient
from ..exceptions import ServerError, ValidationError
from ..queries.auto_asset_tags import GetAutoAssetTagQuery


class CreateAutoAssetTagCommand(Command[AutoAssetTag]):
    """Command to create auto asset tag."""
    
    def __init__(self, http_client: HTTPClient, request: Union[CreateAutoAssetTagRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> AutoAssetTag:
        """Execute the create auto asset tag command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(by_alias=True)
        
        # Validate payload format before sending to API
        self._validate_payload_format(payload)
        
        try:
            response = self.http_client.post("auto-asset-tag", json_data=payload)
            
            if response.get("success"):
                tag_data = response.get("result", {})
                return AutoAssetTag(**tag_data)
            
            raise Exception(f"Failed to create auto asset tag: {response.get('error', 'Unknown error')}")
            
        except ServerError as e:
            if e.status_code == 500:
                # Provide better error message for format issues
                raise ValidationError(
                    f"Auto asset tag creation failed due to invalid format. "
                    f"Please ensure all conditions follow the required nested structure:\n"
                    f"- Each condition group must have 'operator' (and/or) and 'conditions' array\n"
                    f"- Individual conditions must have 'field', 'operator', and 'value'\n"
                    f"- Required fields: linuxConditions, windowsConditions, macosConditions\n"
                    f"Example format: {{\n"
                    f"  'linuxConditions': {{\n"
                    f"    'operator': 'and',\n"
                    f"    'conditions': [{{\n"
                    f"      'operator': 'or',\n"
                    f"      'conditions': [{{\n"
                    f"        'field': 'hostname',\n"
                    f"        'operator': 'contains',\n"
                    f"        'value': 'test'\n"
                    f"      }}]\n"
                    f"    }}]\n"
                    f"  }}\n"
                    f"}}\n"
                    f"Original error: {str(e)}"
                )
            else:
                # Re-raise other server errors
                raise
    
    def _validate_payload_format(self, payload: Dict[str, Any]) -> None:
        """Validate the payload format before sending to API."""
        required_fields = ["tag"]
        condition_fields = ["linuxConditions", "windowsConditions", "macosConditions"]
        
        # Check required fields
        for field in required_fields:
            if field not in payload:
                raise ValidationError(f"Missing required field: {field}")
        
        # Validate at least one condition is provided
        has_conditions = any(field in payload for field in condition_fields)
        if not has_conditions:
            raise ValidationError(
                f"At least one condition type must be provided: {', '.join(condition_fields)}"
            )
        
        # Validate condition structure for provided conditions
        for condition_type in condition_fields:
            if condition_type in payload:
                self._validate_condition_structure(payload[condition_type], condition_type)
    
    def _validate_condition_structure(self, condition: Dict[str, Any], condition_type: str) -> None:
        """Validate the structure of a condition group."""
        if not isinstance(condition, dict):
            raise ValidationError(f"{condition_type} must be an object")
        
        # Check for required fields in condition group
        if "operator" not in condition:
            raise ValidationError(f"{condition_type}.operator is required")
        
        if condition["operator"] not in ["and", "or"]:
            raise ValidationError(f"{condition_type}.operator must be 'and' or 'or'")
        
        if "conditions" not in condition:
            raise ValidationError(f"{condition_type}.conditions array is required")
        
        if not isinstance(condition["conditions"], list):
            raise ValidationError(f"{condition_type}.conditions must be an array")
        
        # Validate each nested condition
        for i, nested_condition in enumerate(condition["conditions"]):
            if not isinstance(nested_condition, dict):
                raise ValidationError(f"{condition_type}.conditions[{i}] must be an object")
            
            # Check if it's a group condition or individual condition
            if "conditions" in nested_condition:
                # It's a nested group - validate recursively
                self._validate_condition_structure(nested_condition, f"{condition_type}.conditions[{i}]")
            else:
                # It's an individual condition - validate fields
                required_condition_fields = ["field", "operator", "value"]
                for field in required_condition_fields:
                    if field not in nested_condition:
                        raise ValidationError(
                            f"{condition_type}.conditions[{i}].{field} is required"
                        )


class UpdateAutoAssetTagCommand(Command[AutoAssetTag]):
    """Command to update auto asset tag."""
    
    def __init__(self, http_client: HTTPClient, tag_id: str, request: Union[UpdateAutoAssetTagRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.tag_id = tag_id
        self.request = request
    
    def execute(self) -> AutoAssetTag:
        """Execute the update auto asset tag command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(by_alias=True)
        
        try:
            response = self.http_client.put(f"auto-asset-tag/{self.tag_id}", json_data=payload)
            
            if response.get("success"):
                tag_data = response.get("result", {})
                return AutoAssetTag(**tag_data)
            
            raise Exception(f"Failed to update auto asset tag: {response.get('error', 'Unknown error')}")
            
        except ServerError as e:
            # API-002 Workaround: If update fails with server error, provide helpful message
            # with alternative approach (delete + recreate)
            if "Auto asset tag update is currently unavailable" in str(e):
                # Get the current tag data for reference
                try:
                    get_query = GetAutoAssetTagQuery(self.http_client, self.tag_id)
                    current_tag = get_query.execute()
                    
                    # Merge current data with updates
                    updated_data = current_tag.model_dump()
                    updated_data.update(payload)
                    
                    raise ValidationError(
                        f"Auto asset tag update is currently unavailable due to a server bug. "
                        f"WORKAROUND: To update this tag, please:\n"
                        f"1. Delete the existing tag (ID: {self.tag_id})\n"
                        f"2. Create a new tag with the updated data:\n"
                        f"   Tag: {updated_data.get('tag', current_tag.tag)}\n"
                        f"   Organization IDs: {updated_data.get('organizationIds', current_tag.organizationIds)}\n"
                        f"   Linux Conditions: {updated_data.get('linuxConditions', current_tag.linuxConditions)}\n"
                        f"   Windows Conditions: {updated_data.get('windowsConditions', current_tag.windowsConditions)}\n"
                        f"   macOS Conditions: {updated_data.get('macosConditions', current_tag.macosConditions)}\n"
                        f"\nUse client.auto_asset_tags.delete('{self.tag_id}') then client.auto_asset_tags.create(new_data)"
                    )
                except Exception:
                    # If we can't get current data, provide generic workaround message
                    raise ValidationError(
                        f"Auto asset tag update is currently unavailable due to a server bug. "
                        f"WORKAROUND: Delete the existing tag (ID: {self.tag_id}) and create a new one with updated values."
                    )
            else:
                # Re-raise if it's a different server error
                raise


class DeleteAutoAssetTagCommand(Command[Dict[str, Any]]):
    """Command to delete auto asset tag."""
    
    def __init__(self, http_client: HTTPClient, tag_id: str):
        self.http_client = http_client
        self.tag_id = tag_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete auto asset tag command."""
        response = self.http_client.delete(f"auto-asset-tag/{self.tag_id}")
        
        if response.get("success"):
            return response
        
        raise Exception(f"Failed to delete auto asset tag: {response.get('error', 'Unknown error')}")


class StartTaggingCommand(Command[TaggingResponse]):
    """Command to start tagging process."""
    
    def __init__(self, http_client: HTTPClient, request: Union[StartTaggingRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> TaggingResponse:
        """Execute the start tagging command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            payload = self.request.model_dump(by_alias=True, exclude_none=True)
        
        response = self.http_client.post("auto-asset-tag/start-tagging", json_data=payload)
        
        if response.get("success"):
            result_data = response.get("result", [])
            # Handle the list response from the API
            return TaggingResponse.from_api_result(result_data)
        
        raise Exception(f"Failed to start tagging process: {response.get('error', 'Unknown error')}") 