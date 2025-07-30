"""License models for Binalyze AIR SDK."""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class License:
    """Represents a license in the Binalyze AIR system.
    
    Attributes:
        key: The license key identifier
        is_locked_down: Whether the license is in locked down mode
        activated_on: When the license was activated
        period_days: Total license period in days
        remaining_days: Remaining days until expiration
        expires_on: License expiration date
        device_count: Current number of devices
        max_device_count: Maximum allowed devices
        client_count: Current number of clients
        max_client_count: Maximum allowed clients
        model: License model type
        is_lifetime: Whether this is a lifetime license
        customer_name: Name of the customer
    """
    key: str
    is_locked_down: bool
    activated_on: datetime
    period_days: int
    remaining_days: int
    expires_on: datetime
    device_count: int
    max_device_count: int
    client_count: int
    max_client_count: int
    model: int
    is_lifetime: bool
    customer_name: str

    @classmethod
    def from_dict(cls, data: dict) -> 'License':
        """Create License instance from dictionary data.
        
        Args:
            data: Dictionary containing license data
            
        Returns:
            License instance
        """
        return cls(
            key=data.get('key', ''),
            is_locked_down=data.get('isLockedDown', False),
            activated_on=datetime.fromisoformat(
                data.get('activatedOn', '').replace('Z', '+00:00')
            ) if data.get('activatedOn') else datetime.now(),
            period_days=data.get('periodDays', 0),
            remaining_days=data.get('remainingDays', 0),
            expires_on=datetime.fromisoformat(
                data.get('expiresOn', '').replace('Z', '+00:00')
            ) if data.get('expiresOn') else datetime.now(),
            device_count=data.get('deviceCount', 0),
            max_device_count=data.get('maxDeviceCount', 0),
            client_count=data.get('clientCount', 0),
            max_client_count=data.get('maxClientCount', 0),
            model=data.get('model', 0),
            is_lifetime=data.get('isLifetime', False),
            customer_name=data.get('customerName', '')
        )

    def to_dict(self) -> dict:
        """Convert License instance to dictionary.
        
        Returns:
            Dictionary representation of the license
        """
        return {
            'key': self.key,
            'isLockedDown': self.is_locked_down,
            'activatedOn': self.activated_on.isoformat(),
            'periodDays': self.period_days,
            'remainingDays': self.remaining_days,
            'expiresOn': self.expires_on.isoformat(),
            'deviceCount': self.device_count,
            'maxDeviceCount': self.max_device_count,
            'clientCount': self.client_count,
            'maxClientCount': self.max_client_count,
            'model': self.model,
            'isLifetime': self.is_lifetime,
            'customerName': self.customer_name
        }

    def is_expired(self) -> bool:
        """Check if the license is expired.
        
        Returns:
            True if license is expired, False otherwise
        """
        return self.remaining_days <= 0

    def is_near_expiry(self, days_threshold: int = 30) -> bool:
        """Check if license is near expiry.
        
        Args:
            days_threshold: Number of days to consider as near expiry
            
        Returns:
            True if license expires within threshold days
        """
        return self.remaining_days <= days_threshold

    def get_usage_percentage(self) -> dict:
        """Get usage percentages for devices and clients.
        
        Returns:
            Dictionary with device and client usage percentages
        """
        device_usage = (
            (self.device_count / self.max_device_count * 100) 
            if self.max_device_count > 0 else 0
        )
        client_usage = (
            (self.client_count / self.max_client_count * 100) 
            if self.max_client_count > 0 else 0
        )
        
        return {
            'device_usage_percent': round(device_usage, 2),
            'client_usage_percent': round(client_usage, 2)
        }


@dataclass
class LicenseUpdateRequest:
    """Request model for updating license.
    
    Attributes:
        license_key: The new license key to set
    """
    license_key: str

    def to_dict(self) -> dict:
        """Convert to dictionary for API request.
        
        Returns:
            Dictionary representation for API
        """
        return {
            'licenseKey': self.license_key
        } 