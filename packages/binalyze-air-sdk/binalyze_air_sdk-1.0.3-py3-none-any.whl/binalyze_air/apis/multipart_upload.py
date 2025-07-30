"""Multipart Upload API client for Binalyze AIR SDK."""

from typing import Optional, Dict, Any, Callable
from ..http_client import HTTPClient
from ..models.multipart_upload import (
    UploadInitializeResponse, UploadPartResponse, UploadStatusResponse, 
    UploadFinalizeResponse, MultipartUploadSession
)
from ..queries.multipart_upload import (
    InitializeUploadQuery, UploadPartQuery, CheckUploadStatusQuery, FinalizeUploadQuery
)
from ..commands.multipart_upload import (
    InitializeUploadCommand, UploadPartCommand, CheckUploadStatusCommand, 
    FinalizeUploadCommand, CompleteFileUploadCommand, AbortUploadCommand
)


class MultipartUploadAPI:
    """Multipart Upload API with CQRS pattern - separated queries and commands.
    
    This class provides methods for uploading large files using multipart upload,
    which allows for resumable uploads and better handling of large files.
    """
    
    def __init__(self, http_client: HTTPClient):
        """Initialize Multipart Upload API client.
        
        Args:
            http_client: HTTP client for making API requests
        """
        self.http_client = http_client

    # QUERIES (Read operations)
    def check_upload_status(self, file_id: str) -> UploadStatusResponse:
        """Check if upload is ready to be finalized.
        
        Args:
            file_id: Upload session identifier
            
        Returns:
            UploadStatusResponse with ready status
            
        Raises:
            APIError: If the request fails
        """
        command = CheckUploadStatusCommand(self, file_id)
        return command.execute()

    # COMMANDS (Write operations)
    def initialize_upload(self) -> UploadInitializeResponse:
        """Initialize a new multipart upload session.
        
        Returns:
            UploadInitializeResponse with file ID for the session
            
        Raises:
            APIError: If the request fails
        """
        command = InitializeUploadCommand(self)
        return command.execute()

    def upload_part(self, file_id: str, part_number: int, file_data: bytes, filename: Optional[str] = None) -> UploadPartResponse:
        """Upload a file part in a multipart upload.
        
        Args:
            file_id: Upload session identifier
            part_number: Sequential part number (starting from 1)
            file_data: Binary file data for this part
            filename: Optional filename for the part
            
        Returns:
            UploadPartResponse indicating success/failure
            
        Raises:
            APIError: If the request fails
        """
        command = UploadPartCommand(self, file_id, part_number, file_data, filename)
        return command.execute()

    def finalize_upload(self, file_id: str) -> UploadFinalizeResponse:
        """Finalize a multipart upload session.
        
        Args:
            file_id: Upload session identifier to finalize
            
        Returns:
            UploadFinalizeResponse indicating success/failure
            
        Raises:
            APIError: If the request fails
        """
        command = FinalizeUploadCommand(self, file_id)
        return command.execute()

    def abort_upload(self, file_id: str) -> Dict[str, Any]:
        """Abort a multipart upload session and discard all uploaded parts.

        Args:
            file_id: Upload session identifier to abort

        Returns:
            Dictionary with API response
        """
        command = AbortUploadCommand(self, file_id)
        return command.execute()

    def upload_file(
        self, 
        file_path: str, 
        chunk_size: int = 5 * 1024 * 1024,
        progress_callback: Optional[Callable[[float, int, int], None]] = None
    ) -> Dict[str, Any]:
        """Upload a complete file using multipart upload.
        
        This method handles the entire upload process automatically:
        1. Initialize upload session
        2. Upload all file parts
        3. Check upload status
        4. Finalize upload
        
        Args:
            file_path: Path to the file to upload
            chunk_size: Size of each chunk in bytes (default 5MB)
            progress_callback: Optional callback for progress updates (percentage, current_part, total_parts)
            
        Returns:
            Dictionary with upload results and session information
            
        Raises:
            APIError: If any step of the upload fails
            FileNotFoundError: If the file doesn't exist
        """
        command = CompleteFileUploadCommand(self, file_path, chunk_size, progress_callback)
        return command.execute()

    # Low-level query methods (for internal use by commands)
    def _initialize_upload_query(self, query: InitializeUploadQuery) -> Dict[str, Any]:
        """Execute initialize upload query (internal use).
        
        Args:
            query: InitializeUploadQuery instance
            
        Returns:
            API response dictionary
        """
        body = query.build_body()
        return self.http_client.post('multipart-upload/initialize', json_data=body)

    def _upload_part_query(self, query: UploadPartQuery) -> Dict[str, Any]:
        """Execute upload part query (internal use).
        
        Args:
            query: UploadPartQuery instance
            
        Returns:
            API response dictionary
        """
        form_data = query.build_form_data()
        
        # Prepare files and data for multipart upload
        # Use the filename from the request, or default to 'part.bin'
        filename = getattr(query._request, 'filename', None) or 'part.bin'
        files = {
            'file': (filename, form_data['file'], 'application/octet-stream')
        }
        
        data = {
            'fileId': form_data['fileId'],
            'partNumber': form_data['partNumber']
        }
        
        return self.http_client.upload_multipart(
            'multipart-upload/upload-part',
            files=files,
            data=data,
            method='PUT'
        )

    def _check_upload_status_query(self, query: CheckUploadStatusQuery) -> Dict[str, Any]:
        """Execute check upload status query (internal use).
        
        Args:
            query: CheckUploadStatusQuery instance
            
        Returns:
            API response dictionary
        """
        params = query.build_params()
        return self.http_client.get('multipart-upload/is-ready', params=params)

    def _finalize_upload_query(self, query: FinalizeUploadQuery) -> Dict[str, Any]:
        """Execute finalize upload query (internal use).
        
        Args:
            query: FinalizeUploadQuery instance
            
        Returns:
            API response dictionary
        """
        body = query.build_body()
        return self.http_client.post('multipart-upload/finalize', json_data=body) 