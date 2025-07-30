"""
Evidences/Repositories-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.evidences import (
    EvidenceRepository, AmazonS3Repository, AzureStorageRepository,
    FTPSRepository, SFTPRepository, SMBRepository, RepositoryFilter
)
from ..http_client import HTTPClient


class ListRepositoriesQuery(Query[List[EvidenceRepository]]):
    """Query to list evidence repositories."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[RepositoryFilter] = None, organization_ids: Optional[List[int]] = None):
        self.http_client = http_client
        self.filter_params = filter_params
        self.organization_ids = organization_ids or [0]
    
    def execute(self) -> List[EvidenceRepository]:
        """Execute the list repositories query."""
        params = {}
        if self.filter_params:
            params = self.filter_params.to_params()
        else:
            # Add required organization IDs filter if no filter provided
            params["filter[organizationIds]"] = ",".join(map(str, self.organization_ids))
        
        # Ensure consistent sorting to match API defaults
        if "sortBy" not in params:
            params["sortBy"] = "createdAt"
        if "sortType" not in params:
            params["sortType"] = "ASC"
        
        response = self.http_client.get("evidences/repositories", params=params)
        
        if response.get("success"):
            repositories_data = response.get("result", {}).get("entities", [])
            
            # Use Pydantic parsing with proper field aliasing
            repositories = []
            for repo_data in repositories_data:
                repositories.append(EvidenceRepository.model_validate(repo_data))
            
            return repositories
        
        return []


class GetRepositoryQuery(Query[EvidenceRepository]):
    """Query to get evidence repository by ID."""
    
    def __init__(self, http_client: HTTPClient, repository_id: str):
        self.http_client = http_client
        self.repository_id = repository_id
    
    def execute(self) -> EvidenceRepository:
        """Execute the get repository query."""
        response = self.http_client.get(f"evidences/repositories/{self.repository_id}")
        
        if response.get("success"):
            repository_data = response.get("result", {})
            
            # Use Pydantic parsing with proper field aliasing
            return EvidenceRepository.model_validate(repository_data)
        
        raise Exception(f"Evidence repository not found: {self.repository_id}")


# Amazon S3 Repository Queries

class ListAmazonS3RepositoriesQuery(Query[List[AmazonS3Repository]]):
    """Query to list Amazon S3 repositories."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[RepositoryFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> List[AmazonS3Repository]:
        """Execute the list Amazon S3 repositories query."""
        params = {}
        if self.filter_params:
            params = self.filter_params.model_dump(exclude_none=True)
        
        response = self.http_client.get("evidences/repositories/amazon-s3", params=params)
        
        if response.get("success"):
            repositories_data = response.get("result", {}).get("entities", [])
            return [AmazonS3Repository(**repo) for repo in repositories_data]
        
        return []


class GetAmazonS3RepositoryQuery(Query[AmazonS3Repository]):
    """Query to get Amazon S3 repository by ID."""
    
    def __init__(self, http_client: HTTPClient, repository_id: str):
        self.http_client = http_client
        self.repository_id = repository_id
    
    def execute(self) -> AmazonS3Repository:
        """Execute the get Amazon S3 repository query."""
        response = self.http_client.get(f"evidences/repositories/amazon-s3/{self.repository_id}")
        
        if response.get("success"):
            repository_data = response.get("result", {})
            return AmazonS3Repository(**repository_data)
        
        raise Exception(f"Amazon S3 repository not found: {self.repository_id}")


# Azure Storage Repository Queries

class ListAzureStorageRepositoriesQuery(Query[List[AzureStorageRepository]]):
    """Query to list Azure Storage repositories."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[RepositoryFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> List[AzureStorageRepository]:
        """Execute the list Azure Storage repositories query."""
        params = {}
        if self.filter_params:
            params = self.filter_params.model_dump(exclude_none=True)
        
        response = self.http_client.get("evidences/repositories/azure-storage", params=params)
        
        if response.get("success"):
            repositories_data = response.get("result", {}).get("entities", [])
            return [AzureStorageRepository(**repo) for repo in repositories_data]
        
        return []


class GetAzureStorageRepositoryQuery(Query[AzureStorageRepository]):
    """Query to get Azure Storage repository by ID."""
    
    def __init__(self, http_client: HTTPClient, repository_id: str):
        self.http_client = http_client
        self.repository_id = repository_id
    
    def execute(self) -> AzureStorageRepository:
        """Execute the get Azure Storage repository query."""
        response = self.http_client.get(f"evidences/repositories/azure-storage/{self.repository_id}")
        
        if response.get("success"):
            repository_data = response.get("result", {})
            return AzureStorageRepository(**repository_data)
        
        raise Exception(f"Azure Storage repository not found: {self.repository_id}")


# FTPS Repository Queries

class ListFTPSRepositoriesQuery(Query[List[FTPSRepository]]):
    """Query to list FTPS repositories."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[RepositoryFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> List[FTPSRepository]:
        """Execute the list FTPS repositories query."""
        params = {}
        if self.filter_params:
            params = self.filter_params.model_dump(exclude_none=True)
        
        response = self.http_client.get("evidences/repositories/ftps", params=params)
        
        if response.get("success"):
            repositories_data = response.get("result", {}).get("entities", [])
            return [FTPSRepository(**repo) for repo in repositories_data]
        
        return []


class GetFTPSRepositoryQuery(Query[FTPSRepository]):
    """Query to get FTPS repository by ID."""
    
    def __init__(self, http_client: HTTPClient, repository_id: str):
        self.http_client = http_client
        self.repository_id = repository_id
    
    def execute(self) -> FTPSRepository:
        """Execute the get FTPS repository query."""
        response = self.http_client.get(f"evidences/repositories/ftps/{self.repository_id}")
        
        if response.get("success"):
            repository_data = response.get("result", {})
            return FTPSRepository(**repository_data)
        
        raise Exception(f"FTPS repository not found: {self.repository_id}")


# SFTP Repository Queries

class ListSFTPRepositoriesQuery(Query[List[SFTPRepository]]):
    """Query to list SFTP repositories."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[RepositoryFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> List[SFTPRepository]:
        """Execute the list SFTP repositories query."""
        params = {}
        if self.filter_params:
            params = self.filter_params.model_dump(exclude_none=True)
        
        response = self.http_client.get("evidences/repositories/sftp", params=params)
        
        if response.get("success"):
            repositories_data = response.get("result", {}).get("entities", [])
            return [SFTPRepository(**repo) for repo in repositories_data]
        
        return []


class GetSFTPRepositoryQuery(Query[SFTPRepository]):
    """Query to get SFTP repository by ID."""
    
    def __init__(self, http_client: HTTPClient, repository_id: str):
        self.http_client = http_client
        self.repository_id = repository_id
    
    def execute(self) -> SFTPRepository:
        """Execute the get SFTP repository query."""
        response = self.http_client.get(f"evidences/repositories/sftp/{self.repository_id}")
        
        if response.get("success"):
            repository_data = response.get("result", {})
            return SFTPRepository(**repository_data)
        
        raise Exception(f"SFTP repository not found: {self.repository_id}")


# SMB Repository Queries

class ListSMBRepositoriesQuery(Query[List[SMBRepository]]):
    """Query to list SMB repositories."""
    
    def __init__(self, http_client: HTTPClient, filter_params: Optional[RepositoryFilter] = None):
        self.http_client = http_client
        self.filter_params = filter_params
    
    def execute(self) -> List[SMBRepository]:
        """Execute the list SMB repositories query."""
        params = {}
        if self.filter_params:
            params = self.filter_params.model_dump(exclude_none=True)
        
        response = self.http_client.get("evidences/repositories/smb", params=params)
        
        if response.get("success"):
            repositories_data = response.get("result", {}).get("entities", [])
            return [SMBRepository(**repo) for repo in repositories_data]
        
        return []


class GetSMBRepositoryQuery(Query[SMBRepository]):
    """Query to get SMB repository by ID."""
    
    def __init__(self, http_client: HTTPClient, repository_id: str):
        self.http_client = http_client
        self.repository_id = repository_id
    
    def execute(self) -> SMBRepository:
        """Execute the get SMB repository query."""
        response = self.http_client.get(f"evidences/repositories/smb/{self.repository_id}")
        
        if response.get("success"):
            repository_data = response.get("result", {})
            return SMBRepository(**repository_data)
        
        raise Exception(f"SMB repository not found: {self.repository_id}") 