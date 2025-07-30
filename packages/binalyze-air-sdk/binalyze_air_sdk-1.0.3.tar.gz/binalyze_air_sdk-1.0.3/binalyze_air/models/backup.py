"""
Backup models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel


class BackupStatus(str, Enum):
    """Backup status enumeration."""
    IN_PROGRESS = "in-progress"
    SUCCEEDED = "succeeded"
    UPLOADING = "uploading"
    FAILED = "failed"
    QUEUED = "queued"


class BackupSource(str, Enum):
    """Backup source enumeration."""
    USER = "user"
    SCHEDULER = "scheduler"


class BackupLocation(str, Enum):
    """Backup location enumeration."""
    LOCAL = "local"
    SFTP = "sftp"
    S3 = "s3"


class Backup(AIRBaseModel):
    """Backup model."""
    
    id: str = Field(alias="_id")
    location: BackupLocation
    status: BackupStatus
    size: Optional[int] = None
    source: BackupSource
    username: str
    to: str  # Backup file path/location
    stats: Dict[str, Any] = {}
    start_date: datetime = Field(alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class BackupFilter(AIRBaseModel):
    """Filter parameters for backup history."""
    
    page_size: Optional[int] = Field(default=10, alias="pageSize")
    page_number: Optional[int] = Field(default=1, alias="pageNumber")
    sort_type: Optional[str] = Field(default="DESC", alias="sortType")  # ASC or DESC
    sort_by: Optional[str] = Field(default="createdAt", alias="sortBy")  # source, username, status, startDate, createdAt
    search_term: Optional[str] = Field(default=None, alias="searchTerm")
    username: Optional[str] = None
    source: Optional[BackupSource] = None
    status: Optional[BackupStatus] = None
    start_date: Optional[datetime] = Field(default=None, alias="startDate")
    end_date: Optional[datetime] = Field(default=None, alias="endDate")
    location: Optional[BackupLocation] = None


class BackupHistoryResponse(AIRBaseModel):
    """Paginated response for backup history."""
    
    entities: List[Backup]
    filters: List[Dict[str, Any]]
    sortables: List[str]
    total_entity_count: int = Field(alias="totalEntityCount")
    current_page: int = Field(alias="currentPage")
    page_size: int = Field(alias="pageSize")
    previous_page: int = Field(alias="previousPage")
    total_page_count: int = Field(alias="totalPageCount")
    next_page: int = Field(alias="nextPage")


class BackupNowRequest(AIRBaseModel):
    """Request model for creating an immediate backup."""
    
    # The API appears to use filters for backup scope
    # Based on the prerequest script, it uses includedEndpointIds
    include_endpoint_ids: Optional[List[str]] = Field(default=None, alias="includedEndpointIds")
    exclude_endpoint_ids: Optional[List[str]] = Field(default=None, alias="excludedEndpointIds")
    organization_ids: Optional[List[int]] = Field(default=None, alias="organizationIds")
    backup_location: Optional[BackupLocation] = BackupLocation.LOCAL


class BackupConfig(AIRBaseModel):
    """Backup configuration model."""
    
    enabled: bool = True
    schedule: Optional[str] = None  # Cron expression
    location: BackupLocation = BackupLocation.LOCAL
    retention_days: Optional[int] = Field(default=30, alias="retentionDays")
    compression: bool = True
    encryption: bool = False
    
    # SFTP configuration
    sftp_host: Optional[str] = Field(default=None, alias="sftpHost")
    sftp_port: Optional[int] = Field(default=22, alias="sftpPort")
    sftp_username: Optional[str] = Field(default=None, alias="sftpUsername")
    sftp_password: Optional[str] = Field(default=None, alias="sftpPassword")
    sftp_path: Optional[str] = Field(default=None, alias="sftpPath")
    
    # S3 configuration
    s3_bucket: Optional[str] = Field(default=None, alias="s3Bucket")
    s3_region: Optional[str] = Field(default=None, alias="s3Region")
    s3_access_key: Optional[str] = Field(default=None, alias="s3AccessKey")
    s3_secret_key: Optional[str] = Field(default=None, alias="s3SecretKey")
    s3_path: Optional[str] = Field(default=None, alias="s3Path")


class BackupStats(AIRBaseModel):
    """Backup statistics model."""
    
    total_backups: int = Field(default=0, alias="totalBackups")
    successful_backups: int = Field(default=0, alias="successfulBackups")
    failed_backups: int = Field(default=0, alias="failedBackups")
    in_progress_backups: int = Field(default=0, alias="inProgressBackups")
    total_size_bytes: int = Field(default=0, alias="totalSizeBytes")
    average_backup_time_minutes: float = Field(default=0.0, alias="averageBackupTimeMinutes")
    last_backup_date: Optional[datetime] = Field(default=None, alias="lastBackupDate")
    next_scheduled_backup: Optional[datetime] = Field(default=None, alias="nextScheduledBackup")


class BackupDownloadInfo(AIRBaseModel):
    """Backup download information model."""
    
    backup_id: str = Field(alias="backupId")
    filename: str
    size_bytes: int = Field(alias="sizeBytes")
    download_url: str = Field(alias="downloadUrl")
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt") 