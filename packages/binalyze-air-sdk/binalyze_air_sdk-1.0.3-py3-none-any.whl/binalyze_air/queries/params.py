"""
Params queries for the Binalyze AIR SDK.
"""

from typing import List, Dict, Any, Union

from ..base import Query
from ..models.params import (
    AcquisitionArtifact, EDiscoveryPattern, AcquisitionEvidence, DroneAnalyzer,
    AcquisitionArtifactsResponse, EDiscoveryCategory, AcquisitionEvidencesResponse,
    MitreAttackTactic, MitreAttackTechnique, MitreAttackResponse
)
from ..http_client import HTTPClient


class GetAcquisitionArtifactsQuery(Query[List[AcquisitionArtifact]]):
    """Query to get acquisition artifacts."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> List[AcquisitionArtifact]:
        """Execute the query to get acquisition artifacts."""
        response: Dict[str, Any] = self.http_client.get("params/acquisition/artifacts")
        
        # Parse using Pydantic models
        artifacts_response = AcquisitionArtifactsResponse.model_validate(response)
        
        # Flatten the structure into a single list
        all_artifacts = []
        
        # Process all platforms
        for platform_name, groups in [
            ("windows", artifacts_response.windows),
            ("linux", artifacts_response.linux),
            ("macos", artifacts_response.macos),
            ("aix", artifacts_response.aix)
        ]:
            for group in groups:
                for artifact in group.items:
                    artifact.group = group.group
                    artifact.platform = platform_name
                    all_artifacts.append(artifact)
        
        return all_artifacts


class GetEDiscoveryPatternsQuery(Query[List[EDiscoveryPattern]]):
    """Query to get e-discovery patterns."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> List[EDiscoveryPattern]:
        """Execute the query to get e-discovery patterns."""
        response = self.http_client.get("params/acquisition/e-discovery-patterns")
        
        # Extract the result array from the API response
        if isinstance(response, dict) and "result" in response:
            categories_data = response["result"]
        else:
            # Fallback for direct array response
            categories_data = response
        
        # Parse using Pydantic models
        categories = [EDiscoveryCategory.model_validate(item) for item in categories_data]
        
        # Flatten the structure into a single list
        all_patterns = []
        for category in categories:
            for pattern in category.applications:
                pattern.category = category.category
                all_patterns.append(pattern)
        
        return all_patterns


class GetAcquisitionEvidencesQuery(Query[List[AcquisitionEvidence]]):
    """Query to get acquisition evidences."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> List[AcquisitionEvidence]:
        """Execute the query to get acquisition evidences."""
        response: Dict[str, Any] = self.http_client.get("params/acquisition/evidences")
        
        # Parse using Pydantic models
        evidences_response = AcquisitionEvidencesResponse.model_validate(response)
        
        # Flatten the structure into a single list
        all_evidences = []
        
        # Process all platforms
        for platform_name, groups in [
            ("windows", evidences_response.windows),
            ("linux", evidences_response.linux),
            ("macos", evidences_response.macos),
            ("aix", evidences_response.aix)
        ]:
            for group in groups:
                for evidence in group.items:
                    evidence.group = group.group
                    evidence.platform = platform_name
                    all_evidences.append(evidence)
        
        return all_evidences


class GetDroneAnalyzersQuery(Query[List[DroneAnalyzer]]):
    """Query to get drone analyzers."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> List[DroneAnalyzer]:
        """Execute the query to get drone analyzers."""
        response = self.http_client.get("params/drone/analyzers")
        
        # Extract the result array from the API response
        if isinstance(response, dict) and "result" in response:
            analyzers_data = response["result"]
        else:
            # Fallback for direct array response
            analyzers_data = response
        
        # Parse using Pydantic models with automatic field mapping
        analyzers = [DroneAnalyzer.model_validate(item) for item in analyzers_data]
        
        return analyzers


class GetMitreAttackTacticsQuery(Query[List[MitreAttackTactic]]):
    """Query to get MITRE ATT&CK tactics."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    def execute(self) -> List[MitreAttackTactic]:
        """Execute the query to get MITRE ATT&CK tactics."""
        response = self.http_client.get("params/mitre-attack/tactics")
        
        # Extract the result from the API response
        if isinstance(response, dict) and "result" in response:
            mitre_data = response["result"]
        else:
            # Fallback for direct response
            mitre_data = response
        
        # Parse using Pydantic models
        mitre_response = MitreAttackResponse.model_validate(mitre_data)
        
        # Return only the tactics as a list
        return list(mitre_response.tactics.values()) 