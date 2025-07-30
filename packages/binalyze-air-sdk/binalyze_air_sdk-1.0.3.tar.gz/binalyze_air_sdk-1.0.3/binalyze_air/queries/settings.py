"""
Settings queries for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union, Optional
from ..base import Query
from ..models.settings import (
    BannerSettings, AllSettings, UpdateProxySettingsRequest, 
    ValidateProxySettingsRequest, UpdateActiveDirectorySettingsRequest,
    ValidateActiveDirectorySettingsRequest, UpdateSMTPSettingsRequest,
    ValidateSMTPSettingsRequest, UpdateConsoleAddressSettingsRequest,
    ValidateConsoleAddressSettingsRequest, UpdatePolicySettingsRequest,
    UpdateEnforceTFASettingsRequest, UpdateAutoAssetTaggingSettingsRequest,
    UpdateInteractSettingsRequest, UpdateRFC3161SettingsRequest,
    UpdateResponderSettingsRequest, UpdateLocardSettingsRequest,
    UpdateUninstallationPasswordProtectionSettingsRequest,
    UpdateSyslogSettingsRequest, ValidateSyslogSettingsRequest,
    UpdateBackupRestoreSettingsRequest, ValidateBackupSftpSettingsRequest,
    UpdateSslSettingsRequest, ValidateSslSettingsRequest,
    UpdateSingleSignOnSettingsRequest
)
from ..http_client import HTTPClient


class GetSettingsQuery(Query[AllSettings]):
    """Query to get all system settings."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> AllSettings:
        """Execute the query to get all settings."""
        response = self.http_client.get("settings")
        
        return AllSettings(**response.get("result", {}))


class GetBannerSettingsQuery(Query[BannerSettings]):
    """Query to get banner settings."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> BannerSettings:
        """Execute the query to get banner settings."""
        response = self.http_client.get("settings/banner")
        
        return BannerSettings(**response.get("result", {}))


class UpdateProxySettingsQuery:
    """Query for updating proxy settings."""
    
    def __init__(self, request: Union[UpdateProxySettingsRequest, Dict[str, Any]]):
        """Initialize proxy settings update query.
        
        Args:
            request: Proxy settings request data
        """
        if isinstance(request, dict):
            self._request = UpdateProxySettingsRequest(**request)
        else:
            self._request = request

    def build_form_data(self) -> Dict[str, Any]:
        """Build form data for proxy settings update.
        
        Returns:
            Dictionary of form data
        """
        form_data = {
            'enabled': str(self._request.enabled).lower(),
        }
        
        if self._request.address:
            form_data['address'] = self._request.address
        if self._request.port:
            form_data['port'] = str(self._request.port)
        if self._request.username:
            form_data['username'] = self._request.username
        if self._request.password:
            form_data['password'] = self._request.password
        if self._request.cert_type:
            # Handle both enum and string values - FIXED
            if hasattr(self._request.cert_type, 'value'):
                form_data['certType'] = self._request.cert_type.value
            else:
                form_data['certType'] = self._request.cert_type
        if self._request.cert_password:
            form_data['certPassword'] = self._request.cert_password
        
        return form_data

    def build_files(self) -> Optional[Dict[str, Any]]:
        """Build files data for proxy settings update.
        
        Returns:
            Dictionary of files data or None
        """
        if self._request.cert:
            return {'cert': ('cert.pem', self._request.cert, 'application/x-pem-file')}
        return None


class ValidateProxySettingsQuery:
    """Query for validating proxy settings."""
    
    def __init__(self, request: Union[ValidateProxySettingsRequest, Dict[str, Any]]):
        """Initialize proxy settings validation query.
        
        Args:
            request: Proxy settings validation request data
        """
        if isinstance(request, dict):
            self._request = ValidateProxySettingsRequest(**request)
        else:
            self._request = request

    def build_form_data(self) -> Dict[str, Any]:
        """Build form data for proxy settings validation.
        
        Returns:
            Dictionary of form data
        """
        form_data = {
            'enabled': str(self._request.enabled).lower(),
        }
        
        if self._request.address:
            form_data['address'] = self._request.address
        if self._request.port:
            form_data['port'] = str(self._request.port)
        if self._request.username:
            form_data['username'] = self._request.username
        if self._request.password:
            form_data['password'] = self._request.password
        if self._request.cert_type:
            # Handle both enum and string values - FIXED
            if hasattr(self._request.cert_type, 'value'):
                form_data['certType'] = self._request.cert_type.value
            else:
                form_data['certType'] = self._request.cert_type
        if self._request.cert_password:
            form_data['certPassword'] = self._request.cert_password
        
        return form_data

    def build_files(self) -> Optional[Dict[str, Any]]:
        """Build files data for proxy settings validation.
        
        Returns:
            Dictionary of files data or None
        """
        if self._request.cert:
            return {'cert': ('cert.pem', self._request.cert, 'application/x-pem-file')}
        return None


class UpdateActiveDirectorySettingsQuery:
    """Query for updating Active Directory settings."""
    
    def __init__(self, request: Union[UpdateActiveDirectorySettingsRequest, Dict[str, Any]]):
        """Initialize Active Directory settings update query.
        
        Args:
            request: Active Directory settings request data
        """
        if isinstance(request, dict):
            self._request = UpdateActiveDirectorySettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        """Build request body for Active Directory settings update.
        
        Returns:
            Dictionary of request body data
        """
        return self._request.model_dump(exclude_none=True, by_alias=True)


class ValidateActiveDirectorySettingsQuery:
    """Query for validating Active Directory settings."""
    
    def __init__(self, request: Union[ValidateActiveDirectorySettingsRequest, Dict[str, Any]]):
        """Initialize Active Directory settings validation query.
        
        Args:
            request: Active Directory settings validation request data
        """
        if isinstance(request, dict):
            self._request = ValidateActiveDirectorySettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        """Build request body for Active Directory settings validation.
        
        Returns:
            Dictionary of request body data
        """
        return self._request.model_dump(exclude_none=True, by_alias=True)


class UpdateSMTPSettingsQuery:
    """Query for updating SMTP settings."""
    
    def __init__(self, request: Union[UpdateSMTPSettingsRequest, Dict[str, Any]]):
        """Initialize SMTP settings update query.
        
        Args:
            request: SMTP settings request data
        """
        if isinstance(request, dict):
            self._request = UpdateSMTPSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        """Build request body for SMTP settings update.
        
        Returns:
            Dictionary of request body data
        """
        return self._request.model_dump(exclude_none=True, by_alias=True)


class ValidateSMTPSettingsQuery:
    """Query for validating SMTP settings."""
    
    def __init__(self, request: Union[ValidateSMTPSettingsRequest, Dict[str, Any]]):
        """Initialize SMTP settings validation query.
        
        Args:
            request: SMTP settings validation request data
        """
        if isinstance(request, dict):
            self._request = ValidateSMTPSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        """Build request body for SMTP settings validation.
        
        Returns:
            Dictionary of request body data
        """
        return self._request.model_dump(exclude_none=True, by_alias=True)


class UpdateConsoleAddressSettingsQuery:
    """Query for updating console address settings."""
    
    def __init__(self, request: Union[UpdateConsoleAddressSettingsRequest, Dict[str, Any]]):
        """Initialize console address settings update query.
        
        Args:
            request: Console address settings request data
        """
        if isinstance(request, dict):
            self._request = UpdateConsoleAddressSettingsRequest(**request)
        else:
            self._request = request

    def build_form_data(self) -> Dict[str, Any]:
        """Build form data for console address settings update.
        
        Returns:
            Dictionary of form data
        """
        form_data = {
            'consoleAddress': self._request.console_address,
        }
        
        if self._request.cert_type:
            form_data['certType'] = self._request.cert_type
        if self._request.cert_password:
            form_data['certPassword'] = self._request.cert_password
        
        return form_data

    def build_files(self) -> Optional[Dict[str, Any]]:
        """Build files data for console address settings update.
        
        Returns:
            Dictionary of files data or None
        """
        files = {}
        if self._request.cert:
            files['cert'] = ('cert.pem', self._request.cert, 'application/x-pem-file')
        if self._request.key:
            files['key'] = ('key.pem', self._request.key, 'application/x-pem-file')
        return files if files else None


class ValidateConsoleAddressSettingsQuery:
    """Query for validating console address settings."""
    
    def __init__(self, request: Union[ValidateConsoleAddressSettingsRequest, Dict[str, Any]]):
        """Initialize console address settings validation query.
        
        Args:
            request: Console address settings validation request data
        """
        if isinstance(request, dict):
            self._request = ValidateConsoleAddressSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        """Build request body for console address settings validation.
        
        Returns:
            Dictionary of request body data
        """
        return self._request.model_dump(exclude_none=True, by_alias=True)


# Simple JSON-based settings queries (most have the same pattern)
class UpdatePolicySettingsQuery:
    """Query for updating policy settings."""
    
    def __init__(self, request: Union[UpdatePolicySettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdatePolicySettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)


class UpdateEnforceTFASettingsQuery:
    """Query for updating enforce TFA settings."""
    
    def __init__(self, request: Union[UpdateEnforceTFASettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateEnforceTFASettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)


class UpdateAutoAssetTaggingSettingsQuery:
    """Query for updating auto asset tagging settings."""
    
    def __init__(self, request: Union[UpdateAutoAssetTaggingSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateAutoAssetTaggingSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)


class UpdateInteractSettingsQuery:
    """Query for updating InterACT settings."""
    
    def __init__(self, request: Union[UpdateInteractSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateInteractSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)


class UpdateRFC3161SettingsQuery:
    """Query for updating RFC3161 settings."""
    
    def __init__(self, request: Union[UpdateRFC3161SettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateRFC3161SettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)


class UpdateResponderSettingsQuery:
    """Query for updating responder/agent settings."""
    
    def __init__(self, request: Union[UpdateResponderSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateResponderSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)


class UpdateLocardSettingsQuery:
    """Query for updating Locard settings."""
    
    def __init__(self, request: Union[UpdateLocardSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateLocardSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)


class UpdateUninstallationPasswordProtectionSettingsQuery:
    """Query for updating uninstallation password protection settings."""
    
    def __init__(self, request: Union[UpdateUninstallationPasswordProtectionSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateUninstallationPasswordProtectionSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)

# ADD THE REMAINING 9 QUERIES FOR SETTINGS API

class UpdateSyslogSettingsQuery:
    """Query for updating syslog settings."""
    
    def __init__(self, request: Union[UpdateSyslogSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateSyslogSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)

class ValidateSyslogSettingsQuery:
    """Query for validating syslog settings."""
    
    def __init__(self, request: Union[ValidateSyslogSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = ValidateSyslogSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)

class UpdateBackupRestoreSettingsQuery:
    """Query for updating backup restore settings."""
    
    def __init__(self, request: Union[UpdateBackupRestoreSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateBackupRestoreSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)

class ValidateBackupSftpSettingsQuery:
    """Query for validating backup SFTP settings."""
    
    def __init__(self, request: Union[ValidateBackupSftpSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = ValidateBackupSftpSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)

class UpdateSslSettingsQuery:
    """Query for updating SSL settings."""
    
    def __init__(self, request: Union[UpdateSslSettingsRequest, Dict[str, Any]], cert_file: Optional[bytes] = None, key_file: Optional[bytes] = None):
        if isinstance(request, dict):
            self._request = UpdateSslSettingsRequest(**request)
        else:
            self._request = request
        self._cert_file = cert_file
        self._key_file = key_file

    def build_body(self) -> Dict[str, Any]:
        """Build form data for SSL settings"""
        form_data = self._request.model_dump(exclude_none=True, by_alias=True)
        if self._cert_file:
            form_data['cert'] = self._cert_file
        if self._key_file:
            form_data['key'] = self._key_file
        return form_data

class ValidateSslSettingsQuery:
    """Query for validating SSL settings."""
    
    def __init__(self, request: Union[ValidateSslSettingsRequest, Dict[str, Any]], cert_file: Optional[bytes] = None, key_file: Optional[bytes] = None):
        if isinstance(request, dict):
            self._request = ValidateSslSettingsRequest(**request)
        else:
            self._request = request
        self._cert_file = cert_file
        self._key_file = key_file

    def build_body(self) -> Dict[str, Any]:
        """Build form data for SSL validation"""
        form_data = self._request.model_dump(exclude_none=True, by_alias=True)
        if self._cert_file:
            form_data['cert'] = self._cert_file
        if self._key_file:
            form_data['key'] = self._key_file
        return form_data

class UpdateSingleSignOnSettingsQuery:
    """Query for updating single sign-on settings."""
    
    def __init__(self, request: Union[UpdateSingleSignOnSettingsRequest, Dict[str, Any]]):
        if isinstance(request, dict):
            self._request = UpdateSingleSignOnSettingsRequest(**request)
        else:
            self._request = request

    def build_body(self) -> Dict[str, Any]:
        return self._request.model_dump(exclude_none=True, by_alias=True)

class GetSsoCallbackUrlQuery:
    """Query for getting SSO callback URL by type."""
    
    def __init__(self, sso_type: str):
        self._sso_type = sso_type

    def get_sso_type(self) -> str:
        """Get the SSO type (azure or okta)"""
        return self._sso_type 