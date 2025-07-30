"""
Command implementations for the Binalyze AIR SDK (CQRS pattern).
"""

from .assets import (
    IsolateAssetsCommand,
    UnisolateAssetsCommand,
    RebootAssetsCommand,
    ShutdownAssetsCommand,
    AddTagsToAssetsCommand,
    RemoveTagsFromAssetsCommand,
    UninstallAssetsCommand,
    DeleteAssetTagByIdCommand,
    DeleteAssetTagsByOrganizationIdCommand,
)
from .cases import (
    CreateCaseCommand,
    UpdateCaseCommand,
    CloseCaseCommand,
    OpenCaseCommand,
    ArchiveCaseCommand,
    ChangeCaseOwnerCommand,
    RemoveEndpointsFromCaseCommand,
    RemoveTaskAssignmentFromCaseCommand,
    ImportTaskAssignmentsToCaseCommand,
)
from .tasks import (
    CancelTaskCommand,
    CancelTaskAssignmentCommand,
    DeleteTaskAssignmentCommand,
    DeleteTaskCommand,
    CancelTaskByFilterCommand,
    GenerateOffNetworkZipPasswordCommand,
)
from .acquisitions import (
    AssignAcquisitionTaskCommand,
    AssignImageAcquisitionTaskCommand,
    CreateAcquisitionProfileCommand,
    UpdateAcquisitionProfileCommand,
    DeleteAcquisitionProfileCommand,
    CreateOffNetworkAcquisitionCommand,
    UpdateScheduledEvidenceAcquisitionCommand,
    UpdateScheduledImageAcquisitionCommand,
    ValidateOsqueryCommand,
)
from .policies import (
    CreatePolicyCommand,
    UpdatePolicyCommand,
    DeletePolicyCommand,
    ActivatePolicyCommand,
    DeactivatePolicyCommand,
    AssignPolicyCommand,
    UnassignPolicyCommand,
    ExecutePolicyCommand,
)
from .organizations import (
    CreateOrganizationCommand,
    UpdateOrganizationCommand,
    UpdateOrganizationSettingsCommand,
)
from .triage import (
    CreateTriageRuleCommand,
    UpdateTriageRuleCommand,
    DeleteTriageRuleCommand,
    EnableTriageRuleCommand,
    CreateTriageTagCommand,
)
from .baseline import (
    AcquireBaselineByFilterCommand,
    CompareBaselineByEndpointCommand,
)
from .user_management import (
    CreateUserCommand,
    UpdateUserCommand,
    DeleteUserCommand,
    CreateAIUserCommand,
    CreateAPIUserCommand,
    ChangeCurrentUserPasswordCommand,
    SetAPIUserPasswordCommand,
    ResetPasswordCommand,
    ResetTFACommand,
    CreateRoleCommand,
    UpdateRoleCommand,
    DeleteRoleCommand,
    CreateUserGroupCommand,
    UpdateUserGroupCommand,
    DeleteUserGroupCommand,
)

# TODO: Add imports when implementing other endpoints  

__all__ = [
    # Asset commands
    "IsolateAssetsCommand",
    "UnisolateAssetsCommand", 
    "RebootAssetsCommand",
    "ShutdownAssetsCommand",
    "AddTagsToAssetsCommand",
    "RemoveTagsFromAssetsCommand",
    "UninstallAssetsCommand",
    "DeleteAssetTagByIdCommand",
    "DeleteAssetTagsByOrganizationIdCommand",
    
    # Case commands
    "CreateCaseCommand",
    "UpdateCaseCommand",
    "CloseCaseCommand",
    "OpenCaseCommand",
    "ArchiveCaseCommand",
    "ChangeCaseOwnerCommand",
    "RemoveEndpointsFromCaseCommand",
    "RemoveTaskAssignmentFromCaseCommand",
    "ImportTaskAssignmentsToCaseCommand",
    
    # Task commands
    "CancelTaskCommand",
    "CancelTaskAssignmentCommand",
    "DeleteTaskAssignmentCommand",
    "DeleteTaskCommand",
    "CancelTaskByFilterCommand",
    "GenerateOffNetworkZipPasswordCommand",
    
    # Acquisition commands
    "AssignAcquisitionTaskCommand",
    "AssignImageAcquisitionTaskCommand",
    "CreateAcquisitionProfileCommand",
    "UpdateAcquisitionProfileCommand",
    "DeleteAcquisitionProfileCommand",
    "CreateOffNetworkAcquisitionCommand",
    "UpdateScheduledEvidenceAcquisitionCommand",
    "UpdateScheduledImageAcquisitionCommand",
    "ValidateOsqueryCommand",
    
    # Policy commands
    "CreatePolicyCommand",
    "UpdatePolicyCommand",
    "DeletePolicyCommand",
    "ActivatePolicyCommand",
    "DeactivatePolicyCommand",
    "AssignPolicyCommand",
    "UnassignPolicyCommand",
    "ExecutePolicyCommand",
    
    # Organization commands
    "CreateOrganizationCommand",
    "UpdateOrganizationCommand",
    "UpdateOrganizationSettingsCommand",
    
    # Triage commands
    "CreateTriageRuleCommand",
    "UpdateTriageRuleCommand",
    "DeleteTriageRuleCommand",
    "EnableTriageRuleCommand",
    "CreateTriageTagCommand",
    
    # Baseline commands
    "AcquireBaselineByFilterCommand",
    "CompareBaselineByEndpointCommand",
    
    # User Management commands
    "CreateUserCommand",
    "UpdateUserCommand",
    "DeleteUserCommand",
    "CreateAIUserCommand",
    "CreateAPIUserCommand",
    "ChangeCurrentUserPasswordCommand",
    "SetAPIUserPasswordCommand",
    "ResetPasswordCommand",
    "ResetTFACommand",
    "CreateRoleCommand",
    "UpdateRoleCommand",
    "DeleteRoleCommand",
    "CreateUserGroupCommand",
    "UpdateUserGroupCommand",
    "DeleteUserGroupCommand",
] 