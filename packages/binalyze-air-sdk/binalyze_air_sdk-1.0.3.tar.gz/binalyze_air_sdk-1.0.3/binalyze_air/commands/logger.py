"""Logger command classes for Binalyze AIR SDK."""

from typing import Optional, Dict, Any
from pathlib import Path
from ..models.logger import LogDownloadResponse
from ..queries.logger import DownloadLogsQuery


class LoggerCommand:
    """Base command class for logger operations."""
    
    def __init__(self, api_client):
        """Initialize logger command.
        
        Args:
            api_client: The Logger API client instance
        """
        self._api_client = api_client


class DownloadLogsCommand(LoggerCommand):
    """Command for downloading application logs as ZIP file.
    
    This command provides comprehensive log download functionality
    with options for latest logs only and automatic file saving.
    """
    
    def __init__(self, api_client, latest_log_file: bool = False):
        """Initialize download logs command.
        
        Args:
            api_client: The Logger API client instance
            latest_log_file: Whether to download only the latest log file
        """
        super().__init__(api_client)
        self._latest_log_file = latest_log_file

    def execute(self) -> LogDownloadResponse:
        """Execute download logs command.
        
        Returns:
            LogDownloadResponse with downloaded log data
            
        Raises:
            APIError: If the request fails
        """
        query = DownloadLogsQuery(self._latest_log_file)
        response_data, headers = self._api_client._download_logs_query(query)
        
        # Create response object from binary data and headers
        return LogDownloadResponse.from_response(response_data, headers)

    def download_and_save(self, save_path: Optional[str] = None) -> Dict[str, Any]:
        """Download logs and save to file.
        
        Args:
            save_path: Optional path where to save the logs.
                      If not provided, saves to current directory.
        
        Returns:
            Dictionary with download result and file information
        """
        try:
            # Download the logs
            log_response = self.execute()
            
            # Determine save path
            if save_path is None:
                save_path = log_response.filename or 'air_logs.zip'
            
            # Ensure directory exists
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file
            success = log_response.save_to_file(save_path)
            
            return {
                'success': success,
                'file_path': save_path,
                'file_size': log_response.size,
                'content_type': log_response.content_type,
                'filename': log_response.filename,
                'latest_only': self._latest_log_file
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': save_path,
                'latest_only': self._latest_log_file
            }

    def get_log_info(self) -> Dict[str, Any]:
        """Get information about available logs without downloading.
        
        Returns:
            Dictionary with log information
        """
        try:
            # Download logs to get metadata
            log_response = self.execute()
            
            return {
                'available': True,
                'size': log_response.size,
                'content_type': log_response.content_type,
                'filename': log_response.filename,
                'latest_only': self._latest_log_file
            }
            
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'latest_only': self._latest_log_file
            }

    @property
    def latest_log_file(self) -> bool:
        """Get the latest log file flag.
        
        Returns:
            Whether downloading only the latest log file
        """
        return self._latest_log_file 