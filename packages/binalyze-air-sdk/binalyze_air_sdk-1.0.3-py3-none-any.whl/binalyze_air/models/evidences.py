"""
Evidences/Repositories-related data models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field, field_validator

from ..base import AIRBaseModel, Filter


class EvidenceRepository(AIRBaseModel):
    """Base evidence repository model."""
    
    id: str = Field(alias="_id")
    name: str
    description: Optional[str] = None
    type: str  # "amazon-s3", "azure-storage", "ftps", "sftp", "smb"
    path: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    organization_id: Optional[int] = Field(default=None, alias="organizationId")
    organization_ids: Optional[List[int]] = Field(default=None, alias="organizationIds")
    is_active: bool = Field(default=True, alias="isActive")
    is_default: bool = Field(default=False, alias="isDefault")
    created_at: Optional[datetime] = Field(default=None, alias="createdAt")
    updated_at: Optional[datetime] = Field(default=None, alias="updatedAt")
    created_by: Optional[str] = Field(default=None, alias="createdBy")
    
    @field_validator('organization_id', mode='after')
    @classmethod
    def derive_organization_id(cls, v, info):
        """Derive organization_id from organization_ids if not provided."""
        if v is None and 'organization_ids' in info.data:
            org_ids = info.data['organization_ids']
            if org_ids and len(org_ids) > 0:
                return org_ids[0]
            return 0  # Default to 0 if no organization IDs
        return v


class AmazonS3Repository(AIRBaseModel):
    """Amazon S3 evidence repository model."""
    
    id: str
    name: str
    description: Optional[str] = None
    bucketName: str
    region: str
    accessKeyId: str
    secretAccessKey: str
    prefix: Optional[str] = None
    organizationId: int
    isActive: bool = True
    isDefault: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class CreateAmazonS3RepositoryRequest(AIRBaseModel):
    """Create Amazon S3 repository request model."""
    
    name: str
    description: Optional[str] = None
    bucketName: str
    region: str
    accessKeyId: str
    secretAccessKey: str
    prefix: Optional[str] = None
    organizationId: int
    isDefault: bool = False


class UpdateAmazonS3RepositoryRequest(AIRBaseModel):
    """Update Amazon S3 repository request model."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    bucketName: Optional[str] = None
    region: Optional[str] = None
    accessKeyId: Optional[str] = None
    secretAccessKey: Optional[str] = None
    prefix: Optional[str] = None
    isDefault: Optional[bool] = None


class AzureStorageRepository(AIRBaseModel):
    """Azure Storage evidence repository model."""
    
    id: str
    name: str
    description: Optional[str] = None
    accountName: str
    accountKey: str
    containerName: str
    prefix: Optional[str] = None
    organizationId: int
    isActive: bool = True
    isDefault: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class CreateAzureStorageRepositoryRequest(AIRBaseModel):
    """Create Azure Storage repository request model."""
    
    name: str
    description: Optional[str] = None
    accountName: str
    accountKey: str
    containerName: str
    prefix: Optional[str] = None
    organizationId: int
    isDefault: bool = False


class UpdateAzureStorageRepositoryRequest(AIRBaseModel):
    """Update Azure Storage repository request model."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    accountName: Optional[str] = None
    accountKey: Optional[str] = None
    containerName: Optional[str] = None
    prefix: Optional[str] = None
    isDefault: Optional[bool] = None


class FTPSRepository(AIRBaseModel):
    """FTPS evidence repository model."""
    
    id: str
    name: str
    description: Optional[str] = None
    host: str
    port: int = 21
    username: str
    password: str
    remotePath: Optional[str] = None
    passive: bool = True
    organizationId: int
    isActive: bool = True
    isDefault: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class CreateFTPSRepositoryRequest(AIRBaseModel):
    """Create FTPS repository request model."""
    
    name: str
    description: Optional[str] = None
    host: str
    port: int = 21
    username: str
    password: str
    remotePath: Optional[str] = None
    passive: bool = True
    organizationId: int
    isDefault: bool = False


class UpdateFTPSRepositoryRequest(AIRBaseModel):
    """Update FTPS repository request model."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    remotePath: Optional[str] = None
    passive: Optional[bool] = None
    isDefault: Optional[bool] = None


class SFTPRepository(AIRBaseModel):
    """SFTP evidence repository model."""
    
    id: str
    name: str
    description: Optional[str] = None
    host: str
    port: int = 22
    username: str
    password: Optional[str] = None
    privateKey: Optional[str] = None
    remotePath: Optional[str] = None
    organizationId: int
    isActive: bool = True
    isDefault: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class CreateSFTPRepositoryRequest(AIRBaseModel):
    """Create SFTP repository request model."""
    
    name: str
    description: Optional[str] = None
    host: str
    port: int = 22
    username: str
    password: Optional[str] = None
    privateKey: Optional[str] = None
    remotePath: Optional[str] = None
    organizationId: int
    isDefault: bool = False


class UpdateSFTPRepositoryRequest(AIRBaseModel):
    """Update SFTP repository request model."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    privateKey: Optional[str] = None
    remotePath: Optional[str] = None
    isDefault: Optional[bool] = None


class SMBRepository(AIRBaseModel):
    """SMB evidence repository model."""
    
    id: str
    name: str
    description: Optional[str] = None
    path: str
    username: str
    password: str
    domainName: Optional[str] = None
    organizationId: int
    organizationIds: Optional[List[int]] = None
    isActive: bool = True
    isDefault: bool = False
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class CreateSMBRepositoryRequest(AIRBaseModel):
    """Create SMB repository request model."""
    
    name: str
    description: Optional[str] = None
    path: str
    username: str
    password: str
    domainName: Optional[str] = None
    organizationId: int
    organizationIds: Optional[List[int]] = None
    isDefault: bool = False


class UpdateSMBRepositoryRequest(AIRBaseModel):
    """Update SMB repository request model."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    domainName: Optional[str] = None
    isDefault: Optional[bool] = None


class ValidateRepositoryRequest(AIRBaseModel):
    """Validate repository request model."""
    
    repositoryType: str  # "amazon-s3", "azure-storage", "ftps"
    config: Dict[str, Any]  # Repository-specific configuration
    
    def model_dump(self, **kwargs):
        """Override to ensure path -> repositoryPath mapping in config."""
        data = super().model_dump(**kwargs)
        if 'config' in data and isinstance(data['config'], dict):
            config = data['config']
            if 'path' in config:
                config['repositoryPath'] = config.pop('path')
        return data


class ValidationResult(AIRBaseModel):
    """Repository validation result model."""
    
    isValid: bool
    message: str
    errors: List[str] = []
    warnings: List[str] = []


class RepositoryFilter(Filter):
    """Filter for repository queries."""
    
    name: Optional[str] = None
    type: Optional[str] = None
    organization_id: Optional[int] = None
    organization_ids: Optional[List[int]] = None
    all_organizations: Optional[bool] = None
    path: Optional[str] = None
    username: Optional[str] = None
    host: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    created_by: Optional[str] = None
    
    def to_params(self) -> Dict[str, Any]:
        """Convert filter to API parameters with proper field mapping."""
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
        
        # Filter parameters with proper field mapping
        field_mappings = {
            "search_term": "searchTerm",
            "organization_ids": "organizationIds",
            "organization_id": "organizationIds",  # Map to organizationIds for API
            "all_organizations": "allOrganizations",
            "name": "name",
            "type": "type",
            "path": "path",
            "username": "username",
            "host": "host",
            "is_active": "isActive",
            "is_default": "isDefault",
            "created_by": "createdBy"
        }
        
        # Ensure organizationIds is always provided (required by API)
        org_ids_provided = False
        
        for field_name, field_value in self.model_dump(exclude_none=True).items():
            # Skip pagination/sorting fields as they're handled above
            if field_name in ["page_number", "page_size", "sort_by", "sort_type"]:
                continue
                
            if field_value is not None:
                api_field_name = field_mappings.get(field_name, field_name)
                
                # Special handling for organization_ids - use first ID for organizationIds filter
                if field_name == "organization_ids" and isinstance(field_value, list) and len(field_value) > 0:
                    params[f"filter[{api_field_name}]"] = ",".join([str(x) for x in field_value])
                    org_ids_provided = True
                elif field_name == "organization_id":
                    params[f"filter[organizationIds]"] = str(field_value)
                    org_ids_provided = True
                elif isinstance(field_value, list):
                    params[f"filter[{api_field_name}]"] = ",".join([str(x) for x in field_value])
                else:
                    params[f"filter[{api_field_name}]"] = str(field_value)
        
        # API requires organizationIds - provide default if not set
        if not org_ids_provided:
            params["filter[organizationIds]"] = "0"
        
        return params 