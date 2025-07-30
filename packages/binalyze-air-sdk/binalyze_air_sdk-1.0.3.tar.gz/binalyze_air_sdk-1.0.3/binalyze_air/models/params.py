"""
Params API models for the Binalyze AIR SDK.
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import Field

from ..base import AIRBaseModel


class ArtifactType(str, Enum):
    """Acquisition artifact types."""
    FILE = "file"
    REGISTRY = "registry"
    MEMORY = "memory"
    NETWORK = "network"
    PROCESS = "process"
    EVENT_LOG = "event_log"
    PREFETCH = "prefetch"
    BROWSER = "browser"
    SYSTEM = "system"


class ArtifactCategory(str, Enum):
    """Artifact categories."""
    FORENSICS = "forensics"
    MALWARE = "malware"
    NETWORK = "network"
    SYSTEM = "system"
    BROWSER = "browser"
    EMAIL = "email"
    CHAT = "chat"
    CLOUD = "cloud"


class Platform(str, Enum):
    """Supported platforms."""
    WINDOWS = "windows"
    LINUX = "linux"
    DARWIN = "darwin"
    MACOS = "macos"


class AcquisitionArtifact(AIRBaseModel):
    """Acquisition artifact model based on API response structure."""
    
    name: str
    desc: str = Field(alias="desc")
    type: str = Field(alias="type")
    
    # Additional fields for SDK processing
    group: Optional[str] = None
    platform: Optional[str] = None


class EDiscoveryPattern(AIRBaseModel):
    """E-Discovery pattern model based on API response structure."""
    
    name: str
    pattern: str
    
    # Additional fields for SDK processing  
    category: Optional[str] = None


class AcquisitionEvidence(AIRBaseModel):
    """Acquisition evidence model based on API response structure."""
    
    name: str
    desc: str = Field(alias="desc")
    type: str = Field(alias="type")
    
    # Additional fields for SDK processing
    group: Optional[str] = None
    platform: Optional[str] = None


class DroneAnalyzer(AIRBaseModel):
    """Drone analyzer model with proper field mapping."""
    
    id: str = Field(alias="Id")
    name: str = Field(alias="Name")
    default_enabled: bool = Field(alias="DefaultEnabled")
    platforms: List[str] = Field(default=[], alias="Platforms")
    o_ses: List[str] = Field(default=[], alias="OSes")
    
    # Computed properties can be added as methods if needed


# MITRE Attack models
class MitreAttackTactic(AIRBaseModel):
    """MITRE ATT&CK tactic model."""
    
    id: str
    name: str
    url: str


class MitreAttackTechnique(AIRBaseModel):
    """MITRE ATT&CK technique model."""
    
    id: str
    name: str
    url: str
    sub_techniques: Optional[List[str]] = Field(default=[], alias="subTechniques")
    parent_technique: Optional[str] = Field(default=None, alias="parentTechnique")


class MitreAttackResponse(AIRBaseModel):
    """MITRE ATT&CK response structure - matches actual API response format."""
    
    tactics: Dict[str, MitreAttackTactic]
    techniques: Dict[str, MitreAttackTechnique]


# API Response wrapper models for structured responses
class AcquisitionArtifactGroup(AIRBaseModel):
    """Group of acquisition artifacts."""
    
    group: str
    items: List[AcquisitionArtifact]


class AcquisitionArtifactsResponse(AIRBaseModel):
    """Full response structure for acquisition artifacts."""
    
    windows: List[AcquisitionArtifactGroup] = []
    linux: List[AcquisitionArtifactGroup] = []
    macos: List[AcquisitionArtifactGroup] = []
    aix: List[AcquisitionArtifactGroup] = []


class EDiscoveryCategory(AIRBaseModel):
    """E-Discovery pattern category."""
    
    category: str
    applications: List[EDiscoveryPattern]


class AcquisitionEvidenceGroup(AIRBaseModel):
    """Group of acquisition evidences."""
    
    group: str  
    items: List[AcquisitionEvidence]


class AcquisitionEvidencesResponse(AIRBaseModel):
    """Full response structure for acquisition evidences."""
    
    windows: List[AcquisitionEvidenceGroup] = []
    linux: List[AcquisitionEvidenceGroup] = []
    macos: List[AcquisitionEvidenceGroup] = []
    aix: List[AcquisitionEvidenceGroup] = [] 