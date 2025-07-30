"""
Settings API for the Binalyze AIR SDK.
"""

from typing import Union, Dict, Any

from ..http_client import HTTPClient
from ..models.settings import (
    BannerSettings, UpdateBannerSettingsRequest, AllSettings, GeneralSettingsRequest,
    UpdateProxySettingsRequest, ValidateProxySettingsRequest, ProxySettings,
    UpdateActiveDirectorySettingsRequest, ValidateActiveDirectorySettingsRequest,
    ActiveDirectorySettings, UpdateSMTPSettingsRequest, ValidateSMTPSettingsRequest,
    UpdateConsoleAddressSettingsRequest, ValidateConsoleAddressSettingsRequest,
    UpdatePolicySettingsRequest, UpdateEnforceTFASettingsRequest,
    UpdateAutoAssetTaggingSettingsRequest, UpdateInteractSettingsRequest,
    UpdateRFC3161SettingsRequest, UpdateResponderSettingsRequest,
    UpdateLocardSettingsRequest, UpdateUninstallationPasswordProtectionSettingsRequest,
    UpdateSyslogSettingsRequest, ValidateSyslogSettingsRequest,
    UpdateBackupRestoreSettingsRequest, ValidateBackupSftpSettingsRequest,
    UpdateSslSettingsRequest, ValidateSslSettingsRequest,
    UpdateSingleSignOnSettingsRequest, SslCertificateValidation
)
from ..queries.settings import (
    GetSettingsQuery, GetBannerSettingsQuery, UpdateProxySettingsQuery,
    ValidateProxySettingsQuery, UpdateActiveDirectorySettingsQuery,
    ValidateActiveDirectorySettingsQuery, UpdateSMTPSettingsQuery,
    ValidateSMTPSettingsQuery, UpdateConsoleAddressSettingsQuery,
    ValidateConsoleAddressSettingsQuery, UpdatePolicySettingsQuery,
    UpdateEnforceTFASettingsQuery, UpdateAutoAssetTaggingSettingsQuery,
    UpdateInteractSettingsQuery, UpdateRFC3161SettingsQuery,
    UpdateResponderSettingsQuery, UpdateLocardSettingsQuery,
    UpdateUninstallationPasswordProtectionSettingsQuery,
    UpdateSyslogSettingsQuery, ValidateSyslogSettingsQuery,
    UpdateBackupRestoreSettingsQuery, ValidateBackupSftpSettingsQuery,
    UpdateSslSettingsQuery, ValidateSslSettingsQuery,
    UpdateSingleSignOnSettingsQuery, GetSsoCallbackUrlQuery
)
from ..commands.settings import (
    UpdateBannerSettingsCommand, UpdateGeneralSettingsCommand,
    UpdateProxySettingsCommand, ValidateProxySettingsCommand,
    UpdateActiveDirectorySettingsCommand, ValidateActiveDirectorySettingsCommand,
    UpdateSMTPSettingsCommand, ValidateSMTPSettingsCommand,
    UpdateConsoleAddressSettingsCommand, ValidateConsoleAddressSettingsCommand,
    UpdatePolicySettingsCommand, UpdateEnforceTFASettingsCommand,
    UpdateAutoAssetTaggingSettingsCommand, UpdateInteractSettingsCommand,
    UpdateRFC3161SettingsCommand, UpdateResponderSettingsCommand,
    UpdateLocardSettingsCommand, UpdateUninstallationPasswordProtectionSettingsCommand,
    UpdateSyslogSettingsCommand, ValidateSyslogSettingsCommand,
    UpdateBackupRestoreSettingsCommand, ValidateBackupSftpSettingsCommand,
    UpdateSslSettingsCommand, ValidateSslSettingsCommand,
    UpdateSingleSignOnSettingsCommand, GetSsoCallbackUrlCommand
)


class SettingsAPI:
    """Settings API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self._http_client = http_client
    
    # QUERIES (Read operations)
    def get_settings(self) -> AllSettings:
        """Get all system settings (includes banner settings in result.banner)."""
        query = GetSettingsQuery(self._http_client)
        return query.execute()
    
    # COMMANDS (Write operations)
    def update_general_settings(self, request: Union[GeneralSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update general settings."""
        command = UpdateGeneralSettingsCommand(self._http_client, request)
        return command.execute()
    
    def update_banner_settings(self, request: Union[UpdateBannerSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update banner settings."""
        command = UpdateBannerSettingsCommand(self._http_client, request)
        return command.execute()

    def update_proxy_settings(self, request: Union[UpdateProxySettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update proxy settings.
        
        Args:
            request: Proxy settings request containing enabled status, address, port, 
                    credentials, and optional certificate information
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateProxySettingsCommand(self._http_client, request)
        return command.execute()

    def validate_proxy_settings(self, request: Union[ValidateProxySettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate proxy settings without applying them.
        
        Args:
            request: Proxy settings request to validate containing enabled status, 
                    address, port, credentials, and optional certificate information
        
        Returns:
            Dictionary with validation result
            
        Raises:
            APIError: If the request fails
        """
        command = ValidateProxySettingsCommand(self._http_client, request)
        return command.execute()

    def update_active_directory_settings(self, request: Union[UpdateActiveDirectorySettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update Active Directory settings.
        
        Args:
            request: Active Directory settings request containing enabled status,
                    server, domain, authentication credentials, and connection options
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateActiveDirectorySettingsCommand(self._http_client, request)
        return command.execute()

    def validate_active_directory_settings(self, request: Union[ValidateActiveDirectorySettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate Active Directory settings without applying them.
        
        Args:
            request: Active Directory settings request to validate containing
                    server, domain, authentication credentials, and connection options
        
        Returns:
            Dictionary with validation result
            
        Raises:
            APIError: If the request fails
        """
        command = ValidateActiveDirectorySettingsCommand(self._http_client, request)
        return command.execute()

    def update_smtp_settings(self, request: Union[UpdateSMTPSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update SMTP settings.
        
        Args:
            request: SMTP settings request containing enabled status, server configuration,
                    authentication credentials, and email addresses
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateSMTPSettingsCommand(self._http_client, request)
        return command.execute()

    def validate_smtp_settings(self, request: Union[ValidateSMTPSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate SMTP settings without applying them.
        
        Args:
            request: SMTP settings request to validate containing enabled status,
                    server configuration, authentication credentials, and email addresses
        
        Returns:
            Dictionary with validation result
            
        Raises:
            APIError: If the request fails
        """
        command = ValidateSMTPSettingsCommand(self._http_client, request)
        return command.execute()

    def update_console_address_settings(self, request: Union[UpdateConsoleAddressSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update console address settings.
        
        Args:
            request: Console address settings request containing console address
                    and optional SSL certificate information
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateConsoleAddressSettingsCommand(self._http_client, request)
        return command.execute()

    def validate_console_address_settings(self, request: Union[ValidateConsoleAddressSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Validate console address settings without applying them.
        
        Args:
            request: Console address settings request to validate
        
        Returns:
            Dictionary with validation result
            
        Raises:
            APIError: If the request fails
        """
        command = ValidateConsoleAddressSettingsCommand(self._http_client, request)
        return command.execute()

    def update_policy_settings(self, request: Union[UpdatePolicySettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update policy settings.
        
        Args:
            request: Policy settings request containing enabled status
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdatePolicySettingsCommand(self._http_client, request)
        return command.execute()

    def update_enforce_tfa_settings(self, request: Union[UpdateEnforceTFASettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update enforce TFA settings.
        
        Args:
            request: Enforce TFA settings request containing enabled status
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateEnforceTFASettingsCommand(self._http_client, request)
        return command.execute()

    def update_auto_asset_tagging_settings(self, request: Union[UpdateAutoAssetTaggingSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update auto asset tagging settings.
        
        Args:
            request: Auto asset tagging settings request containing enabled status
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateAutoAssetTaggingSettingsCommand(self._http_client, request)
        return command.execute()

    def update_interact_settings(self, request: Union[UpdateInteractSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update InterACT settings.
        
        Args:
            request: InterACT settings request containing enabled status
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateInteractSettingsCommand(self._http_client, request)
        return command.execute()

    def update_rfc3161_settings(self, request: Union[UpdateRFC3161SettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update RFC3161 settings.
        
        Args:
            request: RFC3161 settings request containing enabled status
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateRFC3161SettingsCommand(self._http_client, request)
        return command.execute()

    def update_responder_settings(self, request: Union[UpdateResponderSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update responder/agent settings.
        
        Args:
            request: Responder settings request containing enabled status
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateResponderSettingsCommand(self._http_client, request)
        return command.execute()

    def update_locard_settings(self, request: Union[UpdateLocardSettingsRequest, Dict[str, Any]]) -> Dict[str, Any]:
        """Update Locard settings.
        
        Args:
            request: Locard settings request containing enabled status and configuration
        
        Returns:
            Dictionary with operation result
            
        Raises:
            APIError: If the request fails
        """
        command = UpdateLocardSettingsCommand(self._http_client, request)
        return command.execute()

    def update_uninstallation_password_protection_settings(
        self,
        request: Union[UpdateUninstallationPasswordProtectionSettingsRequest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update uninstallation password protection settings."""
        query = UpdateUninstallationPasswordProtectionSettingsQuery(request)
        command = UpdateUninstallationPasswordProtectionSettingsCommand(self._http_client)
        return command.execute(query)

    def update_syslog_settings(
        self,
        request: Union[UpdateSyslogSettingsRequest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update syslog settings."""
        query = UpdateSyslogSettingsQuery(request)
        command = UpdateSyslogSettingsCommand(self._http_client)
        return command.execute(query)

    def validate_syslog_settings(
        self,
        request: Union[ValidateSyslogSettingsRequest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate syslog settings."""
        query = ValidateSyslogSettingsQuery(request)
        command = ValidateSyslogSettingsCommand(self._http_client)
        return command.execute(query)

    def update_backup_restore_settings(
        self,
        request: Union[UpdateBackupRestoreSettingsRequest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update backup restore settings."""
        query = UpdateBackupRestoreSettingsQuery(request)
        command = UpdateBackupRestoreSettingsCommand(self._http_client)
        return command.execute(query)

    def validate_backup_sftp_settings(
        self,
        request: Union[ValidateBackupSftpSettingsRequest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Validate backup SFTP settings."""
        query = ValidateBackupSftpSettingsQuery(request)
        command = ValidateBackupSftpSettingsCommand(self._http_client)
        return command.execute(query)

    def update_ssl_settings(
        self,
        request: Union[UpdateSslSettingsRequest, Dict[str, Any]],
        cert_file: bytes,
        key_file: bytes
    ) -> Dict[str, Any]:
        """Update SSL settings with certificate and key files."""
        query = UpdateSslSettingsQuery(request, cert_file, key_file)
        command = UpdateSslSettingsCommand(self._http_client)
        return command.execute(query)

    def validate_ssl_settings(
        self,
        request: Union[ValidateSslSettingsRequest, Dict[str, Any]],
        cert_file: bytes,
        key_file: bytes
    ) -> SslCertificateValidation:
        """Validate SSL settings with certificate and key files."""
        query = ValidateSslSettingsQuery(request, cert_file, key_file)
        command = ValidateSslSettingsCommand(self._http_client)
        response = command.execute(query)
        return SslCertificateValidation(**response.get('result', {}))

    def update_single_sign_on_settings(
        self,
        request: Union[UpdateSingleSignOnSettingsRequest, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Update single sign-on settings."""
        query = UpdateSingleSignOnSettingsQuery(request)
        command = UpdateSingleSignOnSettingsCommand(self._http_client)
        return command.execute(query)

    def get_sso_callback_url_by_type(
        self,
        sso_type: str
    ) -> str:
        """Get SSO callback URL by type (azure or okta)."""
        query = GetSsoCallbackUrlQuery(sso_type)
        command = GetSsoCallbackUrlCommand(self._http_client)
        response = command.execute(query)
        return response.get('result', '') 