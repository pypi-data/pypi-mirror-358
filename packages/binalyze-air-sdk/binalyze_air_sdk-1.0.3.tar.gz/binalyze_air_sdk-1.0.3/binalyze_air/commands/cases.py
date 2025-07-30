"""
Case-related commands for the Binalyze AIR SDK.
Fixed to match API documentation exactly.
"""

from typing import List, Dict, Any, Optional, Union

from ..base import Command, ensure_organization_ids, format_organization_ids_param
from ..models.cases import CreateCaseRequest, UpdateCaseRequest, Case, CaseNote
from ..models.assets import AssetFilter
from ..http_client import HTTPClient


class CreateCaseCommand(Command[Case]):
    """Command to create a new case - FIXED endpoint URL."""
    
    def __init__(self, http_client: HTTPClient, case_data: CreateCaseRequest):
        self.http_client = http_client
        self.case_data = case_data
    
    def execute(self) -> Case:
        """Execute the create case command."""
        payload = {
            "organizationId": self.case_data.organization_id,
            "name": self.case_data.name,
            "ownerUserId": self.case_data.owner_user_id,
            "visibility": self.case_data.visibility,
            "assignedUserIds": self.case_data.assigned_user_ids,
        }
        
        # FIXED: Remove api/public/ prefix
        response = self.http_client.post("cases", json_data=payload)
        
        # Use Pydantic parsing with proper field aliasing
        entity_data = response.get("result", {})
        return Case.model_validate(entity_data)


class UpdateCaseCommand(Command[Case]):
    """Command to update an existing case - FIXED endpoint URL."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, update_data: UpdateCaseRequest):
        self.http_client = http_client
        self.case_id = case_id
        self.update_data = update_data
    
    def execute(self) -> Case:
        """Execute the update case command."""
        payload = {}
        
        # Only include fields that are set
        if self.update_data.name is not None:
            payload["name"] = self.update_data.name
        if self.update_data.owner_user_id is not None:
            payload["ownerUserId"] = self.update_data.owner_user_id
        if self.update_data.visibility is not None:
            payload["visibility"] = self.update_data.visibility
        if self.update_data.assigned_user_ids is not None:
            payload["assignedUserIds"] = self.update_data.assigned_user_ids
        if self.update_data.status is not None:
            payload["status"] = self.update_data.status
        if self.update_data.notes is not None:
            payload["notes"] = self.update_data.notes
        
        # FIXED: Use PATCH method to match API specification (was PUT)
        response = self.http_client.patch(f"cases/{self.case_id}", json_data=payload)
        
        # Use Pydantic parsing with proper field aliasing
        entity_data = response.get("result", {})
        return Case.model_validate(entity_data)


class CloseCaseCommand(Command[Case]):
    """Command to close a case - FIXED endpoint URL."""
    
    def __init__(self, http_client: HTTPClient, case_id: str):
        self.http_client = http_client
        self.case_id = case_id
    
    def execute(self) -> Case:
        """Execute the close case command."""
        # FIXED: Remove api/public/ prefix
        response = self.http_client.post(f"cases/{self.case_id}/close", json_data={})
        
        # Use Pydantic parsing with proper field aliasing
        entity_data = response.get("result", {})
        return Case.model_validate(entity_data)


class OpenCaseCommand(Command[Case]):
    """Command to open a case - FIXED endpoint URL."""
    
    def __init__(self, http_client: HTTPClient, case_id: str):
        self.http_client = http_client
        self.case_id = case_id
    
    def execute(self) -> Case:
        """Execute the open case command."""
        # FIXED: Remove api/public/ prefix
        response = self.http_client.post(f"cases/{self.case_id}/open", json_data={})
        
        # Use Pydantic parsing with proper field aliasing
        entity_data = response.get("result", {})
        return Case.model_validate(entity_data)


class ArchiveCaseCommand(Command[Case]):
    """Command to archive a case - FIXED endpoint URL."""
    
    def __init__(self, http_client: HTTPClient, case_id: str):
        self.http_client = http_client
        self.case_id = case_id
    
    def execute(self) -> Case:
        """Execute the archive case command."""
        # FIXED: Remove api/public/ prefix
        response = self.http_client.post(f"cases/{self.case_id}/archive", json_data={})
        
        # Use Pydantic parsing with proper field aliasing
        entity_data = response.get("result", {})
        return Case.model_validate(entity_data)


class ChangeCaseOwnerCommand(Command[Case]):
    """Command to change case owner - FIXED to match API specification exactly."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, new_owner_id: str):
        self.http_client = http_client
        self.case_id = case_id
        self.new_owner_id = new_owner_id
    
    def execute(self) -> Case:
        """Execute the change case owner command."""
        # FIXED: Use correct payload field name as per API specification
        payload = {"newOwnerId": self.new_owner_id}
        
        # FIXED: Use correct endpoint URL and HTTP method as per API specification
        # POST /api/public/cases/{id}/change-owner
        response = self.http_client.post(f"cases/{self.case_id}/change-owner", json_data=payload)
        
        # Use Pydantic parsing with proper field aliasing
        entity_data = response.get("result", {})
        return Case.model_validate(entity_data)


class RemoveEndpointsFromCaseCommand(Command[Dict[str, Any]]):
    """Command to remove endpoints from a case - FIXED to match API documentation exactly."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, asset_filter: AssetFilter):
        self.http_client = http_client
        self.case_id = case_id
        self.asset_filter = asset_filter
    
    def execute(self) -> Dict[str, Any]:
        """Execute the remove endpoints from case command with correct structure."""
        # FIXED: Use proper filter structure as per API documentation
        payload = {
            "filter": self.asset_filter.to_filter_dict()
        }
        
        # FIXED: Correct endpoint URL and HTTP method (DELETE)
        return self.http_client.delete(f"cases/{self.case_id}/endpoints", json_data=payload)


class RemoveTaskAssignmentFromCaseCommand(Command[Dict[str, Any]]):
    """Command to remove task assignment from a case - FIXED endpoint URL."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, task_assignment_id: str):
        self.http_client = http_client
        self.case_id = case_id
        self.task_assignment_id = task_assignment_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the remove task assignment from case command."""
        # FIXED: Remove api/public/ prefix
        return self.http_client.post(
            f"cases/{self.case_id}/tasks/{self.task_assignment_id}/remove", 
            json_data={}
        )


class ImportTaskAssignmentsToCaseCommand(Command[Dict[str, Any]]):
    """Command to import task assignments to a case - FIXED endpoint URL."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, task_assignment_ids: List[str]):
        self.http_client = http_client
        self.case_id = case_id
        self.task_assignment_ids = task_assignment_ids
    
    def execute(self) -> Dict[str, Any]:
        """Execute the import task assignments to case command."""
        payload = {"taskAssignmentIds": self.task_assignment_ids}
        
        # FIXED: Remove api/public/ prefix
        return self.http_client.post(f"cases/{self.case_id}/tasks/import", json_data=payload)


class AddNoteToCaseCommand(Command[CaseNote]):
    """Command to add a note to a case - Based on API documentation."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, note_value: str):
        self.http_client = http_client
        self.case_id = case_id
        self.note_value = note_value
    
    def execute(self) -> CaseNote:
        """Execute the add note to case command."""
        payload = {"value": self.note_value}
        
        # POST /api/public/cases/{id}/notes
        response = self.http_client.post(f"cases/{self.case_id}/notes", json_data=payload)
        
        # Use Pydantic parsing with proper field aliasing
        entity_data = response.get("result", {})
        return CaseNote.model_validate(entity_data)


class UpdateNoteToCaseCommand(Command[CaseNote]):
    """Command to update a note in a case - Based on API documentation."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, note_id: str, note_value: str):
        self.http_client = http_client
        self.case_id = case_id
        self.note_id = note_id
        self.note_value = note_value
    
    def execute(self) -> CaseNote:
        """Execute the update note in case command."""
        payload = {"value": self.note_value}
        
        # PATCH /api/public/cases/{caseId}/notes/{noteId}
        response = self.http_client.patch(f"cases/{self.case_id}/notes/{self.note_id}", json_data=payload)
        
        # Use Pydantic parsing with proper field aliasing
        entity_data = response.get("result", {})
        return CaseNote.model_validate(entity_data)


class DeleteNoteToCaseCommand(Command[Dict[str, Any]]):
    """Command to delete a note from a case - Based on API documentation."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, note_id: str):
        self.http_client = http_client
        self.case_id = case_id
        self.note_id = note_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the delete note from case command."""
        # DELETE /api/public/cases/{caseId}/notes/{noteId}
        response = self.http_client.delete(f"cases/{self.case_id}/notes/{self.note_id}")
        return response


class ExportCaseNotesCommand(Command[Dict[str, Any]]):
    """Command to export case notes as a file download - Based on API documentation."""
    
    def __init__(self, http_client: HTTPClient, case_id: str):
        self.http_client = http_client
        self.case_id = case_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the export case notes command."""
        import requests
        
        # GET /api/public/cases/{id}/notes/export
        # This endpoint returns a file download (ZIP/CSV), so we need raw HTTP handling
        headers = {
            'Authorization': f'Bearer {self.http_client.config.api_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.http_client.config.host}/api/public/cases/{self.case_id}/notes/export"
        
        response = requests.get(
            url,
            headers=headers,
            verify=self.http_client.config.verify_ssl,
            timeout=self.http_client.config.timeout
        )
        
        if response.status_code == 200:
            # Handle file downloads (ZIP/CSV export)
            content_type = response.headers.get('content-type', '')
            if 'application/zip' in content_type or 'text/csv' in content_type:
                # Extract filename from content disposition if available
                content_disposition = response.headers.get('content-disposition', '')
                filename = "case_notes_export"
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                
                return {
                    "success": True,
                    "result": {
                        "export_type": "file_download",
                        "content_type": content_type,
                        "file_size": len(response.content),
                        "filename": filename,
                        "file_content": response.content  # Binary content for file download
                    },
                    "statusCode": response.status_code,
                    "errors": []
                }
            else:
                # Fallback to JSON parsing
                return response.json()
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")


class ExportCasesCommand(Command[Dict[str, Any]]):
    """Command to export cases as a file download - Based on API documentation."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[Dict[str, Any]] = None):
        self.http_client = http_client
        self.filter_params = filter_params or {}
    
    def execute(self) -> Dict[str, Any]:
        """Execute the export cases command."""
        import requests
        
        # GET /api/public/cases/export
        # This endpoint returns a file download (CSV), so we need raw HTTP handling
        headers = {
            'Authorization': f'Bearer {self.http_client.config.api_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.http_client.config.host}/api/public/cases/export"
        
        # Prepare query parameters with organization ID protection
        params = {}
        if self.filter_params:
            params.update(self.filter_params)
        
        # Ensure organizationIds is set using our utility functions
        if 'filter[organizationIds]' not in params:
            # Use our organization ID utilities to ensure proper formatting
            org_ids = ensure_organization_ids(None)  # Returns [0] if None
            org_params = format_organization_ids_param(org_ids)
            params.update(org_params)
        
        response = requests.get(
            url,
            headers=headers,
            params=params,
            verify=self.http_client.config.verify_ssl,
            timeout=self.http_client.config.timeout
        )
        
        if response.status_code == 200:
            # Handle file downloads (CSV export)
            content_type = response.headers.get('content-type', '')
            if 'text/csv' in content_type or 'application/octet-stream' in content_type:
                # Extract filename from content disposition if available
                content_disposition = response.headers.get('content-disposition', '')
                filename = "cases_export.csv"
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                
                # Count lines in CSV to get case count
                csv_content = response.text
                case_count = 0
                if csv_content:
                    lines = csv_content.strip().split('\n')
                    case_count = len(lines) - 1 if len(lines) > 0 else 0  # Subtract header
                
                return {
                    "success": True,
                    "result": {
                        "export_type": "csv_download",
                        "content_type": content_type,
                        "file_size": len(response.content),
                        "filename": filename,
                        "csv_content": csv_content,
                        "case_count": case_count,
                        "file_content": response.content  # Binary content for file download
                    },
                    "statusCode": response.status_code,
                    "errors": []
                }
            else:
                # Fallback to JSON parsing
                return response.json()
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")


class ExportCaseEndpointsCommand(Command[Dict[str, Any]]):
    """Command to export case endpoints as a file download - Based on API documentation."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, filter_params: Optional[Dict[str, Any]] = None):
        self.http_client = http_client
        self.case_id = case_id
        self.filter_params = filter_params or {}
    
    def execute(self) -> Dict[str, Any]:
        """Execute the export case endpoints command."""
        import requests
        
        # GET /api/public/cases/{id}/endpoints/export
        # This endpoint returns a file download (CSV), so we need raw HTTP handling
        headers = {
            'Authorization': f'Bearer {self.http_client.config.api_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.http_client.config.host}/api/public/cases/{self.case_id}/endpoints/export"
        
        # Prepare query parameters - ensure organizationIds is included
        params = {}
        if self.filter_params:
            params.update(self.filter_params)
        
        # Ensure organizationIds is set if not provided
        if 'filter[organizationIds]' not in params:
            params['filter[organizationIds]'] = '0'  # Default organization
        
        response = requests.get(
            url,
            headers=headers,
            params=params,
            verify=self.http_client.config.verify_ssl,
            timeout=self.http_client.config.timeout
        )
        
        if response.status_code == 200:
            # Handle file downloads (CSV export)
            content_type = response.headers.get('content-type', '')
            if 'text/csv' in content_type or 'application/octet-stream' in content_type:
                # Extract filename from content disposition if available
                content_disposition = response.headers.get('content-disposition', '')
                filename = "case_endpoints_export.csv"
                if 'filename=' in content_disposition:
                    filename = content_disposition.split('filename=')[1].strip('"')
                
                # Count lines in CSV to get endpoint count
                csv_content = response.text
                endpoint_count = 0
                if csv_content:
                    lines = csv_content.strip().split('\n')
                    endpoint_count = len(lines) - 1 if len(lines) > 0 else 0  # Subtract header
                
                return {
                    "success": True,
                    "result": {
                        "export_type": "csv_download",
                        "content_type": content_type,
                        "file_size": len(response.content),
                        "filename": filename,
                        "csv_content": csv_content,
                        "endpoint_count": endpoint_count,
                        "file_content": response.content  # Binary content for file download
                    },
                    "statusCode": response.status_code,
                    "errors": []
                }
            else:
                # Fallback to JSON parsing
                return response.json()
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}")


class ExportCaseActivitiesCommand(Command[Dict[str, Any]]):
    """Command to export case activities as a file download - Based on API documentation."""
    
    def __init__(self, http_client: HTTPClient, case_id: str, filter_params: Optional[Dict[str, Any]] = None):
        self.http_client = http_client
        self.case_id = case_id
        self.filter_params = filter_params or {}
    
    def execute(self) -> Dict[str, Any]:
        """Execute the export case activities command."""
        import requests
        
        # GET /api/public/cases/{id}/activities/export
        # This endpoint returns a file download (CSV), so we need raw HTTP handling
        headers = {
            'Authorization': f'Bearer {self.http_client.config.api_token}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.http_client.config.host}/api/public/cases/{self.case_id}/activities/export"
        
        # Prepare query parameters - support pagination and filtering
        params = {}
        if self.filter_params:
            params.update(self.filter_params)
        
        # Set default pagination if not provided
        if 'pageNumber' not in params:
            params['pageNumber'] = '1'
        if 'pageSize' not in params:
            params['pageSize'] = '50'  # Reasonable default for export
        if 'sortBy' not in params:
            params['sortBy'] = 'createdAt'
        if 'sortType' not in params:
            params['sortType'] = 'ASC'
        
        response = requests.get(
            url,
            headers=headers,
            params=params,
            verify=self.http_client.config.verify_ssl,
            timeout=self.http_client.config.timeout
        )
        
        if response.status_code == 200:
            # Handle file downloads (ZIP/CSV export)
            content_type = response.headers.get('content-type', '')
            
            if ('text/csv' in content_type or 'application/octet-stream' in content_type or 
                'application/vnd.ms-excel' in content_type or 'application/zip' in content_type):
                # Extract filename from content disposition if available
                content_disposition = response.headers.get('content-disposition', '')
                filename = "case_activities_export"
                if 'filename=' in content_disposition:
                    filename_part = content_disposition.split('filename=')[1].strip('"')
                    if 'filename*=' in content_disposition:
                        # Handle UTF-8 encoded filenames
                        filename_part = content_disposition.split("filename*=UTF-8''")[1] if "filename*=UTF-8''" in content_disposition else filename_part
                    filename = filename_part
                elif 'application/zip' in content_type:
                    filename = "case_activities_export.zip"
                elif 'text/csv' in content_type:
                    filename = "case_activities_export.csv"
                
                # Determine export type and count activities
                if 'application/zip' in content_type:
                    export_type = "zip_download"
                    # For ZIP files, we can't easily count activities without extracting
                    activity_count = "unknown_zip_content"
                else:
                    export_type = "csv_download"
                    # Count lines in CSV to get activity count
                    csv_content = response.text
                    activity_count = 0
                    if csv_content:
                        lines = csv_content.strip().split('\n')
                        activity_count = len(lines) - 1 if len(lines) > 0 else 0  # Subtract header
                
                result_data = {
                    "export_type": export_type,
                    "content_type": content_type,
                    "file_size": len(response.content),
                    "filename": filename,
                    "activity_count": activity_count,
                    "file_content": response.content  # Binary content for file download
                }
                
                # Add content-specific fields
                if export_type == "csv_download":
                    result_data["csv_content"] = response.text
                elif export_type == "zip_download":
                    result_data["zip_content"] = response.content
                
                return {
                    "success": True,
                    "result": result_data,
                    "statusCode": response.status_code,
                    "errors": []
                }
            else:
                # Try to handle as text response first
                try:
                    if response.text.strip():
                        # If it looks like JSON, try to parse it
                        if response.text.strip().startswith('{'):
                            return response.json()
                        else:
                            # Treat as plain text/CSV
                            return {
                                "success": True,
                                "result": {
                                    "export_type": "text_download",
                                    "content_type": content_type,
                                    "file_size": len(response.content),
                                    "filename": "case_activities_export.txt",
                                    "text_content": response.text,
                                    "activity_count": len(response.text.strip().split('\n')) - 1 if response.text.strip() else 0,
                                    "file_content": response.content
                                },
                                "statusCode": response.status_code,
                                "errors": []
                            }
                    else:
                        # Empty response
                        return {
                            "success": True,
                            "result": {
                                "export_type": "empty_response",
                                "content_type": content_type,
                                "file_size": 0,
                                "filename": "empty_export",
                                "activity_count": 0,
                                "file_content": b""
                            },
                            "statusCode": response.status_code,
                            "errors": []
                        }
                except Exception as e:
                    print(f"[DEBUG] Failed to parse response: {e}")
                    return {
                        "success": False,
                        "result": None,
                        "statusCode": response.status_code,
                        "errors": [f"Failed to parse response: {e}"]
                    }
        else:
            raise Exception(f"HTTP {response.status_code}: {response.text}") 