"""Logger models for Binalyze AIR SDK."""

from typing import Optional
from dataclasses import dataclass


@dataclass
class LogDownloadRequest:
    """Request model for downloading logs.
    
    Attributes:
        latest_log_file: Whether to download only the latest log file
    """
    latest_log_file: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for API request.
        
        Returns:
            Dictionary representation for API
        """
        return {
            'latestLogFile': self.latest_log_file
        }


@dataclass
class LogDownloadResponse:
    """Response model for log download operation.
    
    Attributes:
        content: The downloaded log content (binary data)
        filename: Suggested filename for the downloaded logs
        content_type: MIME type of the downloaded content
        size: Size of the downloaded content in bytes
    """
    content: bytes
    filename: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None

    @classmethod
    def from_response(cls, response_data: bytes, headers: Optional[dict] = None) -> 'LogDownloadResponse':
        """Create LogDownloadResponse from HTTP response.
        
        Args:
            response_data: Binary response data
            headers: HTTP response headers
            
        Returns:
            LogDownloadResponse instance
        """
        if headers is None:
            headers = {}
        
        # Extract filename from Content-Disposition header if available
        filename = None
        content_disposition = headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"')
        
        return cls(
            content=response_data,
            filename=filename or 'logs.zip',
            content_type=headers.get('Content-Type', 'application/zip'),
            size=len(response_data) if response_data else 0
        )

    def save_to_file(self, filepath: str) -> bool:
        """Save downloaded logs to a file.
        
        Args:
            filepath: Path where to save the log file
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            with open(filepath, 'wb') as f:
                f.write(self.content)
            return True
        except Exception:
            return False 