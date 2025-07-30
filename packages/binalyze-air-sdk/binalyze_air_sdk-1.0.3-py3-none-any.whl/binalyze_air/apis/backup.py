"""
Backup API for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from ..http_client import HTTPClient
from ..models.backup import (
    BackupHistoryResponse, BackupFilter, BackupNowRequest, 
    BackupStatus, BackupSource, BackupLocation, BackupStats
)
from ..queries.backup import (
    GetBackupHistoryQuery, GetBackupDownloadQuery
)
from ..commands.backup import (
    BackupNowCommand, DeleteBackupCommand
)


class BackupAPI:
    """Backup API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def get_history(self, filter_params: Optional[BackupFilter] = None) -> BackupHistoryResponse:
        """Get backup history with optional filtering."""
        query = GetBackupHistoryQuery(self.http_client, filter_params)
        return query.execute()
    
    def download_backup(self, backup_id: str) -> Dict[str, Any]:
        """Download a backup by ID."""
        query = GetBackupDownloadQuery(self.http_client, backup_id)
        return query.execute()
    
    # COMMANDS (Write operations)
    def backup_now(self, request: BackupNowRequest) -> Dict[str, Any]:
        """Create an immediate backup."""
        command = BackupNowCommand(self.http_client, request)
        return command.execute()
    
    def delete_backup(self, backup_id: str) -> Dict[str, Any]:
        """Delete a backup by ID."""
        command = DeleteBackupCommand(self.http_client, backup_id)
        return command.execute()
    
    # Convenience methods
    def backup_all_endpoints(self, organization_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Create a backup of all endpoints."""
        request = BackupNowRequest(organizationIds=organization_ids)
        return self.backup_now(request)
    
    def backup_specific_endpoints(self, endpoint_ids: List[str], 
                                 organization_ids: Optional[List[int]] = None) -> Dict[str, Any]:
        """Create a backup of specific endpoints."""
        request = BackupNowRequest(
            includedEndpointIds=endpoint_ids,
            organizationIds=organization_ids
        )
        return self.backup_now(request)
    
    def get_recent_backups(self, days: int = 7) -> BackupHistoryResponse:
        """Get recent backups from the last N days."""
        end_date = datetime.utcnow()
        start_date = datetime.utcnow().replace(day=end_date.day - days)
        
        filter_params = BackupFilter(
            startDate=start_date,
            endDate=end_date,
            sortBy="startDate",
            sortType="DESC"
        )
        return self.get_history(filter_params)
    
    def get_failed_backups(self) -> BackupHistoryResponse:
        """Get all failed backups."""
        filter_params = BackupFilter(
            status=BackupStatus.FAILED,
            sortBy="startDate",
            sortType="DESC"
        )
        return self.get_history(filter_params)
    
    def get_in_progress_backups(self) -> BackupHistoryResponse:
        """Get all in-progress backups."""
        filter_params = BackupFilter(
            status=BackupStatus.IN_PROGRESS,
            sortBy="startDate",
            sortType="DESC"
        )
        return self.get_history(filter_params)
    
    def get_user_backups(self, username: str) -> BackupHistoryResponse:
        """Get backups created by a specific user."""
        filter_params = BackupFilter(
            username=username,
            source=BackupSource.USER,
            sortBy="startDate",
            sortType="DESC"
        )
        return self.get_history(filter_params)
    
    def get_scheduled_backups(self) -> BackupHistoryResponse:
        """Get backups created by scheduler."""
        filter_params = BackupFilter(
            source=BackupSource.SCHEDULER,
            sortBy="startDate",
            sortType="DESC"
        )
        return self.get_history(filter_params)
    
    def get_backup_stats(self) -> BackupStats:
        """Get backup statistics summary."""
        # Get all backup history to calculate stats
        all_backups = self.get_history(BackupFilter(pageSize=1000))
        
        stats = BackupStats()
        stats.total_backups = len(all_backups.entities)
        
        total_duration = 0
        backup_count_with_duration = 0
        
        for backup in all_backups.entities:
            # Count by status
            if backup.status == BackupStatus.SUCCEEDED:
                stats.successful_backups += 1
            elif backup.status == BackupStatus.FAILED:
                stats.failed_backups += 1
            elif backup.status == BackupStatus.IN_PROGRESS:
                stats.in_progress_backups += 1
            
            # Sum total size
            if backup.size:
                stats.total_size_bytes += backup.size
            
            # Calculate average backup time
            if backup.start_date and backup.end_date:
                duration = (backup.end_date - backup.start_date).total_seconds() / 60
                total_duration += duration
                backup_count_with_duration += 1
            
            # Track last backup date
            if not stats.last_backup_date or backup.start_date > stats.last_backup_date:
                stats.last_backup_date = backup.start_date
        
        # Calculate average backup time
        if backup_count_with_duration > 0:
            stats.average_backup_time_minutes = total_duration / backup_count_with_duration
        
        return stats
    
    def cleanup_old_backups(self, days_to_keep: int = 30) -> List[str]:
        """Delete backups older than specified days and return deleted backup IDs."""
        cutoff_date = datetime.utcnow().replace(day=datetime.utcnow().day - days_to_keep)
        
        filter_params = BackupFilter(
            endDate=cutoff_date,
            status=BackupStatus.SUCCEEDED,
            sortBy="startDate",
            sortType="ASC",
            pageSize=1000
        )
        
        old_backups = self.get_history(filter_params)
        deleted_ids = []
        
        for backup in old_backups.entities:
            try:
                self.delete_backup(backup.id)
                deleted_ids.append(backup.id)
            except Exception:
                # Continue with other backups if one fails
                continue
        
        return deleted_ids 