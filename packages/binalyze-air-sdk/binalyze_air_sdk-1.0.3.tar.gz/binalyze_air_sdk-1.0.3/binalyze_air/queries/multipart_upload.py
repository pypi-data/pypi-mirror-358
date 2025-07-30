"""Multipart Upload query classes for Binalyze AIR SDK."""

from typing import Dict, Any, Optional
from ..models.multipart_upload import (
    UploadInitializeRequest, UploadPartRequest, UploadStatusRequest, UploadFinalizeRequest
)


class MultipartUploadQuery:
    """Base query class for multipart upload operations."""
    
    def __init__(self):
        """Initialize base multipart upload query."""
        self._params = {}

    def build_params(self) -> Dict[str, Any]:
        """Build query parameters.
        
        Returns:
            Dictionary of query parameters
        """
        return self._params.copy()


class InitializeUploadQuery(MultipartUploadQuery):
    """Query for initializing a multipart upload session.
    
    This query starts a new upload session and returns a unique file ID
    that will be used for all subsequent operations in this upload.
    """
    
    def __init__(self):
        """Initialize upload initialization query."""
        super().__init__()
        self._request = UploadInitializeRequest()

    def build_body(self) -> Dict[str, Any]:
        """Build request body for upload initialization.
        
        Returns:
            Dictionary containing request body (typically empty)
        """
        return self._request.to_dict()


class UploadPartQuery(MultipartUploadQuery):
    """Query for uploading a file part in a multipart upload.
    
    This query uploads a specific part of a file using the file ID
    obtained from the initialization step.
    """
    
    def __init__(self, file_id: str, part_number: int, file_data: bytes, filename: Optional[str] = None):
        """Initialize upload part query.
        
        Args:
            file_id: Upload session identifier
            part_number: Sequential part number (starting from 1)
            file_data: Binary file data for this part
            filename: Optional filename for the part
        """
        super().__init__()
        self._request = UploadPartRequest(
            file_id=file_id,
            part_number=part_number,
            file_data=file_data,
            filename=filename
        )

    def build_form_data(self) -> Dict[str, Any]:
        """Build form data for multipart file upload.
        
        Returns:
            Dictionary with form data fields
        """
        return self._request.to_form_data()

    @property
    def file_id(self) -> str:
        """Get the file ID for this upload.
        
        Returns:
            Upload session identifier
        """
        return self._request.file_id

    @property
    def part_number(self) -> int:
        """Get the part number for this upload.
        
        Returns:
            Part number being uploaded
        """
        return self._request.part_number

    @property
    def part_size(self) -> int:
        """Get the size of this part.
        
        Returns:
            Size of the part in bytes
        """
        return self._request.get_part_size()

    @property
    def part_hash(self) -> str:
        """Get MD5 hash of this part.
        
        Returns:
            MD5 hash of the part data
        """
        return self._request.get_part_hash()


class CheckUploadStatusQuery(MultipartUploadQuery):
    """Query for checking the status of a multipart upload.
    
    This query checks if all parts have been uploaded and the upload
    is ready to be finalized.
    """
    
    def __init__(self, file_id: str):
        """Initialize upload status check query.
        
        Args:
            file_id: Upload session identifier to check
        """
        super().__init__()
        self._request = UploadStatusRequest(file_id=file_id)

    def build_params(self) -> Dict[str, Any]:
        """Build query parameters for status check.
        
        Returns:
            Dictionary containing query parameters
        """
        return self._request.to_dict()

    @property
    def file_id(self) -> str:
        """Get the file ID being checked.
        
        Returns:
            Upload session identifier
        """
        return self._request.file_id


class FinalizeUploadQuery(MultipartUploadQuery):
    """Query for finalizing a multipart upload.
    
    This query completes the upload process by combining all uploaded
    parts into the final file.
    """
    
    def __init__(self, file_id: str):
        """Initialize upload finalization query.
        
        Args:
            file_id: Upload session identifier to finalize
        """
        super().__init__()
        self._request = UploadFinalizeRequest(file_id=file_id)

    def build_body(self) -> Dict[str, Any]:
        """Build request body for upload finalization.
        
        Returns:
            Dictionary containing request body
        """
        return self._request.to_dict()

    @property
    def file_id(self) -> str:
        """Get the file ID being finalized.
        
        Returns:
            Upload session identifier
        """
        return self._request.file_id 