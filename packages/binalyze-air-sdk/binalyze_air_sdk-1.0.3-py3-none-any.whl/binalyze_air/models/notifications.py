"""
Notifications API models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel, Filter


class NotificationLevel(str, Enum):
    """Notification severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


class NotificationType(str, Enum):
    """Notification types."""
    TASK_COMPLETED = "task-completed"
    TASK_FAILED = "task-failed"
    FLAG_CREATED = "flag-created"
    FLAG_UPDATED = "flag-updated"
    FLAG_DELETED = "flag-deleted"
    ASSET_CREATED = "asset-created"
    ASSET_REGISTERED = "asset-registered"
    ASSET_REGISTER_FAILED = "asset-register-failed"
    ASSET_RE_REGISTERED = "asset-re-registered"
    ASSET_RE_REGISTER_FAILED = "asset-re-register-failed"
    CASE_CREATED = "case-created"
    CASE_COMMENT_ADDED = "case-comment-added"
    POLICY_EXECUTED = "policy-executed"
    SYSTEM_UPDATE = "system-update"
    ALERT = "alert"
    UPDATE_CHECK_FAILED = "update-check-failed"
    NATS_PORT_DISABLED = "nats-port-disabled"
    LDAP_SYNC_AUTH_FAILED = "ldap-sync-auth-failed"
    CLOUD_SYNC_FAILED = "cloud-sync-failed"
    REMOTE_BACKUP_DELETION_FAILED = "remote-backup-deletion-failed"
    TASK_CANCELLED_AS_CASE_CLOSED = "task-cancelled-as-case-closed"
    FINDING_EXCLUSION_CREATED = "finding-exclusion-created"
    FINDING_EXCLUSION_UPDATED = "finding-exclusion-updated"
    FINDING_EXCLUSION_DELETED = "finding-exclusion-deleted"
    TASK_COMMENT_ADDED = "task-comment-added"
    NEW_VERSION_RELEASED = "new-version-released"
    UPDATE_SCHEDULED = "update-scheduled"
    UPDATE_COMPLETED = "update-completed"
    UPDATE_FAILED = "update-failed"


class Notification(AIRBaseModel):
    """Notification model."""
    
    id: Union[int, str] = Field(alias="_id")
    is_read: bool = Field(alias="isRead")
    level: NotificationLevel
    type: NotificationType
    organization_ids: List[int] = Field(alias="organizationIds")
    data: Dict[str, Any] = {}
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    created_by: Optional[str] = Field(default=None, alias="createdBy")
    title: Optional[str] = None
    message: Optional[str] = None
    action_url: Optional[str] = Field(default=None, alias="actionUrl")
    expires_at: Optional[datetime] = Field(default=None, alias="expiresAt")


class NotificationsList(AIRBaseModel):
    """Paginated notifications list response."""
    
    entities: List[Notification]
    current_page: int = Field(alias="currentPage")
    page_size: int = Field(alias="pageSize")
    total_entity_count: int = Field(alias="totalEntityCount")
    total_page_count: int = Field(alias="totalPageCount")


class NotificationsFilter(Filter):
    """Filter for notifications queries."""
    
    # Pagination
    page_number: Optional[int] = Field(default=None, alias="pageNumber")
    page_size: Optional[int] = Field(default=None, alias="pageSize")
    sort_by: Optional[str] = Field(default=None, alias="sortBy")
    sort_type: Optional[str] = Field(default=None, alias="sortType")  # ASC, DESC
    
    # Notification-specific filters
    is_read: Optional[bool] = Field(default=None, alias="isRead")
    level: Optional[NotificationLevel] = None
    type: Optional[NotificationType] = None
    organization_ids: Optional[Union[int, List[int]]] = Field(default=None, alias="organizationIds")
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to query parameters."""
        params = {}
        
        # Pagination parameters (not in filter namespace)
        if self.page_number is not None:
            params["pageNumber"] = self.page_number
        if self.page_size is not None:
            params["pageSize"] = self.page_size
        if self.sort_by is not None:
            params["sortBy"] = self.sort_by
        if self.sort_type is not None:
            params["sortType"] = self.sort_type
        
        # Filter parameters (with filter[] namespace)
        if self.is_read is not None:
            params["filter[isRead]"] = "true" if self.is_read else "false"
        if self.level is not None:
            params["filter[level]"] = self.level.value if hasattr(self.level, 'value') else str(self.level)
        if self.type is not None:
            params["filter[type]"] = self.type.value if hasattr(self.type, 'value') else str(self.type)
        if self.organization_ids is not None:
            if isinstance(self.organization_ids, list):
                params["filter[organizationIds]"] = ",".join([str(x) for x in self.organization_ids])
            else:
                params["filter[organizationIds]"] = str(self.organization_ids)
        
        return params


class MarkAsReadRequest(AIRBaseModel):
    """Request model for marking notifications as read."""
    
    notification_ids: Optional[List[Union[int, str]]] = None
    all_notifications: bool = False


class DeleteNotificationsRequest(AIRBaseModel):
    """Request model for deleting notifications."""
    
    notification_ids: Optional[List[Union[int, str]]] = None
    all_notifications: bool = False 