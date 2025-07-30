"""
Settings API models for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel


class BannerType(str, Enum):
    """Banner types."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    MAINTENANCE = "maintenance"


class BannerPosition(str, Enum):
    """Banner display positions."""
    TOP = "top"
    BOTTOM = "bottom"
    CENTER = "center"


class ProxyCertType(str, Enum):
    """Proxy certificate types."""
    PEM = "PEM"
    DER = "DER"
    PKCS12 = "PKCS12"


class ProxySettings(AIRBaseModel):
    """Proxy settings model."""
    enabled: bool = False
    address: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    cert_type: Optional[ProxyCertType] = Field(None, alias="certType")
    cert_password: Optional[str] = Field(None, alias="certPassword")
    cert: Optional[str] = None  # Certificate file content


class UpdateProxySettingsRequest(AIRBaseModel):
    """Request model for updating proxy settings."""
    enabled: bool
    address: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    cert_type: Optional[ProxyCertType] = Field(None, alias="certType")
    cert_password: Optional[str] = Field(None, alias="certPassword")
    cert: Optional[bytes] = None  # Certificate file data


class ValidateProxySettingsRequest(AIRBaseModel):
    """Request model for validating proxy settings."""
    enabled: bool
    address: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    cert_type: Optional[ProxyCertType] = Field(None, alias="certType")
    cert_password: Optional[str] = Field(None, alias="certPassword")
    cert: Optional[bytes] = None  # Certificate file data


class SSLCertificateInfo(AIRBaseModel):
    """SSL certificate information."""
    valid_from: Optional[datetime] = Field(None, alias="validFrom")
    valid_to: Optional[datetime] = Field(None, alias="validTo")
    issuer: Optional[Dict[str, str]] = None
    subject: Optional[Dict[str, str]] = None


class SSLSettings(AIRBaseModel):
    """SSL settings model."""
    ca: Optional[SSLCertificateInfo] = None
    certificate: Optional[SSLCertificateInfo] = None


class SMTPSettings(AIRBaseModel):
    """SMTP settings model."""
    enabled: bool = False
    use_secure_connection: Optional[bool] = Field(None, alias="useSecureConnection")
    server: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    from_email: Optional[str] = Field(None, alias="fromEmail")


class SSOProvider(AIRBaseModel):
    """Single Sign-On provider settings."""
    enabled: bool = False
    callback_url: Optional[str] = Field(None, alias="callbackURL")


class OktaSSO(SSOProvider):
    """Okta SSO settings."""
    pass


class AzureSSO(SSOProvider):
    """Azure SSO settings."""
    client_id: Optional[str] = Field(None, alias="clientId")
    tenant_id: Optional[str] = Field(None, alias="tenantId")
    client_secret: Optional[str] = Field(None, alias="clientSecret")


class SingleSignOnSettings(AIRBaseModel):
    """Single Sign-On settings."""
    okta: Optional[OktaSSO] = None
    azure: Optional[AzureSSO] = None


class BackupSchedule(AIRBaseModel):
    """Backup schedule settings."""
    enabled: bool = False
    keep_last: Optional[int] = Field(None, alias="keepLast")
    start_date: Optional[datetime] = Field(None, alias="startDate")
    recurrence: Optional[str] = None


class BackupRestoreSettings(AIRBaseModel):
    """Backup and restore settings."""
    location: Optional[str] = None
    schedule: Optional[BackupSchedule] = None
    encryption_enabled: Optional[bool] = Field(None, alias="encryptionEnabled")


class AutoAssetTaggingSettings(AIRBaseModel):
    """Auto asset tagging settings."""
    enabled: bool = False


class IPRestrictionSettings(AIRBaseModel):
    """IP restriction settings."""
    rules: List[Dict[str, Any]] = []


class LocardSettings(AIRBaseModel):
    """Locard settings."""
    organization: Optional[str] = None
    host: Optional[str] = None
    username: Optional[str] = None
    enabled: bool = False


class PolicySettings(AIRBaseModel):
    """Policy settings."""
    enabled: bool = False


class AgentUpdateSettings(AIRBaseModel):
    """Agent update settings."""
    time_frame: Optional[bool] = Field(None, alias="timeFrame")
    auto_update: Optional[bool] = Field(None, alias="autoUpdate")
    update_from_cdn: Optional[bool] = Field(None, alias="updateFromCdn")


class AgentSettings(AIRBaseModel):
    """Agent settings."""
    tamper_detection_enabled: Optional[bool] = Field(None, alias="tamperDetectionEnabled")
    resolve_public_ip_enabled: Optional[bool] = Field(None, alias="resolvePublicIpEnabled")
    update: Optional[AgentUpdateSettings] = None
    uninstallation_password_protection_enabled: Optional[bool] = Field(None, alias="uninstallationPasswordProtectionEnabled")


class InterACTSettings(AIRBaseModel):
    """InterACT settings."""
    enabled: bool = False


class RFC3161Settings(AIRBaseModel):
    """RFC3161 settings."""
    enabled: bool = False


class MitreAttackSettings(AIRBaseModel):
    """MITRE ATT&CK settings."""
    version: Optional[str] = None
    last_sync: Optional[datetime] = Field(None, alias="lastSync")


class FleetAISettings(AIRBaseModel):
    """Fleet AI settings."""
    enabled: bool = False


class AutoUpdateSettings(AIRBaseModel):
    """Auto update settings."""
    update_time_type: Optional[str] = Field(None, alias="updateTimeType")
    update_time: Optional[str] = Field(None, alias="updateTime")
    update_day: Optional[str] = Field(None, alias="updateDay")
    enabled: bool = False


class ActiveDirectorySettings(AIRBaseModel):
    """Active Directory settings model."""
    enabled: bool = False
    use_secure_connection: Optional[bool] = Field(None, alias="useSecureConnection")
    query: Optional[str] = None
    server: Optional[str] = None
    domain: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class AllSettings(AIRBaseModel):
    """Complete settings model representing all system settings."""
    
    # Core settings
    language: Optional[str] = None
    log_level: Optional[str] = Field(None, alias="logLevel")
    automatic_error_reporting: Optional[bool] = Field(None, alias="automaticErrorReporting")
    multi_port_enabled: Optional[bool] = Field(None, alias="multiPortEnabled")
    enforce_tfa_globally: Optional[bool] = Field(None, alias="enforceTFAGlobally")
    console_address: Optional[str] = Field(None, alias="consoleAddress")
    console_id: Optional[str] = Field(None, alias="consoleId")
    mandatory_case_selection_enabled: Optional[bool] = Field(None, alias="mandatoryCaseSelectionEnabled")
    statistics_start_date: Optional[datetime] = Field(None, alias="statisticsStartDate")
    
    # Complex settings objects
    ssl: Optional[SSLSettings] = None
    proxy: Optional[ProxySettings] = None
    smtp: Optional[SMTPSettings] = None
    active_directory: Optional[ActiveDirectorySettings] = Field(None, alias="activeDirectory")
    syslog: Optional[Dict[str, Any]] = None
    single_sign_on: Optional[SingleSignOnSettings] = Field(None, alias="singleSignOn")
    backup_restore: Optional[BackupRestoreSettings] = Field(None, alias="backupRestore")
    auto_asset_tagging: Optional[AutoAssetTaggingSettings] = Field(None, alias="autoAssetTagging")
    ip_restriction: Optional[IPRestrictionSettings] = Field(None, alias="ipRestriction")
    locard: Optional[LocardSettings] = None
    banner: Optional[Dict[str, Any]] = None
    policy: Optional[PolicySettings] = None
    agent: Optional[AgentSettings] = None
    interact: Optional[InterACTSettings] = Field(None, alias="interACT")
    rfc3161: Optional[RFC3161Settings] = None
    mitre_attack: Optional[MitreAttackSettings] = Field(None, alias="mitreAttack")
    feature_flags: Optional[Dict[str, Any]] = Field(None, alias="featureFlags")
    fleet_ai: Optional[FleetAISettings] = Field(None, alias="fleetAi")
    auto_update: Optional[AutoUpdateSettings] = Field(None, alias="autoUpdate")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    id: Optional[str] = Field(None, alias="_id")


class GeneralSettingsRequest(AIRBaseModel):
    """Request model for updating general settings."""
    
    log_level: Optional[str] = Field(None, alias="logLevel")
    multi_port_enabled: Optional[bool] = Field(None, alias="multiPortEnabled")
    mandatory_case_selection_enabled: Optional[bool] = Field(None, alias="mandatoryCaseSelectionEnabled")
    automatic_error_reporting: Optional[bool] = Field(None, alias="automaticErrorReporting")
    enforce_tfa_globally: Optional[bool] = Field(None, alias="enforceTFAGlobally")
    console_address: Optional[str] = Field(None, alias="consoleAddress")


class BannerSettings(AIRBaseModel):
    """Banner settings model."""
    
    id: Optional[str] = None
    enabled: bool = False
    title: Optional[str] = None
    message: str
    banner_type: BannerType = BannerType.INFO
    position: BannerPosition = BannerPosition.TOP
    dismissible: bool = True
    auto_dismiss: bool = False
    auto_dismiss_timeout: Optional[int] = None  # seconds
    show_from: Optional[datetime] = None
    show_until: Optional[datetime] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    icon: Optional[str] = None
    link_url: Optional[str] = None
    link_text: Optional[str] = None
    target_roles: Optional[list[str]] = None
    target_organizations: Optional[list[int]] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    organization_id: Optional[int] = None


class UpdateBannerSettingsRequest(AIRBaseModel):
    """Request model for updating banner settings with proper API field mapping."""
    
    enabled: Optional[bool] = None
    title: Optional[str] = None
    message: Optional[str] = None
    # API expects these exact field names - use aliases to map from Python names to API names
    users_can_dismiss: Optional[bool] = Field(default=None, alias="usersCanDismiss")
    color: Optional[str] = None  # API expects: general, info, maintenance, warning, alert
    display_time_type: Optional[str] = Field(default=None, alias="displayTimeType")  # always or scheduled
    schedule_times: Optional[Dict[str, Any]] = Field(default=None, alias="scheduleTimes")
    
    # Legacy/additional fields (may not be used by current API)
    banner_type: Optional[BannerType] = None
    position: Optional[BannerPosition] = None
    dismissible: Optional[bool] = None
    auto_dismiss: Optional[bool] = None
    auto_dismiss_timeout: Optional[int] = None
    show_from: Optional[datetime] = None
    show_until: Optional[datetime] = None
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    icon: Optional[str] = None
    link_url: Optional[str] = None
    link_text: Optional[str] = None
    target_roles: Optional[list[str]] = None
    target_organizations: Optional[list[int]] = None


class UpdateActiveDirectorySettingsRequest(AIRBaseModel):
    """Request model for updating Active Directory settings."""
    enabled: bool
    use_secure_connection: Optional[bool] = Field(None, alias="useSecureConnection")
    query: Optional[str] = None
    server: Optional[str] = None
    domain: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class ValidateActiveDirectorySettingsRequest(AIRBaseModel):
    """Request model for validating Active Directory settings."""
    server: str
    domain: str
    username: str
    password: str
    use_secure_connection: Optional[bool] = Field(None, alias="useSecureConnection")


class UpdateSMTPSettingsRequest(AIRBaseModel):
    """Request model for updating SMTP settings."""
    enabled: bool
    server: Optional[str] = None
    port: Optional[int] = None
    use_secure_connection: Optional[bool] = Field(None, alias="useSecureConnection")
    username: Optional[str] = None
    password: Optional[str] = None
    to_address: Optional[str] = Field(None, alias="toAddress")
    from_email: Optional[str] = Field(None, alias="fromEmail")


class ValidateSMTPSettingsRequest(AIRBaseModel):
    """Request model for validating SMTP settings."""
    enabled: bool
    server: Optional[str] = None
    port: Optional[int] = None
    use_secure_connection: Optional[bool] = Field(None, alias="useSecureConnection")
    username: Optional[str] = None
    password: Optional[str] = None
    to_address: Optional[str] = Field(None, alias="toAddress")
    from_email: Optional[str] = Field(None, alias="fromEmail")


class UpdateConsoleAddressSettingsRequest(AIRBaseModel):
    """Request model for updating console address settings."""
    console_address: str = Field(alias="consoleAddress")
    cert_type: Optional[str] = Field(None, alias="certType")  # PEM, DER, PKCS12
    cert_password: Optional[str] = Field(None, alias="certPassword")
    cert: Optional[bytes] = None  # Certificate file data
    key: Optional[bytes] = None  # Key file data


class ValidateConsoleAddressSettingsRequest(AIRBaseModel):
    """Request model for validating console address settings."""
    console_address: str = Field(alias="consoleAddress")


class UpdatePolicySettingsRequest(AIRBaseModel):
    """Request model for updating policy settings."""
    enabled: bool


class UpdateEnforceTFASettingsRequest(AIRBaseModel):
    """Request model for updating enforce TFA settings."""
    enabled: bool


class UpdateAutoAssetTaggingSettingsRequest(AIRBaseModel):
    """Request model for updating auto asset tagging settings."""
    enabled: bool


class UpdateInteractSettingsRequest(AIRBaseModel):
    """Request model for updating InterACT settings."""
    enabled: bool


class UpdateRFC3161SettingsRequest(AIRBaseModel):
    """Request model for updating RFC3161 settings."""
    enabled: bool


class UpdateResponderSettingsRequest(AIRBaseModel):
    """Request model for updating responder/agent settings."""
    enabled: bool


class UpdateLocardSettingsRequest(AIRBaseModel):
    """Request model for updating Locard settings."""
    enabled: bool
    organization: Optional[str] = None
    host: Optional[str] = None
    username: Optional[str] = None


class UpdateUninstallationPasswordProtectionSettingsRequest(AIRBaseModel):
    """Request model for updating uninstallation password protection settings."""
    enabled: bool = Field(alias="enabled")


class UpdateSyslogSettingsRequest(AIRBaseModel):
    """Request model for updating syslog settings"""
    enabled: bool = Field(alias="enabled")
    server: str = Field(alias="server")
    port: int = Field(alias="port")
    protocol: str = Field(alias="protocol")  # tcp or udp


class ValidateSyslogSettingsRequest(AIRBaseModel):
    """Request model for validating syslog settings"""
    enabled: bool = Field(alias="enabled")
    server: str = Field(alias="server")
    port: int = Field(alias="port")
    protocol: str = Field(alias="protocol")  # tcp or udp


class LocalBackupSettings(AIRBaseModel):
    """Local backup settings model"""
    path: str = Field(alias="path")


class SftpBackupSettings(AIRBaseModel):
    """SFTP backup settings model"""
    host: str = Field(alias="host")
    port: int = Field(alias="port", default=22)
    logon_type: str = Field(alias="logonType")  # normal or keyfile
    username: str = Field(alias="username")
    password: str = Field(alias="password", default="")
    private_key: str = Field(alias="privateKey", default="")
    passphrase: str = Field(alias="passphrase", default="")


class BackupScheduleSettings(AIRBaseModel):
    """Backup schedule settings model"""
    enabled: bool = Field(alias="enabled")
    recurrence: str = Field(alias="recurrence", default="monthly")  # daily, weekly, monthly
    start_date: str = Field(alias="startDate")  # ISO datetime
    keep_last: int = Field(alias="keepLast", default=5)


class UpdateBackupRestoreSettingsRequest(AIRBaseModel):
    """Request model for updating backup restore settings"""
    location: str = Field(alias="location")  # local or sftp
    encryption_enabled: bool = Field(alias="encryptionEnabled", default=False)
    encryption_password: str = Field(alias="encryptionPassword", default="")
    local: LocalBackupSettings = Field(alias="local")
    sftp: SftpBackupSettings = Field(alias="sftp")
    schedule: BackupScheduleSettings = Field(alias="schedule")


class ValidateBackupSftpSettingsRequest(AIRBaseModel):
    """Request model for validating backup SFTP settings"""
    host: str = Field(alias="host")
    port: int = Field(alias="port", default=22)
    path: str = Field(alias="path", default="")
    logon_type: str = Field(alias="logonType")  # normal or keyfile
    username: str = Field(alias="username")
    password: str = Field(alias="password", default="")
    private_key: str = Field(alias="privateKey", default="")
    passphrase: str = Field(alias="passphrase", default="")


class AzureSsoSettings(AIRBaseModel):
    """Azure SSO settings model"""
    enabled: bool = Field(alias="enabled")
    tenant_id: str = Field(alias="tenantId")
    client_id: str = Field(alias="clientId")
    client_secret: str = Field(alias="clientSecret")


class OktaSsoSettings(AIRBaseModel):
    """Okta SSO settings model"""
    enabled: bool = Field(alias="enabled")
    entry_point: str = Field(alias="entryPoint")
    issuer: str = Field(alias="issuer")
    cert: str = Field(alias="cert")


class UpdateSingleSignOnSettingsRequest(AIRBaseModel):
    """Request model for updating single sign-on settings"""
    azure: AzureSsoSettings = Field(alias="azure")
    okta: OktaSsoSettings = Field(alias="okta")


class UpdateSslSettingsRequest(AIRBaseModel):
    """Request model for updating SSL settings (multipart form data)"""
    cert_type: str = Field(alias="certType", default="PEM")  # PEM or PKCS12
    cert_password: str = Field(alias="certPassword", default="")
    # Note: cert and key files handled separately in multipart upload


class ValidateSslSettingsRequest(AIRBaseModel):
    """Request model for validating SSL settings (multipart form data)"""
    cert_type: str = Field(alias="certType", default="PEM")  # PEM or PKCS12
    cert_password: str = Field(alias="certPassword", default="")
    # Note: cert and key files handled separately in multipart upload


class SslCertificateSubject(AIRBaseModel):
    """SSL certificate subject information"""
    country_name: str = Field(alias="countryName")
    state_or_province_name: str = Field(alias="stateOrProvinceName")
    locality_name: str = Field(alias="localityName", default="")
    organization_name: str = Field(alias="organizationName")
    organizational_unit_name: str = Field(alias="organizationalUnitName", default="")
    common_name: str = Field(alias="commonName")
    email_address: str = Field(alias="emailAddress", default="")


class SslCertificateValidation(AIRBaseModel):
    """SSL certificate validation response"""
    issuer: SslCertificateSubject = Field(alias="issuer")
    subject: SslCertificateSubject = Field(alias="subject")
    valid_from: str = Field(alias="validFrom")  # ISO datetime
    valid_to: str = Field(alias="validTo")  # ISO datetime 