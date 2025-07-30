"""
Investigation Hub commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, List

from ..base import Command
from ..models.investigation_hub import (
    Investigation, UpdateInvestigationRequest, FlagEvidenceRequest,
    AddNoteRequest, CreateCommentRequest, InvestigationComment,
    MarkActivityAsReadRequest, CreateAdvancedFilterRequest,
    UpdateAdvancedFilterRequest, AdvancedFilter, ExportRequest
)
from ..http_client import HTTPClient


class UpdateInvestigationCommand(Command[Investigation]):
    """Command to update an investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 request: UpdateInvestigationRequest):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.request = request
    
    def execute(self) -> Investigation:
        """Execute the command."""
        response = self.http_client.put(
            f"investigation-hub/investigations/{self.investigation_id}",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return Investigation(**response["result"])


class DeleteInvestigationCommand(Command[Dict[str, Any]]):
    """Command to delete an investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.delete(f"investigation-hub/investigations/{self.investigation_id}")
        return response


class FlagEvidenceCommand(Command[Dict[str, Any]]):
    """Command to flag evidence records."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 request: FlagEvidenceRequest):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/section/flag",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return response


class UnflagEvidenceCommand(Command[Dict[str, Any]]):
    """Command to unflag evidence records."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 records: List[Dict[str, Any]], section: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.records = records
        self.section = section
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        payload = {
            "records": self.records,
            "section": self.section
        }
        response = self.http_client.delete(
            f"investigation-hub/investigations/{self.investigation_id}/section/flag",
            json_data=payload
        )
        return response


class AddNoteToEvidenceCommand(Command[Dict[str, Any]]):
    """Command to add a note to evidence records."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 request: AddNoteRequest):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.put(
            f"investigation-hub/investigations/{self.investigation_id}/notes",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return response


class CreateCommentCommand(Command[InvestigationComment]):
    """Command to create a comment in an investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 request: CreateCommentRequest):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.request = request
    
    def execute(self) -> InvestigationComment:
        """Execute the command."""
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/comments",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return InvestigationComment(**response["result"])


class UpdateCommentCommand(Command[InvestigationComment]):
    """Command to update a comment in an investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 comment_id: str, content: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.comment_id = comment_id
        self.content = content
    
    def execute(self) -> InvestigationComment:
        """Execute the command."""
        payload = {"content": self.content}
        response = self.http_client.put(
            f"investigation-hub/investigations/{self.investigation_id}/comments/{self.comment_id}",
            json_data=payload
        )
        return InvestigationComment(**response["result"])


class DeleteCommentCommand(Command[Dict[str, Any]]):
    """Command to delete a comment from an investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, comment_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.comment_id = comment_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.delete(
            f"investigation-hub/investigations/{self.investigation_id}/comments/{self.comment_id}"
        )
        return response


class MarkActivitiesAsReadCommand(Command[Dict[str, Any]]):
    """Command to mark activities as read."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 request: MarkActivityAsReadRequest):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/activities/mark-as-read",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return response


class CreateAdvancedFilterCommand(Command[AdvancedFilter]):
    """Command to create an advanced filter."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 request: CreateAdvancedFilterRequest):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.request = request
    
    def execute(self) -> AdvancedFilter:
        """Execute the command."""
        response = self.http_client.post(
            f"investigation-hub/advanced-filters",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return AdvancedFilter(**response["result"])


class UpdateAdvancedFilterCommand(Command[AdvancedFilter]):
    """Command to update an advanced filter."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 filter_id: int, request: UpdateAdvancedFilterRequest):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.filter_id = filter_id
        self.request = request
    
    def execute(self) -> AdvancedFilter:
        """Execute the command."""
        response = self.http_client.put(
            f"investigation-hub/advanced-filters/{self.filter_id}",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return AdvancedFilter(**response["result"])


class DeleteAdvancedFilterCommand(Command[Dict[str, Any]]):
    """Command to delete an advanced filter."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, filter_id: int):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.filter_id = filter_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.delete(
            f"investigation-hub/advanced-filters/{self.filter_id}"
        )
        return response


class ExportEvidenceCommand(Command[Dict[str, Any]]):
    """Command to export evidence data."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 request: ExportRequest):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/export-flags",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return response


class GenerateReportCommand(Command[Dict[str, Any]]):
    """Command to generate an investigation report."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 report_type: str = "comprehensive", include_evidence: bool = True):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.report_type = report_type
        self.include_evidence = include_evidence
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        payload = {
            "reportType": self.report_type,
            "includeEvidence": self.include_evidence
        }
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/generate-report",
            json_data=payload
        )
        return response


class RefreshInvestigationCommand(Command[Investigation]):
    """Command to refresh/rebuild an investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> Investigation:
        """Execute the command."""
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/refresh"
        )
        return Investigation(**response["result"])


class ArchiveInvestigationCommand(Command[Dict[str, Any]]):
    """Command to archive an investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> Dict[str, Any]:
        """Execute the command."""
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/archive"
        )
        return response


class RestoreInvestigationCommand(Command[Investigation]):
    """Command to restore an archived investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> Investigation:
        """Execute the command."""
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/restore"
        )
        return Investigation(**response["result"]) 