"""
Cloud Forensics models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel


class CloudVendor(str, Enum):
    """Cloud vendor enumeration."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"


class CloudAccountStatus(str, Enum):
    """Cloud account status enumeration."""
    CONFIGURED = "configured"
    SYNCING = "syncing"
    FAILED = "failed"


class CloudCredentials(AIRBaseModel):
    """Cloud credentials model."""
    
    access_key_id: Optional[str] = Field(default=None, alias="accessKeyId")
    secret_access_key: Optional[str] = Field(default=None, alias="secretAccessKey")
    # Azure credentials
    tenant_id: Optional[str] = Field(default=None, alias="tenantId")
    client_id: Optional[str] = Field(default=None, alias="clientId")
    client_secret: Optional[str] = Field(default=None, alias="clientSecret")
    # GCP credentials
    service_account_key: Optional[str] = Field(default=None, alias="serviceAccountKey")
    project_id: Optional[str] = Field(default=None, alias="projectId")


class CloudAccount(AIRBaseModel):
    """Cloud account model."""
    
    id: str = Field(alias="_id")
    cloud_vendor: CloudVendor = Field(alias="cloudVendor")
    organization_id: int = Field(alias="organizationId")
    account_id: str = Field(alias="accountId")
    detected_assets_count: int = Field(default=0, alias="detectedAssetsCount")
    status: CloudAccountStatus
    credentials: CloudCredentials
    account_name: str = Field(alias="accountName")
    last_sync_date: Optional[datetime] = Field(default=None, alias="lastSyncDate")
    errors: List[str] = Field(default_factory=list)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")


class CloudAccountFilter(AIRBaseModel):
    """Filter parameters for cloud accounts."""
    
    page_size: Optional[int] = Field(default=10, alias="pageSize")
    page_number: Optional[int] = Field(default=1, alias="pageNumber")
    sort_type: Optional[str] = Field(default="DESC", alias="sortType")  # ASC or DESC
    sort_by: Optional[str] = Field(default="createdAt", alias="sortBy")  # status, cloudVendor, detectedAssetsCount, lastSyncDate, createdAt
    search_term: Optional[str] = Field(default=None, alias="searchTerm")
    cloud_vendor: Optional[CloudVendor] = Field(default=None, alias="cloudVendor")
    status: Optional[CloudAccountStatus] = Field(default=None)
    organization_ids: Optional[List[int]] = Field(default=None, alias="organizationIds")


class CloudAccountsPaginatedResponse(AIRBaseModel):
    """Paginated response for cloud accounts."""
    
    entities: List[CloudAccount]
    filters: List[Dict[str, Any]]
    sortables: List[str]
    total_entity_count: int = Field(alias="totalEntityCount")
    current_page: int = Field(alias="currentPage")
    page_size: int = Field(alias="pageSize")
    previous_page: int = Field(alias="previousPage")
    total_page_count: int = Field(alias="totalPageCount")
    next_page: int = Field(alias="nextPage")


class CreateCloudAccountRequest(AIRBaseModel):
    """Request model for creating cloud accounts."""
    
    cloud_vendor: CloudVendor = Field(alias="cloudVendor")
    account_name: str = Field(alias="accountName")
    credentials: CloudCredentials
    organization_id: int = Field(alias="organizationId")


class UpdateCloudAccountRequest(AIRBaseModel):
    """Request model for updating cloud accounts."""
    
    account_name: Optional[str] = Field(default=None, alias="accountName")
    credentials: Optional[CloudCredentials] = Field(default=None)


class CloudAccountSyncResult(AIRBaseModel):
    """Cloud account sync result model."""
    
    account_id: str = Field(alias="accountId")
    status: str
    assets_discovered: int = Field(default=0, alias="assetsDiscovered")
    sync_started_at: datetime = Field(alias="syncStartedAt")
    sync_completed_at: Optional[datetime] = Field(default=None, alias="syncCompletedAt")
    errors: List[str] = Field(default_factory=list)


class CloudVendorSyncResult(AIRBaseModel):
    """Cloud vendor sync result model."""
    
    cloud_vendor: Optional[CloudVendor] = Field(default=None, alias="cloudVendor")
    accounts_synced: int = Field(default=0, alias="accountsSynced")
    total_assets_discovered: int = Field(default=0, alias="totalAssetsDiscovered")
    sync_started_at: Optional[datetime] = Field(default=None, alias="syncStartedAt")
    sync_completed_at: Optional[datetime] = Field(default=None, alias="syncCompletedAt")
    account_results: List[CloudAccountSyncResult] = Field(default_factory=list, alias="accountResults")


class CloudAsset(AIRBaseModel):
    """Cloud asset model."""
    
    id: str = Field(alias="_id")
    account_id: str = Field(alias="accountId")
    cloud_vendor: CloudVendor = Field(alias="cloudVendor")
    asset_type: str = Field(alias="assetType")
    asset_name: str = Field(alias="assetName")
    region: Optional[str] = Field(default=None)
    status: str
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    discovered_at: datetime = Field(alias="discoveredAt")
    last_updated: datetime = Field(alias="lastUpdated")


class CloudForensicsExportRequest(AIRBaseModel):
    """Export request model for cloud forensics data."""
    
    format: str = Field(default="csv")  # csv, json, xlsx
    filters: Optional[CloudAccountFilter] = Field(default=None)
    include_credentials: bool = Field(default=False, alias="includeCredentials")
    include_assets: bool = Field(default=False, alias="includeAssets") 