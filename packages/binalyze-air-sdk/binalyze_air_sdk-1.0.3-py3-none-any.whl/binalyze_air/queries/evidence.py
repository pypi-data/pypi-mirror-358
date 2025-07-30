"""
Evidence-related queries for the Binalyze AIR SDK.
"""

from ..base import Query
from ..models.evidence import EvidencePPC, EvidenceReportFileInfo, EvidenceReport
from ..http_client import HTTPClient


class GetEvidencePPCQuery(Query[EvidencePPC]):
    """Query to get case evidence PPC."""
    
    def __init__(self, http_client: HTTPClient, endpoint_id: str, task_id: str):
        self.http_client = http_client
        self.endpoint_id = endpoint_id
        self.task_id = task_id
    
    def execute(self) -> EvidencePPC:
        """Execute the get evidence PPC query."""
        try:
            # Use binary HTTP client for file downloads
            response = self.http_client.get_binary(f"evidence/case/ppc/{self.endpoint_id}/{self.task_id}")
            
            # Extract content information
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            filename = response.headers.get('Content-Disposition')
            if filename and 'filename=' in filename:
                filename = filename.split('filename=')[1].strip('"')
            else:
                filename = f"ppc_{self.endpoint_id}_{self.task_id}.zip"
            
            return EvidencePPC(
                endpoint_id=self.endpoint_id,
                task_id=self.task_id,
                content=response.content,
                content_type=content_type,
                content_length=len(response.content) if response.content else 0,
                filename=filename
            )
            
        except Exception as e:
            # Re-raise with more specific error information
            error_str = str(e)
            if "404" in error_str or "not found" in error_str.lower():
                raise Exception(f"Evidence PPC not found (HTTP 404): No task(s) found by provided id(s)")
            else:
                raise Exception(f"Evidence PPC not found for endpoint {self.endpoint_id}, task {self.task_id}: {error_str}")


class GetEvidenceReportFileInfoQuery(Query[EvidenceReportFileInfo]):
    """Query to get case evidence report file info."""
    
    def __init__(self, http_client: HTTPClient, endpoint_id: str, task_id: str):
        self.http_client = http_client
        self.endpoint_id = endpoint_id
        self.task_id = task_id
    
    def execute(self) -> EvidenceReportFileInfo:
        """Execute the get evidence report file info query."""
        try:
            response = self.http_client.get(f"evidence/case/report-file-info/{self.endpoint_id}/{self.task_id}")
            
            if response.get("success"):
                file_info_data = response.get("result", {})
                
                # Map API fields to SDK model fields
                return EvidenceReportFileInfo(
                    endpoint_id=self.endpoint_id,
                    task_id=self.task_id,
                    file_name=file_info_data.get("name"),
                    file_size=file_info_data.get("size"),
                    created_at=file_info_data.get("timestampResponse"),
                    status="available" if not file_info_data.get("purged", False) else "purged",
                    # Additional fields from API
                    file_path=file_info_data.get("path"),
                    encoding=file_info_data.get("encoding"),
                    mime_type=file_info_data.get("mimeType"),
                    file_hash=file_info_data.get("hash"),
                    organization_id=file_info_data.get("organizationId"),
                    is_purged=file_info_data.get("purged", False)
                )
            
            # Handle error response with detailed information from API
            errors = response.get("errors", [])
            status_code = response.get("statusCode", "Unknown")
            error_message = "; ".join(errors) if errors else "Unknown error"
            
            raise Exception(f"Evidence report file info not found (HTTP {status_code}): {error_message}")
            
        except Exception as e:
            # Check if this is already our formatted exception
            if "Evidence report file info not found" in str(e):
                raise e
            
            # Handle HTTP client exceptions and format them consistently
            error_str = str(e)
            if "404" in error_str or "not found" in error_str.lower():
                raise Exception(f"Evidence report file info not found (HTTP 404): No task(s) found by provided id(s)")
            else:
                raise Exception(f"Evidence report file info not found for endpoint {self.endpoint_id}, task {self.task_id}: {error_str}")


class GetEvidenceReportQuery(Query[EvidenceReport]):
    """Query to get case evidence report."""
    
    def __init__(self, http_client: HTTPClient, endpoint_id: str, task_id: str):
        self.http_client = http_client
        self.endpoint_id = endpoint_id
        self.task_id = task_id
    
    def execute(self) -> EvidenceReport:
        """Execute the get evidence report query."""
        try:
            # Use binary HTTP client for file downloads
            response = self.http_client.get_binary(f"evidence/case/report/{self.endpoint_id}/{self.task_id}")
            
            # Extract content information
            content_type = response.headers.get('Content-Type', 'application/octet-stream')
            filename = response.headers.get('Content-Disposition')
            if filename and 'filename=' in filename:
                filename = filename.split('filename=')[1].strip('"')
            else:
                filename = f"report_{self.endpoint_id}_{self.task_id}"
            
            return EvidenceReport(
                endpoint_id=self.endpoint_id,
                task_id=self.task_id,
                content=response.content,
                content_type=content_type,
                content_length=len(response.content) if response.content else 0,
                filename=filename
            )
            
        except Exception as e:
            # Re-raise with more specific error information
            error_str = str(e)
            if "404" in error_str or "not found" in error_str.lower():
                raise Exception(f"Evidence report not found (HTTP 404): No task(s) found by provided id(s)")
            else:
                raise Exception(f"Evidence report not found for endpoint {self.endpoint_id}, task {self.task_id}: {error_str}") 