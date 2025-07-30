"""License API client for Binalyze AIR SDK."""

from ..http_client import HTTPClient
from ..models.license import License
from ..queries.license import GetLicenseQuery, SetLicenseQuery
from ..commands.license import GetLicenseCommand, SetLicenseCommand


class LicenseAPI:
    """License API with CQRS pattern - separated queries and commands.
    
    This class provides methods for managing license information
    including retrieving current license details and updating license keys.
    """
    
    def __init__(self, http_client: HTTPClient):
        """Initialize License API client.
        
        Args:
            http_client: HTTP client for making API requests
        """
        self.http_client = http_client

    # QUERIES (Read operations)
    def get_license(self) -> License:
        """Get current license information.
        
        Returns:
            License object with current license information
            
        Raises:
            APIError: If the request fails
        """
        command = GetLicenseCommand(self)
        return command.execute()

    def get_license_status(self) -> dict:
        """Get comprehensive license status information.
        
        Returns:
            Dictionary with license status, usage, and warnings
        """
        command = GetLicenseCommand(self)
        return command.get_license_status()

    # COMMANDS (Write operations)
    def set_license(self, license_key: str) -> bool:
        """Set/update license key.
        
        Args:
            license_key: The new license key to set
            
        Returns:
            True if license was set successfully
            
        Raises:
            APIError: If the request fails
            ValueError: If license key is invalid
        """
        command = SetLicenseCommand(self, license_key)
        return command.execute()

    def set_and_verify_license(self, license_key: str) -> dict:
        """Set license key and verify the operation.
        
        Args:
            license_key: The new license key to set
        
        Returns:
            Dictionary with operation result and new license status
        """
        command = SetLicenseCommand(self, license_key)
        return command.set_and_verify()

    # Low-level query methods (for internal use by commands)
    def _get_license_query(self, query: GetLicenseQuery) -> dict:
        """Execute get license query (internal use).
        
        Args:
            query: GetLicenseQuery instance
            
        Returns:
            Dictionary containing license information
        """
        params = query.build_params()
        return self.http_client.get('/license', params=params)

    def _set_license_query(self, query: SetLicenseQuery) -> dict:
        """Execute set license query (internal use).
        
        Args:
            query: SetLicenseQuery instance
            
        Returns:
            Dictionary containing operation result
        """
        body = query.build_body()
        params = query.build_params()
        
        return self.http_client.post(
            '/license',
            data=body,
            params=params
        ) 