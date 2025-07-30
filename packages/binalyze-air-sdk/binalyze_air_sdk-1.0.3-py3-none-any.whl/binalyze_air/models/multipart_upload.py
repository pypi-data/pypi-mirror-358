"""Multipart Upload models for Binalyze AIR SDK."""

from typing import Optional, List, Dict, Any, BinaryIO
from dataclasses import dataclass
from pathlib import Path
import hashlib
import os


@dataclass
class UploadInitializeRequest:
    """Request model for initializing a multipart upload.
    
    This model represents the request to start a new multipart upload session.
    No parameters are typically required for initialization.
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request.
        
        Returns:
            Dictionary representation for API (typically empty)
        """
        return {}


@dataclass
class UploadInitializeResponse:
    """Response model for upload initialization.
    
    Attributes:
        file_id: Unique identifier for the upload session
        success: Whether the initialization was successful
    """
    file_id: str
    success: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UploadInitializeResponse':
        """Create UploadInitializeResponse from API response.
        
        Args:
            data: API response dictionary
            
        Returns:
            UploadInitializeResponse instance
        """
        result = data.get('result', {})
        return cls(
            file_id=result.get('fileId', ''),
            success=data.get('success', False)
        )


@dataclass
class UploadPartRequest:
    """Request model for uploading a file part.
    
    Attributes:
        file_id: Upload session identifier
        part_number: Sequential part number (starting from 1)
        file_data: Binary file data for this part
        filename: Optional filename for the part
    """
    file_id: str
    part_number: int
    file_data: bytes
    filename: Optional[str] = None

    def to_form_data(self) -> Dict[str, Any]:
        """Convert to form data for multipart file upload.
        
        Returns:
            Dictionary with form data fields
        """
        return {
            'fileId': self.file_id,
            'partNumber': str(self.part_number),
            'file': self.file_data
        }

    def get_part_size(self) -> int:
        """Get the size of this part in bytes.
        
        Returns:
            Size of the file data in bytes
        """
        return len(self.file_data)

    def get_part_hash(self) -> str:
        """Generate MD5 hash of the part data for integrity checking.
        
        Returns:
            MD5 hash of the part data
        """
        return hashlib.md5(self.file_data).hexdigest()


@dataclass
class UploadPartResponse:
    """Response model for file part upload.
    
    Attributes:
        success: Whether the part upload was successful
        part_number: The part number that was uploaded
        error_message: Error message if upload failed
    """
    success: bool
    part_number: int
    error_message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], part_number: int) -> 'UploadPartResponse':
        """Create UploadPartResponse from API response.
        
        Args:
            data: API response dictionary
            part_number: The part number that was uploaded
            
        Returns:
            UploadPartResponse instance
        """
        success = data.get('success', False)
        error_message = None
        if not success and data.get('errors'):
            error_message = '; '.join(data['errors'])
        
        return cls(
            success=success,
            part_number=part_number,
            error_message=error_message
        )


@dataclass
class UploadStatusRequest:
    """Request model for checking upload status.
    
    Attributes:
        file_id: Upload session identifier to check
    """
    file_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request.
        
        Returns:
            Dictionary with query parameters
        """
        return {'fileId': self.file_id}


@dataclass
class UploadStatusResponse:
    """Response model for upload status check.
    
    Attributes:
        ready: Whether the upload is ready to be finalized
        file_id: Upload session identifier
        success: Whether the status check was successful
    """
    ready: bool
    file_id: str
    success: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any], file_id: str) -> 'UploadStatusResponse':
        """Create UploadStatusResponse from API response.
        
        Args:
            data: API response dictionary
            file_id: Upload session identifier
            
        Returns:
            UploadStatusResponse instance
        """
        result = data.get('result', {})
        return cls(
            ready=result.get('ready', False),
            file_id=file_id,
            success=data.get('success', False)
        )


@dataclass
class UploadFinalizeRequest:
    """Request model for finalizing a multipart upload.
    
    Attributes:
        file_id: Upload session identifier to finalize
    """
    file_id: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request.
        
        Returns:
            Dictionary representation for API
        """
        return {'fileId': self.file_id}


@dataclass
class UploadFinalizeResponse:
    """Response model for upload finalization.
    
    Attributes:
        success: Whether the finalization was successful
        file_id: Upload session identifier
        error_message: Error message if finalization failed
    """
    success: bool
    file_id: str
    error_message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any], file_id: str) -> 'UploadFinalizeResponse':
        """Create UploadFinalizeResponse from API response.
        
        Args:
            data: API response dictionary
            file_id: Upload session identifier
            
        Returns:
            UploadFinalizeResponse instance
        """
        success = data.get('success', False)
        error_message = None
        if not success and data.get('errors'):
            error_message = '; '.join(data['errors'])
        
        return cls(
            success=success,
            file_id=file_id,
            error_message=error_message
        )


@dataclass
class MultipartUploadSession:
    """Complete multipart upload session information.
    
    Attributes:
        file_id: Upload session identifier
        total_parts: Total number of parts to upload
        uploaded_parts: List of successfully uploaded part numbers
        file_path: Path to the file being uploaded
        chunk_size: Size of each chunk in bytes
        total_size: Total size of the file in bytes
    """
    file_id: str
    total_parts: int
    uploaded_parts: List[int]
    file_path: Optional[str] = None
    chunk_size: int = 5 * 1024 * 1024  # 5MB default
    total_size: int = 0

    def is_complete(self) -> bool:
        """Check if all parts have been uploaded.
        
        Returns:
            True if all parts are uploaded, False otherwise
        """
        return len(self.uploaded_parts) == self.total_parts

    def get_progress_percentage(self) -> float:
        """Get upload progress as percentage.
        
        Returns:
            Progress percentage (0.0 to 100.0)
        """
        if self.total_parts == 0:
            return 0.0
        return (len(self.uploaded_parts) / self.total_parts) * 100.0

    def get_missing_parts(self) -> List[int]:
        """Get list of part numbers that still need to be uploaded.
        
        Returns:
            List of missing part numbers
        """
        all_parts = set(range(1, self.total_parts + 1))
        uploaded_set = set(self.uploaded_parts)
        return sorted(list(all_parts - uploaded_set))

    def add_uploaded_part(self, part_number: int) -> None:
        """Mark a part as successfully uploaded.
        
        Args:
            part_number: Part number that was uploaded
        """
        if part_number not in self.uploaded_parts:
            self.uploaded_parts.append(part_number)
            self.uploaded_parts.sort()


class FileChunker:
    """Utility class for splitting files into chunks for multipart upload."""
    
    @staticmethod
    def calculate_parts(file_size: int, chunk_size: int = 5 * 1024 * 1024) -> int:
        """Calculate number of parts needed for a file.
        
        Args:
            file_size: Size of the file in bytes
            chunk_size: Size of each chunk in bytes
            
        Returns:
            Number of parts needed
        """
        return (file_size + chunk_size - 1) // chunk_size

    @staticmethod
    def read_chunk(file_path: str, part_number: int, chunk_size: int = 5 * 1024 * 1024) -> bytes:
        """Read a specific chunk from a file.
        
        Args:
            file_path: Path to the file
            part_number: Part number to read (1-based)
            chunk_size: Size of each chunk in bytes
            
        Returns:
            Binary data for the specified chunk
        """
        offset = (part_number - 1) * chunk_size
        
        with open(file_path, 'rb') as f:
            f.seek(offset)
            return f.read(chunk_size)

    @staticmethod
    def create_session_from_file(file_path: str, chunk_size: int = 5 * 1024 * 1024) -> MultipartUploadSession:
        """Create an upload session from a file path.
        
        Args:
            file_path: Path to the file to upload
            chunk_size: Size of each chunk in bytes
            
        Returns:
            MultipartUploadSession configured for the file
        """
        file_size = os.path.getsize(file_path)
        total_parts = FileChunker.calculate_parts(file_size, chunk_size)
        
        return MultipartUploadSession(
            file_id='',  # Will be set after initialization
            total_parts=total_parts,
            uploaded_parts=[],
            file_path=file_path,
            chunk_size=chunk_size,
            total_size=file_size
        ) 