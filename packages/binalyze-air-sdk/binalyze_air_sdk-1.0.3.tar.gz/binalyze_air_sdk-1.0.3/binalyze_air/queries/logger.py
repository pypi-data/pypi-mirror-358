"""Logger query classes for Binalyze AIR SDK."""

from typing import Dict, Any, Optional
from ..models.logger import LogDownloadRequest


class LoggerQuery:
    """Base query class for logger operations."""
    
    def __init__(self):
        """Initialize base logger query."""
        self._params = {}

    def build_params(self) -> Dict[str, Any]:
        """Build query parameters.
        
        Returns:
            Dictionary of query parameters
        """
        return self._params.copy()


class DownloadLogsQuery(LoggerQuery):
    """Query for downloading application logs as ZIP file.
    
    This query downloads system logs which can include:
    - Application logs
    - Error logs
    - System diagnostic information
    - Debug logs (if enabled)
    """
    
    def __init__(self, latest_log_file: bool = False):
        """Initialize download logs query.
        
        Args:
            latest_log_file: Whether to download only the latest log file
        """
        super().__init__()
        self._latest_log_file = latest_log_file

    def build_params(self) -> Dict[str, Any]:
        """Build parameters for download logs request.
        
        Returns:
            Dictionary containing query parameters
        """
        request = LogDownloadRequest(latest_log_file=self._latest_log_file)
        return request.to_dict()

    @property
    def latest_log_file(self) -> bool:
        """Get the latest log file flag.
        
        Returns:
            Whether to download only the latest log file
        """
        return self._latest_log_file 