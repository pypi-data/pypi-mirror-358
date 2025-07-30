"""
Main client for the Binalyze AIR SDK using CQRS architecture.
"""

import os
from typing import List, Optional, Union, Dict, Any
from datetime import datetime

from .config import AIRConfig
from .http_client import HTTPClient

# Import models
from .models.assets import Asset, AssetDetail, AssetTask, AssetFilter, AssetTaskFilter
from .models.cases import (
    Case, CaseActivity, CaseEndpoint, CaseTask, User, CaseFilter, CaseActivityFilter,
    CreateCaseRequest, UpdateCaseRequest, CaseNote, CaseEndpointFilter, CaseTaskFilter, CaseUserFilter
)
from .models.tasks import Task, TaskFilter, TaskAssignment
from .models.acquisitions import (
    AcquisitionProfile, AcquisitionProfileDetails, AcquisitionFilter,
    AcquisitionTaskRequest, ImageAcquisitionTaskRequest, CreateAcquisitionProfileRequest
)
from .models.policies import (
    Policy, PolicyAssignment, PolicyExecution, PolicyFilter,
    CreatePolicyRequest, UpdatePolicyRequest, AssignPolicyRequest
)
from .models.organizations import (
    Organization, OrganizationUser, OrganizationRole, OrganizationLicense,
    OrganizationSettings, OrganizationFilter, CreateOrganizationRequest,
    UpdateOrganizationRequest, AddUserToOrganizationRequest, OrganizationsPaginatedResponse,
    OrganizationUsersPaginatedResponse
)
from .models.triage import (
    TriageRule, TriageTag,
    TriageFilter, CreateTriageRuleRequest, UpdateTriageRuleRequest,
    CreateTriageTagRequest, CreateTriageProfileRequest
)
from .models.audit import (
    AuditLog, AuditSummary, AuditUserActivity, AuditSystemEvent,
    AuditRetentionPolicy, AuditFilter, AuditLogsFilter, AuditLevel
)
from .models.baseline import (
    Baseline, BaselineProfile, BaselineComparison, BaselineSchedule,
    BaselineFilter, CreateBaselineRequest, UpdateBaselineRequest,
    CreateBaselineProfileRequest, CompareBaselineRequest
)
from .models.auth import (
    AuthStatus, LoginRequest, LoginResponse
)
from .models.user_management import (
    UserManagementUser, CreateUserRequest, UpdateUserRequest,
    AIUser, CreateAIUserRequest, APIUser, CreateAPIUserRequest, UserFilter
)
from .models.evidence import (
    EvidencePPC, EvidenceReportFileInfo, EvidenceReport
)
from .models.auto_asset_tags import (
    AutoAssetTag, CreateAutoAssetTagRequest, UpdateAutoAssetTagRequest,
    StartTaggingRequest, TaggingResult, AutoAssetTagFilter
)
from .models.evidences import (
    EvidenceRepository, AmazonS3Repository, AzureStorageRepository,
    FTPSRepository, SFTPRepository, SMBRepository, RepositoryFilter,
    CreateAmazonS3RepositoryRequest, UpdateAmazonS3RepositoryRequest,
    CreateAzureStorageRepositoryRequest, UpdateAzureStorageRepositoryRequest,
    CreateFTPSRepositoryRequest, UpdateFTPSRepositoryRequest,
    CreateSFTPRepositoryRequest, UpdateSFTPRepositoryRequest,
    CreateSMBRepositoryRequest, UpdateSMBRepositoryRequest,
    ValidateRepositoryRequest, ValidationResult
)
from .models.event_subscription import (
    EventSubscription, EventSubscriptionFilter, CreateEventSubscriptionRequest,
    UpdateEventSubscriptionRequest
)
from .models.interact import (
    ShellInteraction, AssignShellTaskRequest, ShellTaskResponse
)
from .models.params import (
    AcquisitionArtifact, EDiscoveryPattern, AcquisitionEvidence, DroneAnalyzer
)
from .models.settings import (
    BannerSettings, UpdateBannerSettingsRequest
)
from .models.license import (
    License, LicenseUpdateRequest
)
from .models.logger import (
    LogDownloadRequest, LogDownloadResponse
)
from .models.multipart_upload import (
    UploadInitializeRequest, UploadInitializeResponse, UploadPartRequest, UploadPartResponse,
    UploadStatusRequest, UploadStatusResponse, UploadFinalizeRequest, UploadFinalizeResponse,
    MultipartUploadSession, FileChunker
)

# Import ALL API classes from their separate files
from .apis.assets import AssetsAPI
from .apis.cases import CasesAPI
from .apis.tasks import TasksAPI
from .apis.acquisitions import AcquisitionsAPI
from .apis.policies import PoliciesAPI
from .apis.organizations import OrganizationsAPI
from .apis.triage import TriageAPI
from .apis.audit_logs import AuditAPI
from .apis.baseline import BaselineAPI
from .apis.auth import AuthAPI
from .apis.evidence import EvidenceAPI
from .apis.auto_asset_tags import AutoAssetTagsAPI
from .apis.event_subscription import EventSubscriptionAPI
from .apis.interact import InteractAPI
from .apis.params import ParamsAPI
from .apis.settings import SettingsAPI
from .apis.webhooks import WebhookAPI
from .apis.api_tokens import APITokensAPI
from .apis.investigation_hub import InvestigationHubAPI
from .apis.cloud_forensics import CloudForensicsAPI
from .apis.backup import BackupAPI
from .apis.license import LicenseAPI
from .apis.logger import LoggerAPI
from .apis.multipart_upload import MultipartUploadAPI
from .apis.notifications import NotificationsAPI
from .apis.preset_filters import PresetFiltersAPI
from .apis.recent_activities import RecentActivitiesAPI
from .apis.relay_server import RelayServerAPI
from .apis.webhook_executions import WebhookExecutionsAPI
from .apis.user_management import UserManagementAPI


class AIRClient:
    """Main client for the Binalyze AIR API using CQRS architecture."""
    
    def __init__(
        self,
        host: Optional[str] = None,
        api_token: Optional[str] = None,
        organization_id: Optional[int] = None,
        config_file: Optional[str] = None,
        config: Optional[AIRConfig] = None,
        **kwargs
    ):
        """
        Initialize the AIR client.
        
        Args:
            host: AIR instance host URL
            api_token: API token for authentication
            organization_id: Default organization ID
            config_file: Path to configuration file
            config: Pre-configured AIRConfig instance
            **kwargs: Additional configuration options
        """
        if config:
            self.config = config
        else:
            self.config = AIRConfig.create(
                host=host,
                api_token=api_token,
                organization_id=organization_id,
                config_file=config_file,
                **kwargs
            )
        
        self.http_client = HTTPClient(self.config)
        
        # Initialize API sections using CQRS pattern - ALL FROM SEPARATE FILES
        self.assets = AssetsAPI(self.http_client)
        self.cases = CasesAPI(self.http_client)
        self.tasks = TasksAPI(self.http_client)
        self.acquisitions = AcquisitionsAPI(self.http_client)
        self.policies = PoliciesAPI(self.http_client)
        self.organizations = OrganizationsAPI(self.http_client)
        self.triage = TriageAPI(self.http_client)
        self.audit = AuditAPI(self.http_client)
        self.baseline = BaselineAPI(self.http_client)
        
        # Additional API sections
        self.auth = AuthAPI(self.http_client)
        self.user_management = UserManagementAPI(self.http_client)
        self.evidence = EvidenceAPI(self.http_client)
        self.auto_asset_tags = AutoAssetTagsAPI(self.http_client)
        self.event_subscription = EventSubscriptionAPI(self.http_client)
        self.interact = InteractAPI(self.http_client)
        self.params = ParamsAPI(self.http_client)
        self.settings = SettingsAPI(self.http_client)
        self.webhooks = WebhookAPI(self.http_client)
        self.api_tokens = APITokensAPI(self.http_client)
        self.investigation_hub = InvestigationHubAPI(self.http_client)
        self.cloud_forensics = CloudForensicsAPI(self.http_client)
        self.backup = BackupAPI(self.http_client)
        self.license = LicenseAPI(self.http_client)
        self.logger = LoggerAPI(self.http_client)
        self.multipart_upload = MultipartUploadAPI(self.http_client)
        self.notifications = NotificationsAPI(self.http_client)
        self.preset_filters = PresetFiltersAPI(self.http_client)
        self.recent_activities = RecentActivitiesAPI(self.http_client)
        self.relay_server = RelayServerAPI(self.http_client)
        self.webhook_executions = WebhookExecutionsAPI(self.http_client)
    
    def test_connection(self) -> bool:
        """Test the connection to AIR API."""
        try:
            # Try to check authentication as a simple test
            self.auth.check_status()
            return True
        except Exception:
            return False
    
    @classmethod
    def from_environment(cls) -> "AIRClient":
        """Create client from environment variables."""
        config = AIRConfig.from_environment()
        return cls(config=config)
    
    @classmethod
    def from_config_file(cls, config_path: str = ".air_config.json") -> "AIRClient":
        """Create client from configuration file."""
        config = AIRConfig.from_file(config_path)
        return cls(config=config) 