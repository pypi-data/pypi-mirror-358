"""
Params API for the Binalyze AIR SDK.
"""

from typing import List

from ..http_client import HTTPClient
from ..models.params import AcquisitionArtifact, EDiscoveryPattern, AcquisitionEvidence, DroneAnalyzer, MitreAttackTactic
from ..queries.params import (
    GetAcquisitionArtifactsQuery, GetEDiscoveryPatternsQuery, 
    GetAcquisitionEvidencesQuery, GetDroneAnalyzersQuery, GetMitreAttackTacticsQuery
)


class ParamsAPI:
    """Params API with CQRS pattern - read-only operations for parameters."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations only - params are read-only)
    def get_acquisition_artifacts(self) -> List[AcquisitionArtifact]:
        """Get available acquisition artifacts."""
        query = GetAcquisitionArtifactsQuery(self.http_client)
        return query.execute()
    
    def get_ediscovery_patterns(self) -> List[EDiscoveryPattern]:
        """Get available e-discovery patterns."""
        query = GetEDiscoveryPatternsQuery(self.http_client)
        return query.execute()
    
    def get_acquisition_evidences(self) -> List[AcquisitionEvidence]:
        """Get available acquisition evidence types."""
        query = GetAcquisitionEvidencesQuery(self.http_client)
        return query.execute()
    
    def get_drone_analyzers(self) -> List[DroneAnalyzer]:
        """Get available drone analyzers."""
        query = GetDroneAnalyzersQuery(self.http_client)
        return query.execute()
    
    def get_mitre_attack_tactics(self) -> List[MitreAttackTactic]:
        """Get available MITRE ATT&CK tactics."""
        query = GetMitreAttackTacticsQuery(self.http_client)
        return query.execute() 