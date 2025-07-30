"""License query classes for Binalyze AIR SDK."""

from typing import Dict, Any, Optional
from ..models.license import LicenseUpdateRequest


class LicenseQuery:
    """Base query class for license operations."""
    
    def __init__(self):
        """Initialize base license query."""
        self._params = {}

    def build_params(self) -> Dict[str, Any]:
        """Build query parameters.
        
        Returns:
            Dictionary of query parameters
        """
        return self._params.copy()


class GetLicenseQuery(LicenseQuery):
    """Query for retrieving license information.
    
    This query retrieves current license details including:
    - License key and activation status
    - Expiration dates and remaining time
    - Device and client usage limits
    - Customer information
    """
    
    def __init__(self):
        """Initialize get license query."""
        super().__init__()

    def build_params(self) -> Dict[str, Any]:
        """Build parameters for get license request.
        
        Returns:
            Empty dictionary as GET license requires no parameters
        """
        return {}


class SetLicenseQuery(LicenseQuery):
    """Query for setting/updating license key.
    
    This query allows updating the license key for the system.
    """
    
    def __init__(self, license_key: str):
        """Initialize set license query.
        
        Args:
            license_key: The new license key to set
        """
        super().__init__()
        self._license_key = license_key

    def build_body(self) -> Dict[str, Any]:
        """Build request body for set license request.
        
        Returns:
            Dictionary containing license key for API request
        """
        request = LicenseUpdateRequest(license_key=self._license_key)
        return request.to_dict()

    def build_params(self) -> Dict[str, Any]:
        """Build parameters for set license request.
        
        Returns:
            Empty dictionary as POST license uses body, not params
        """
        return {}

    @property
    def license_key(self) -> str:
        """Get the license key.
        
        Returns:
            The license key to be set
        """
        return self._license_key 