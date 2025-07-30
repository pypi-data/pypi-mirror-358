"""Multipart Upload command classes for Binalyze AIR SDK."""

from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
import time
from ..models.multipart_upload import (
    UploadInitializeResponse, UploadPartResponse, UploadStatusResponse, 
    UploadFinalizeResponse, MultipartUploadSession, FileChunker
)
from ..queries.multipart_upload import (
    InitializeUploadQuery, UploadPartQuery, CheckUploadStatusQuery, FinalizeUploadQuery
)


class MultipartUploadCommand:
    """Base command class for multipart upload operations."""
    
    def __init__(self, api_client):
        """Initialize multipart upload command.
        
        Args:
            api_client: The Multipart Upload API client instance
        """
        self._api_client = api_client


class InitializeUploadCommand(MultipartUploadCommand):
    """Command for initializing a multipart upload session."""
    
    def execute(self) -> UploadInitializeResponse:
        """Execute upload initialization command.
        
        Returns:
            UploadInitializeResponse with file ID for the session
            
        Raises:
            APIError: If the request fails
        """
        query = InitializeUploadQuery()
        response_data = self._api_client._initialize_upload_query(query)
        
        return UploadInitializeResponse.from_dict(response_data)


class UploadPartCommand(MultipartUploadCommand):
    """Command for uploading a file part in a multipart upload."""
    
    def __init__(self, api_client, file_id: str, part_number: int, file_data: bytes, filename: Optional[str] = None):
        """Initialize upload part command.
        
        Args:
            api_client: The Multipart Upload API client instance
            file_id: Upload session identifier
            part_number: Sequential part number (starting from 1)
            file_data: Binary file data for this part
            filename: Optional filename for the part
        """
        super().__init__(api_client)
        self._file_id = file_id
        self._part_number = part_number
        self._file_data = file_data
        self._filename = filename

    def execute(self) -> UploadPartResponse:
        """Execute upload part command.
        
        Returns:
            UploadPartResponse indicating success/failure
            
        Raises:
            APIError: If the request fails
        """
        query = UploadPartQuery(self._file_id, self._part_number, self._file_data, self._filename)
        response_data = self._api_client._upload_part_query(query)
        
        return UploadPartResponse.from_dict(response_data, self._part_number)


class CheckUploadStatusCommand(MultipartUploadCommand):
    """Command for checking upload status."""
    
    def __init__(self, api_client, file_id: str):
        """Initialize upload status check command.
        
        Args:
            api_client: The Multipart Upload API client instance
            file_id: Upload session identifier to check
        """
        super().__init__(api_client)
        self._file_id = file_id

    def execute(self) -> UploadStatusResponse:
        """Execute upload status check command.
        
        Returns:
            UploadStatusResponse with ready status
            
        Raises:
            APIError: If the request fails
        """
        query = CheckUploadStatusQuery(self._file_id)
        response_data = self._api_client._check_upload_status_query(query)
        
        return UploadStatusResponse.from_dict(response_data, self._file_id)


class FinalizeUploadCommand(MultipartUploadCommand):
    """Command for finalizing a multipart upload."""
    
    def __init__(self, api_client, file_id: str):
        """Initialize upload finalization command.
        
        Args:
            api_client: The Multipart Upload API client instance
            file_id: Upload session identifier to finalize
        """
        super().__init__(api_client)
        self._file_id = file_id

    def execute(self) -> UploadFinalizeResponse:
        """Execute upload finalization command.
        
        Returns:
            UploadFinalizeResponse indicating success/failure
            
        Raises:
            APIError: If the request fails
        """
        query = FinalizeUploadQuery(self._file_id)
        response_data = self._api_client._finalize_upload_query(query)
        
        return UploadFinalizeResponse.from_dict(response_data, self._file_id)


class CompleteFileUploadCommand(MultipartUploadCommand):
    """Command for uploading a complete file using multipart upload.
    
    This command orchestrates the entire upload process:
    1. Initialize upload session
    2. Upload all file parts
    3. Check upload status
    4. Finalize upload
    """
    
    def __init__(
        self, 
        api_client, 
        file_path: str, 
        chunk_size: int = 5 * 1024 * 1024,
        progress_callback: Optional[Callable[[float, int, int], None]] = None
    ):
        """Initialize complete file upload command.
        
        Args:
            api_client: The Multipart Upload API client instance
            file_path: Path to the file to upload
            chunk_size: Size of each chunk in bytes (default 5MB)
            progress_callback: Optional callback for progress updates (percentage, current_part, total_parts)
        """
        super().__init__(api_client)
        self._file_path = file_path
        self._chunk_size = chunk_size
        self._progress_callback = progress_callback
        self._session: Optional[MultipartUploadSession] = None

    def execute(self) -> Dict[str, Any]:
        """Execute complete file upload.
        
        Returns:
            Dictionary with upload results and session information
            
        Raises:
            APIError: If any step of the upload fails
            FileNotFoundError: If the file doesn't exist
        """
        try:
            # Validate file exists
            if not Path(self._file_path).exists():
                raise FileNotFoundError(f"File not found: {self._file_path}")

            # Step 1: Initialize upload session
            init_response = self._initialize_session()
            if not init_response.success:
                return {
                    'success': False,
                    'error': 'Failed to initialize upload session',
                    'file_path': self._file_path
                }

            # Step 2: Upload all parts
            upload_results = self._upload_all_parts()
            if not upload_results['success']:
                return {
                    'success': False,
                    'error': upload_results['error'],
                    'file_path': self._file_path,
                    'file_id': self._session.file_id if self._session else None,
                    'uploaded_parts': len(self._session.uploaded_parts) if self._session else 0,
                    'total_parts': self._session.total_parts if self._session else 0
                }

            # Step 3: Check upload status
            status_response = self._check_status()
            if not status_response.success or not status_response.ready:
                return {
                    'success': False,
                    'error': 'Upload not ready for finalization',
                    'file_path': self._file_path,
                    'file_id': self._session.file_id if self._session else None,
                    'ready': status_response.ready
                }

            # Step 4: Finalize upload
            finalize_response = self._finalize_upload()
            if not finalize_response.success:
                return {
                    'success': False,
                    'error': finalize_response.error_message or 'Failed to finalize upload',
                    'file_path': self._file_path,
                    'file_id': self._session.file_id if self._session else None
                }

            # Success!
            return {
                'success': True,
                'file_path': self._file_path,
                'file_id': self._session.file_id if self._session else None,
                'total_parts': self._session.total_parts if self._session else 0,
                'total_size': self._session.total_size if self._session else 0,
                'chunk_size': self._session.chunk_size if self._session else 0,
                'upload_complete': True
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': self._file_path,
                'file_id': self._session.file_id if self._session else None
            }

    def _initialize_session(self) -> UploadInitializeResponse:
        """Initialize the upload session."""
        # Create session from file
        self._session = FileChunker.create_session_from_file(self._file_path, self._chunk_size)
        
        # Initialize upload
        init_command = InitializeUploadCommand(self._api_client)
        init_response = init_command.execute()
        
        # Update session with file ID
        if init_response.success:
            self._session.file_id = init_response.file_id
        
        return init_response

    def _upload_all_parts(self) -> Dict[str, Any]:
        """Upload all file parts."""
        if not self._session:
            return {'success': False, 'error': 'Session not initialized'}

        failed_parts = []
        
        for part_number in range(1, self._session.total_parts + 1):
            try:
                # Read chunk data
                chunk_data = FileChunker.read_chunk(
                    self._file_path, 
                    part_number, 
                    self._session.chunk_size
                )
                
                # Upload part
                upload_command = UploadPartCommand(
                    self._api_client,
                    self._session.file_id,
                    part_number,
                    chunk_data,
                    Path(self._file_path).name
                )
                
                part_response = upload_command.execute()
                
                if part_response.success:
                    self._session.add_uploaded_part(part_number)
                    
                    # Call progress callback if provided
                    if self._progress_callback:
                        progress = self._session.get_progress_percentage()
                        self._progress_callback(progress, part_number, self._session.total_parts)
                else:
                    failed_parts.append({
                        'part_number': part_number,
                        'error': part_response.error_message
                    })
                    
            except Exception as e:
                failed_parts.append({
                    'part_number': part_number,
                    'error': str(e)
                })

        if failed_parts:
            return {
                'success': False,
                'error': f"Failed to upload {len(failed_parts)} parts",
                'failed_parts': failed_parts
            }

        return {'success': True}

    def _check_status(self) -> UploadStatusResponse:
        """Check upload status."""
        if not self._session:
            raise ValueError("Session not initialized")
        status_command = CheckUploadStatusCommand(self._api_client, self._session.file_id)
        return status_command.execute()

    def _finalize_upload(self) -> UploadFinalizeResponse:
        """Finalize the upload."""
        if not self._session:
            raise ValueError("Session not initialized")
        finalize_command = FinalizeUploadCommand(self._api_client, self._session.file_id)
        return finalize_command.execute()

    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """Get current session information.
        
        Returns:
            Dictionary with session details or None if not initialized
        """
        if not self._session:
            return None

        return {
            'file_id': self._session.file_id,
            'file_path': self._session.file_path,
            'total_parts': self._session.total_parts,
            'uploaded_parts': len(self._session.uploaded_parts),
            'total_size': self._session.total_size,
            'chunk_size': self._session.chunk_size,
            'progress_percentage': self._session.get_progress_percentage(),
            'is_complete': self._session.is_complete(),
            'missing_parts': self._session.get_missing_parts()
        }


# ---------------------------------------------------------------------------
# Abort Upload Command
# ---------------------------------------------------------------------------


class AbortUploadCommand(MultipartUploadCommand):
    """Command for aborting a multipart upload session (discard all parts)."""

    def __init__(self, api_client, file_id: str):
        super().__init__(api_client)
        self._file_id = file_id

    def execute(self) -> Dict[str, Any]:  # returns plain dict. specific model not needed
        """Abort upload session by POSTing fileId to multipart-upload/abort."""
        payload = {"fileId": self._file_id}
        return self._api_client.http_client.post("multipart-upload/abort", json_data=payload) 