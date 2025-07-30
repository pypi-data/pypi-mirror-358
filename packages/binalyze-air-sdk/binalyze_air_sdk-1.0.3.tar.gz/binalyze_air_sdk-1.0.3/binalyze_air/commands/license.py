"""License command classes for Binalyze AIR SDK."""

from typing import Optional, Dict, Any
from ..models.license import License
from ..queries.license import GetLicenseQuery, SetLicenseQuery


class LicenseCommand:
    """Base command class for license operations."""
    
    def __init__(self, api_client):
        """Initialize license command.
        
        Args:
            api_client: The License API client instance
        """
        self._api_client = api_client


class GetLicenseCommand(LicenseCommand):
    """Command for retrieving current license information.
    
    This command provides comprehensive license details including
    expiration status, usage statistics, and validation.
    """
    
    def execute(self) -> License:
        """Execute get license command.
        
        Returns:
            License object with current license information
            
        Raises:
            APIError: If the request fails
        """
        query = GetLicenseQuery()
        response = self._api_client._get_license_query(query)
        
        if response.get('success') and response.get('result'):
            return License.from_dict(response['result'])
        else:
            raise ValueError(
                f"Failed to get license: {response.get('errors', [])}"
            )

    def get_license_status(self) -> Dict[str, Any]:
        """Get comprehensive license status information.
        
        Returns:
            Dictionary with license status, usage, and warnings
        """
        license_info = self.execute()
        usage_stats = license_info.get_usage_percentage()
        
        status = {
            'license_key': license_info.key,
            'customer_name': license_info.customer_name,
            'is_active': not license_info.is_expired(),
            'is_lifetime': license_info.is_lifetime,
            'expires_on': license_info.expires_on.isoformat(),
            'remaining_days': license_info.remaining_days,
            'device_usage': {
                'current': license_info.device_count,
                'maximum': license_info.max_device_count,
                'percentage': usage_stats['device_usage_percent']
            },
            'client_usage': {
                'current': license_info.client_count,
                'maximum': license_info.max_client_count,
                'percentage': usage_stats['client_usage_percent']
            },
            'warnings': []
        }
        
        # Add warnings for various conditions
        if license_info.is_expired():
            status['warnings'].append('License has expired')
        elif license_info.is_near_expiry(30):
            status['warnings'].append(
                f'License expires in {license_info.remaining_days} days'
            )
        
        if usage_stats['device_usage_percent'] > 80:
            status['warnings'].append(
                f'Device usage at {usage_stats["device_usage_percent"]}%'
            )
        
        if usage_stats['client_usage_percent'] > 80:
            status['warnings'].append(
                f'Client usage at {usage_stats["client_usage_percent"]}%'
            )
        
        if license_info.is_locked_down:
            status['warnings'].append('License is in locked down mode')
        
        return status


class SetLicenseCommand(LicenseCommand):
    """Command for setting/updating license key.
    
    This command allows updating the system license key
    and validates the operation.
    """
    
    def __init__(self, api_client, license_key: str):
        """Initialize set license command.
        
        Args:
            api_client: The License API client instance
            license_key: The new license key to set
        """
        super().__init__(api_client)
        self._license_key = license_key

    def execute(self) -> bool:
        """Execute set license command.
        
        Returns:
            True if license was set successfully
            
        Raises:
            APIError: If the request fails
            ValueError: If license key is invalid
        """
        if not self._license_key or not self._license_key.strip():
            raise ValueError("License key cannot be empty")
        
        query = SetLicenseQuery(self._license_key)
        response = self._api_client._set_license_query(query)
        
        if response.get('success'):
            return True
        else:
            raise ValueError(
                f"Failed to set license: {response.get('errors', [])}"
            )

    def set_and_verify(self) -> Dict[str, Any]:
        """Set license key and verify the operation.
        
        Returns:
            Dictionary with operation result and new license status
        """
        # Set the license
        success = self.execute()
        
        if success:
            # Verify by getting current license info
            get_command = GetLicenseCommand(self._api_client)
            try:
                new_license = get_command.execute()
                return {
                    'success': True,
                    'message': 'License updated successfully',
                    'license_info': {
                        'key': new_license.key,
                        'customer_name': new_license.customer_name,
                        'expires_on': new_license.expires_on.isoformat(),
                        'remaining_days': new_license.remaining_days,
                        'is_active': not new_license.is_expired()
                    }
                }
            except Exception as e:
                return {
                    'success': True,
                    'message': 'License set but verification failed',
                    'warning': str(e)
                }
        
        return {
            'success': False,
            'message': 'Failed to set license'
        }

    @property
    def license_key(self) -> str:
        """Get the license key to be set.
        
        Returns:
            The license key
        """
        return self._license_key 