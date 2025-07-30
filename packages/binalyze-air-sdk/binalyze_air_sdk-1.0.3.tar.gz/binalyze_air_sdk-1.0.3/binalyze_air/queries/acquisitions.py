"""
Acquisition-related queries for the Binalyze AIR SDK.
"""

from typing import List, Optional

from ..base import Query
from ..models.acquisitions import (
    AcquisitionProfile, AcquisitionProfileDetails, AcquisitionFilter,
    AcquisitionProfilePlatformDetails, NetworkCaptureConfig, EDiscoveryPattern
)
from ..http_client import HTTPClient


class ListAcquisitionProfilesQuery(Query[List[AcquisitionProfile]]):
    """Query to list acquisition profiles with optional filtering."""
    
    def __init__(
        self, 
        http_client: HTTPClient, 
        filter_params: Optional[AcquisitionFilter] = None,
        organization_ids: Optional[List[int]] = None,
        all_organizations: bool = False
    ):
        self.http_client = http_client
        # Initialize filter with default organization IDs if not provided
        if filter_params is None:
            filter_params = AcquisitionFilter()
        
        # Set organization parameters if not already set in filter
        if filter_params.organization_ids is None and organization_ids is not None:
            filter_params.organization_ids = organization_ids
        elif filter_params.organization_ids is None:
            filter_params.organization_ids = [0]  # Default to organization 0
        
        # Set all_organizations parameter if not already set in filter
        if filter_params.all_organizations is None and all_organizations:
            filter_params.all_organizations = all_organizations
        
        self.filter_params = filter_params
    
    def execute(self) -> List[AcquisitionProfile]:
        """Execute the query to list acquisition profiles."""
        # Use filter's parameter generation
        params = self.filter_params.to_params()
        
        response = self.http_client.get("acquisitions/profiles", params=params)
        
        entities = response.get("result", {}).get("entities", [])
        
        # Convert to AcquisitionProfile objects
        profiles = []
        for entity_data in entities:
            mapped_data = {
                "id": entity_data.get("_id"),
                "name": entity_data.get("name"),
                "organization_ids": entity_data.get("organizationIds", []),  # Keep as integers
                "created_at": entity_data.get("createdAt"),
                "updated_at": entity_data.get("updatedAt"),
                "created_by": entity_data.get("createdBy"),
                "deletable": entity_data.get("deletable", True),
                "average_time": entity_data.get("averageTime"),
                "last_used_at": entity_data.get("lastUsedAt"),
                "last_used_by": entity_data.get("lastUsedBy"),
                "has_event_log_records_evidence": entity_data.get("hasEventLogRecordsEvidence"),
            }
            
            # Remove None values
            mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
            
            profiles.append(AcquisitionProfile(**mapped_data))
        
        return profiles


class GetAcquisitionProfileQuery(Query[AcquisitionProfileDetails]):
    """Query to get a specific acquisition profile by ID."""
    
    def __init__(self, http_client: HTTPClient, profile_id: str):
        self.http_client = http_client
        self.profile_id = profile_id
    
    def execute(self) -> AcquisitionProfileDetails:
        """Execute the query to get acquisition profile details."""
        response = self.http_client.get(f"acquisitions/profiles/{self.profile_id}")
        
        entity_data = response.get("result", {})
        
        # Parse platform configurations
        def parse_platform_config(platform_data: dict) -> AcquisitionProfilePlatformDetails:
            network_capture = None
            if "networkCapture" in platform_data:
                nc_data = platform_data["networkCapture"]
                network_capture = NetworkCaptureConfig(
                    enabled=nc_data.get("enabled", False),
                    duration=nc_data.get("duration", 60),
                    pcap=nc_data.get("pcap", {"enabled": False}),
                    network_flow=nc_data.get("networkFlow", {"enabled": False})
                )
            
            return AcquisitionProfilePlatformDetails(
                evidence_list=platform_data.get("evidenceList", []),
                artifact_list=platform_data.get("artifactList"),
                custom_content_profiles=platform_data.get("customContentProfiles", []),
                network_capture=network_capture
            )
        
        # Parse platform configurations
        windows_config = None
        linux_config = None
        macos_config = None
        aix_config = None
        
        if "windows" in entity_data:
            windows_config = parse_platform_config(entity_data["windows"])
        
        if "linux" in entity_data:
            linux_config = parse_platform_config(entity_data["linux"])
        
        if "macos" in entity_data:
            macos_config = parse_platform_config(entity_data["macos"])
        
        if "aix" in entity_data:
            aix_config = parse_platform_config(entity_data["aix"])
        
        # Parse eDiscovery patterns
        e_discovery = None
        if "eDiscovery" in entity_data and "patterns" in entity_data["eDiscovery"]:
            patterns = [
                EDiscoveryPattern(
                    pattern=pattern.get("pattern", ""),
                    category=pattern.get("category", "")
                )
                for pattern in entity_data["eDiscovery"]["patterns"]
            ]
            e_discovery = {"patterns": patterns}
        
        mapped_data = {
            "id": entity_data.get("_id"),
            "name": entity_data.get("name"),
            "organization_ids": [str(org_id) for org_id in entity_data.get("organizationIds", [])],
            "created_at": entity_data.get("createdAt"),
            "updated_at": entity_data.get("updatedAt"),
            "created_by": entity_data.get("createdBy"),
            "deletable": entity_data.get("deletable", True),
            "windows": windows_config,
            "linux": linux_config,
            "macos": macos_config,
            "aix": aix_config,
            "e_discovery": e_discovery,
        }
        
        # Remove None values
        mapped_data = {k: v for k, v in mapped_data.items() if v is not None}
        
        return AcquisitionProfileDetails(**mapped_data) 