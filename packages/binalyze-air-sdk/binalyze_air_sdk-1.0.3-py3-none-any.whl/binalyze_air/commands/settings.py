"""
Settings commands for the Binalyze AIR SDK.
"""

from typing import Dict, Any, Union

from ..base import Command
from ..models.settings import (
    BannerSettings, UpdateBannerSettingsRequest, GeneralSettingsRequest,
    UpdateProxySettingsRequest, ValidateProxySettingsRequest,
    UpdateActiveDirectorySettingsRequest, ValidateActiveDirectorySettingsRequest,
    UpdateSMTPSettingsRequest, ValidateSMTPSettingsRequest,
    UpdateConsoleAddressSettingsRequest, ValidateConsoleAddressSettingsRequest,
    UpdatePolicySettingsRequest, UpdateEnforceTFASettingsRequest,
    UpdateAutoAssetTaggingSettingsRequest, UpdateInteractSettingsRequest,
    UpdateRFC3161SettingsRequest, UpdateResponderSettingsRequest,
    UpdateLocardSettingsRequest, UpdateUninstallationPasswordProtectionSettingsRequest
)
from ..queries.settings import (
    UpdateProxySettingsQuery, ValidateProxySettingsQuery,
    UpdateActiveDirectorySettingsQuery, ValidateActiveDirectorySettingsQuery,
    UpdateSMTPSettingsQuery, ValidateSMTPSettingsQuery,
    UpdateConsoleAddressSettingsQuery, ValidateConsoleAddressSettingsQuery,
    UpdatePolicySettingsQuery, UpdateEnforceTFASettingsQuery,
    UpdateAutoAssetTaggingSettingsQuery, UpdateInteractSettingsQuery,
    UpdateRFC3161SettingsQuery, UpdateResponderSettingsQuery,
    UpdateLocardSettingsQuery, UpdateUninstallationPasswordProtectionSettingsQuery,
    UpdateSyslogSettingsQuery, ValidateSyslogSettingsQuery,
    UpdateBackupRestoreSettingsQuery, ValidateBackupSftpSettingsQuery,
    UpdateSslSettingsQuery, ValidateSslSettingsQuery,
    UpdateSingleSignOnSettingsQuery, GetSsoCallbackUrlQuery
)
from ..http_client import HTTPClient


class UpdateGeneralSettingsCommand(Command[Dict[str, Any]]):
    """Command to update general settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[GeneralSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self):
        """Execute the update general settings command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            # Use by_alias=True to ensure field aliases are properly mapped to API field names
            payload = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.put("settings/general", json_data=payload)
        return response


class UpdateBannerSettingsCommand(Command[BannerSettings]):
    """Command to update banner settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateBannerSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self):
        """Execute the update banner settings command."""
        # Handle both dict and model objects
        if isinstance(self.request, dict):
            payload = self.request
        else:
            # Use by_alias=True to ensure field aliases are properly mapped to API field names
            payload = self.request.model_dump(exclude_none=True, by_alias=True)
        
        response = self.http_client.put("settings/banner", json_data=payload)
        return response


class UpdateProxySettingsCommand(Command[Dict[str, Any]]):
    """Command to update proxy settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateProxySettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the update proxy settings command."""
        query = UpdateProxySettingsQuery(self.request)
        form_data = query.build_form_data()
        files = query.build_files()
        
        if files:
            response = self.http_client.upload_multipart(
                "settings/proxy", 
                data=form_data, 
                files=files,
                method='PUT'
            )
        else:
            response = self.http_client.put("settings/proxy", data=form_data)
        
        return response


class ValidateProxySettingsCommand(Command[Dict[str, Any]]):
    """Command to validate proxy settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[ValidateProxySettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the validate proxy settings command."""
        query = ValidateProxySettingsQuery(self.request)
        form_data = query.build_form_data()
        files = query.build_files()
        
        if files:
            response = self.http_client.upload_multipart(
                "settings/validate-proxy", 
                data=form_data, 
                files=files,
                method='POST'
            )
        else:
            response = self.http_client.post("settings/validate-proxy", data=form_data)
        
        return response


class UpdateActiveDirectorySettingsCommand(Command[Dict[str, Any]]):
    """Command to update Active Directory settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateActiveDirectorySettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the update Active Directory settings command."""
        query = UpdateActiveDirectorySettingsQuery(self.request)
        payload = query.build_body()
        
        response = self.http_client.put("settings/active-directory", json_data=payload)
        return response


class ValidateActiveDirectorySettingsCommand(Command[Dict[str, Any]]):
    """Command to validate Active Directory settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[ValidateActiveDirectorySettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the validate Active Directory settings command."""
        query = ValidateActiveDirectorySettingsQuery(self.request)
        payload = query.build_body()
        
        response = self.http_client.post("settings/active-directory", json_data=payload)
        return response


class UpdateSMTPSettingsCommand(Command[Dict[str, Any]]):
    """Command to update SMTP settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateSMTPSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the update SMTP settings command."""
        query = UpdateSMTPSettingsQuery(self.request)
        payload = query.build_body()
        
        response = self.http_client.put("settings/smtp", json_data=payload)
        return response


class ValidateSMTPSettingsCommand(Command[Dict[str, Any]]):
    """Command to validate SMTP settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[ValidateSMTPSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the validate SMTP settings command."""
        query = ValidateSMTPSettingsQuery(self.request)
        payload = query.build_body()
        
        response = self.http_client.post("settings/validate-smtp", json_data=payload)
        return response


class UpdateConsoleAddressSettingsCommand(Command[Dict[str, Any]]):
    """Command to update console address settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateConsoleAddressSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the update console address settings command."""
        query = UpdateConsoleAddressSettingsQuery(self.request)
        form_data = query.build_form_data()
        files = query.build_files()
        
        if files:
            response = self.http_client.upload_multipart(
                "settings/console-address", 
                data=form_data, 
                files=files,
                method='PUT'
            )
        else:
            response = self.http_client.put("settings/console-address", data=form_data)
        
        return response


class ValidateConsoleAddressSettingsCommand(Command[Dict[str, Any]]):
    """Command to validate console address settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[ValidateConsoleAddressSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        """Execute the validate console address settings command."""
        query = ValidateConsoleAddressSettingsQuery(self.request)
        payload = query.build_body()
        
        response = self.http_client.post("settings/validate-console-address", json_data=payload)
        return response


# Simple JSON-based settings commands (most have the same pattern)
class UpdatePolicySettingsCommand(Command[Dict[str, Any]]):
    """Command to update policy settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdatePolicySettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        query = UpdatePolicySettingsQuery(self.request)
        payload = query.build_body()
        return self.http_client.put("settings/policy", json_data=payload)


class UpdateEnforceTFASettingsCommand(Command[Dict[str, Any]]):
    """Command to update enforce TFA settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateEnforceTFASettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        query = UpdateEnforceTFASettingsQuery(self.request)
        payload = query.build_body()
        return self.http_client.put("settings/enforce-tfa", json_data=payload)


class UpdateAutoAssetTaggingSettingsCommand(Command[Dict[str, Any]]):
    """Command to update auto asset tagging settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateAutoAssetTaggingSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        query = UpdateAutoAssetTaggingSettingsQuery(self.request)
        payload = query.build_body()
        return self.http_client.put("settings/auto-asset-tagging", json_data=payload)


class UpdateInteractSettingsCommand(Command[Dict[str, Any]]):
    """Command to update InterACT settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateInteractSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        query = UpdateInteractSettingsQuery(self.request)
        payload = query.build_body()
        return self.http_client.put("settings/interact", json_data=payload)


class UpdateRFC3161SettingsCommand(Command[Dict[str, Any]]):
    """Command to update RFC3161 settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateRFC3161SettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        query = UpdateRFC3161SettingsQuery(self.request)
        payload = query.build_body()
        return self.http_client.put("settings/rfc3161", json_data=payload)


class UpdateResponderSettingsCommand(Command[Dict[str, Any]]):
    """Command to update responder/agent settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateResponderSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        query = UpdateResponderSettingsQuery(self.request)
        payload = query.build_body()
        return self.http_client.put("settings/agent", json_data=payload)


class UpdateLocardSettingsCommand(Command[Dict[str, Any]]):
    """Command to update Locard settings."""
    
    def __init__(self, http_client: HTTPClient, request: Union[UpdateLocardSettingsRequest, Dict[str, Any]]):
        self.http_client = http_client
        self.request = request
    
    def execute(self) -> Dict[str, Any]:
        query = UpdateLocardSettingsQuery(self.request)
        payload = query.build_body()
        return self.http_client.put("settings/locard", json_data=payload)


class UpdateUninstallationPasswordProtectionSettingsCommand(Command):
    """Command for updating uninstallation password protection settings"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self, query: UpdateUninstallationPasswordProtectionSettingsQuery) -> Dict[str, Any]:
        """Execute update uninstallation password protection settings command"""
        payload = query.build_body()
        return self.http_client.put("settings/uninstallation-password-protection", json_data=payload)


class UpdateSyslogSettingsCommand(Command):
    """Command for updating syslog settings"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self, query: UpdateSyslogSettingsQuery) -> Dict[str, Any]:
        """Execute update syslog settings command"""
        payload = query.build_body()
        return self.http_client.put("settings/syslog", json_data=payload)


class ValidateSyslogSettingsCommand(Command):
    """Command for validating syslog settings"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self, query: ValidateSyslogSettingsQuery) -> Dict[str, Any]:
        """Execute validate syslog settings command"""
        payload = query.build_body()
        return self.http_client.post("settings/validate-syslog", json_data=payload)


class UpdateBackupRestoreSettingsCommand(Command):
    """Command for updating backup restore settings"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self, query: UpdateBackupRestoreSettingsQuery) -> Dict[str, Any]:
        """Execute update backup restore settings command"""
        payload = query.build_body()
        return self.http_client.put("settings/backup-restore", json_data=payload)


class ValidateBackupSftpSettingsCommand(Command):
    """Command for validating backup SFTP settings"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self, query: ValidateBackupSftpSettingsQuery) -> Dict[str, Any]:
        """Execute validate backup SFTP settings command"""
        payload = query.build_body()
        return self.http_client.post("settings/validate-backup-sftp", json_data=payload)


class UpdateSslSettingsCommand(Command):
    """Command for updating SSL settings"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self, query: UpdateSslSettingsQuery) -> Dict[str, Any]:
        """Execute update SSL settings command"""
        payload = query.build_body()
        return self.http_client.put("settings/ssl", data=payload)


class ValidateSslSettingsCommand(Command):
    """Command for validating SSL settings"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self, query: ValidateSslSettingsQuery) -> Dict[str, Any]:
        """Execute validate SSL settings command"""
        payload = query.build_body()
        return self.http_client.post("settings/validate-ssl", data=payload)


class UpdateSingleSignOnSettingsCommand(Command):
    """Command for updating single sign-on settings"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self, query: UpdateSingleSignOnSettingsQuery) -> Dict[str, Any]:
        """Execute update single sign-on settings command"""
        payload = query.build_body()
        return self.http_client.put("settings/single-sign-on", json_data=payload)


class GetSsoCallbackUrlCommand(Command):
    """Command for getting SSO callback URL by type"""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self, query: GetSsoCallbackUrlQuery) -> Dict[str, Any]:
        """Execute get SSO callback URL command"""
        sso_type = query.get_sso_type()
        return self.http_client.get(f"settings/sso/{sso_type}/callback-url") 