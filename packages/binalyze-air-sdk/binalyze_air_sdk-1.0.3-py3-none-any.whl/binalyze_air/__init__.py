"""
Binalyze AIR Python SDK

A comprehensive Python SDK for interacting with the Binalyze AIR API using CQRS architecture.
"""

from .client import AIRClient
from .config import AIRConfig
from .exceptions import (
    AIRAPIError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
)

# Export commonly used models
from .models import (
    # Assets
    Asset, AssetDetail, AssetTask, AssetFilter, AssetTaskFilter,
    # Cases
    Case, CaseActivity, CaseEndpoint, CaseTask, User, CaseFilter, CaseActivityFilter,
    CreateCaseRequest, UpdateCaseRequest, CaseStatus,
    # Tasks
    Task, TaskFilter, TaskStatus, TaskType,
    # Acquisitions
    AcquisitionProfile, AcquisitionProfileDetails, AcquisitionFilter,
    AcquisitionTaskRequest, ImageAcquisitionTaskRequest, CreateAcquisitionProfileRequest,
    AuditLog, AuditFilter, AuditLogsFilter, AuditSummary, AuditUserActivity, AuditSystemEvent,
)

__version__ = "1.0.1"
__all__ = [
    # Core classes
    "AIRClient",
    "AIRConfig",

    # Exceptions
    "AIRAPIError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",

    # Asset models
    "Asset",
    "AssetDetail",
    "AssetTask",
    "AssetFilter",
    "AssetTaskFilter",

    # Case models
    "Case",
    "CaseActivity",
    "CaseEndpoint",
    "CaseTask",
    "User",
    "CaseFilter",
    "CaseActivityFilter",
    "CreateCaseRequest",
    "UpdateCaseRequest",
    "CaseStatus",

    # Task models
    "Task",
    "TaskFilter",
    "TaskStatus",
    "TaskType",

    # Acquisition models
    "AcquisitionProfile",
    "AcquisitionProfileDetails",
    "AcquisitionFilter",
    "AcquisitionTaskRequest",
    "ImageAcquisitionTaskRequest",
    "CreateAcquisitionProfileRequest",
]
