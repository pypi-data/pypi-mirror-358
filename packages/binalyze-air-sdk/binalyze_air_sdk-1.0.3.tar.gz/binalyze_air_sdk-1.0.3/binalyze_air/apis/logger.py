"""Logger API client for Binalyze AIR SDK."""

from typing import Optional, Dict, Any, Tuple
from ..http_client import HTTPClient
from ..models.logger import LogDownloadResponse
from ..queries.logger import DownloadLogsQuery
from ..commands.logger import DownloadLogsCommand


class LoggerAPI:
    """Logger API with CQRS pattern - separated queries and commands.
    
    This class provides methods for downloading application logs
    and managing log-related operations.
    """
    
    def __init__(self, http_client: HTTPClient):
        """Initialize Logger API client.
        
        Args:
            http_client: HTTP client for making API requests
        """
        self.http_client = http_client

    # QUERIES (Read operations)
    def download_logs(self, latest_only: bool = False) -> LogDownloadResponse:
        """Download application logs as ZIP file.
        
        Args:
            latest_only: Whether to download only the latest log file
        
        Returns:
            LogDownloadResponse with downloaded log data
            
        Raises:
            APIError: If the request fails
        """
        command = DownloadLogsCommand(self, latest_only)
        return command.execute()

    def download_and_save_logs(self, save_path: Optional[str] = None, 
                              latest_only: bool = False) -> Dict[str, Any]:
        """Download logs and save to file.
        
        Args:
            save_path: Optional path where to save the logs
            latest_only: Whether to download only the latest log file
        
        Returns:
            Dictionary with download result and file information
        """
        command = DownloadLogsCommand(self, latest_only)
        return command.download_and_save(save_path)

    def get_log_info(self, latest_only: bool = False) -> Dict[str, Any]:
        """Get information about available logs without downloading.
        
        Args:
            latest_only: Whether to check only the latest log file
        
        Returns:
            Dictionary with log information
        """
        command = DownloadLogsCommand(self, latest_only)
        return command.get_log_info()

    # Low-level query methods (for internal use by commands)
    def _download_logs_query(self, query: DownloadLogsQuery) -> Tuple[bytes, Dict[str, str]]:
        """Execute download logs query (internal use).
        
        Args:
            query: DownloadLogsQuery instance
            
        Returns:
            Tuple of (binary_data, headers)
        """
        params = query.build_params()
        
        # Make the API call and get binary response
        response = self.http_client.get_binary('/logs', params=params)
        
        # Extract binary content and headers
        return response.content, dict(response.headers) 