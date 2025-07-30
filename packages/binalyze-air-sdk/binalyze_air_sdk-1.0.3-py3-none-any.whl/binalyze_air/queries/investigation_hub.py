"""
Investigation Hub queries for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any

from ..base import Query
from ..models.investigation_hub import (
    Investigation, InvestigationAsset, FlagSummary, EvidenceSection,
    EvidenceStructure, SQLQueryResult, FindingsSummary, FindingsStructure,
    FindingsResult, FindingsRequest, MitreMatch, InvestigationComment, 
    InvestigationActivity, AdvancedFilter
)
from ..http_client import HTTPClient


class GetInvestigationQuery(Query[Investigation]):
    """Query to get a specific investigation by ID."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> Investigation:
        """Execute the query."""
        response = self.http_client.get(f"investigation-hub/investigations/{self.investigation_id}")
        return Investigation(**response["result"])


class GetInvestigationAssetsQuery(Query[List[InvestigationAsset]]):
    """Query to get assets for a specific investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> List[InvestigationAsset]:
        """Execute the query."""
        response = self.http_client.get(f"investigation-hub/investigations/{self.investigation_id}/assets")
        return [InvestigationAsset(**asset) for asset in response["result"]]


class GetInvestigationFlagSummaryQuery(Query[List[FlagSummary]]):
    """Query to get flag summary for a specific investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> List[FlagSummary]:
        """Execute the query."""
        response = self.http_client.post(f"investigation-hub/investigations/{self.investigation_id}/flags-summary")
        return [FlagSummary(**flag) for flag in response["result"]]


class GetEvidenceSectionsQuery(Query[List[EvidenceSection]]):
    """Query to get evidence sections for a specific investigation with task assignment IDs."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, task_assignment_ids: List[str]):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.task_assignment_ids = task_assignment_ids
    
    def execute(self) -> List[EvidenceSection]:
        """Execute the query."""
        payload = {"taskAssignmentIds": self.task_assignment_ids}
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/sections", 
            json_data=payload
        )
        return [EvidenceSection(**section) for section in response["result"]]


class GetEvidenceStructureQuery(Query[List[EvidenceStructure]]):
    """Query to get evidence structure for a specific section."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, section: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.section = section
    
    def execute(self) -> List[EvidenceStructure]:
        """Execute the query."""
        response = self.http_client.get(
            f"investigation-hub/investigations/{self.investigation_id}/sections/{self.section}/structure"
        )
        return [EvidenceStructure(**structure) for structure in response["result"]]


class ExecuteSQLQuery(Query[SQLQueryResult]):
    """Query to execute SQL against investigation database."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, query: str, 
                 page_size: int = 10, page_number: int = 1):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.query = query
        self.page_size = page_size
        self.page_number = page_number
    
    def execute(self) -> SQLQueryResult:
        """Execute the query."""
        payload = {
            "query": self.query,
            "pageSize": self.page_size,
            "pageNumber": self.page_number
        }
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/execute-sql-query",
            json_data=payload
        )
        return SQLQueryResult(**response["result"])


class GetFindingsSummaryQuery(Query[FindingsSummary]):
    """Query to get findings summary for a specific investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> FindingsSummary:
        """Execute the query."""
        # Use default payload for findings summary
        payload = {
            "take": 50,
            "skip": 0,
            "filter": [],
            "globalFilter": {
                "assignmentIds": [],
                "flagIds": [],
                "verdictScores": [],
                "createdBy": [],
                "mitreTechniqueIds": [],
                "mitreTacticIds": []
            },
            "sort": [{"column": "verdict_score", "order": "desc"}]
        }
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/findings/summary",
            json_data=payload
        )
        return FindingsSummary(**response["result"])


class GetMitreMatchesQuery(Query[List[MitreMatch]]):
    """Query to get MITRE ATT&CK matches for a specific investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> List[MitreMatch]:
        """Execute the query."""
        # Use default payload for MITRE matches
        payload = {
            "take": 50,
            "skip": 0,
            "filter": [],
            "globalFilter": {
                "assignmentIds": [],
                "flagIds": [],
                "verdictScores": [],
                "createdBy": [],
                "mitreTechniqueIds": [],
                "mitreTacticIds": []
            },
            "sort": [{"column": "verdict_score", "order": "desc"}]
        }
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/findings/mitre-matches",
            json_data=payload
        )
        return [MitreMatch(**match) for match in response["result"]]


class GetInvestigationCommentsQuery(Query[List[InvestigationComment]]):
    """Query to get comments for a specific investigation evidence."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 evidence_id: Optional[str] = None):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.evidence_id = evidence_id or "artifacts"  # Default to artifacts if not specified
    
    def execute(self) -> List[InvestigationComment]:
        """Execute the query."""
        # Add optional query parameters from API spec
        params = {
            "taskAssignmentId": "test_task_1",
            "objectId": "1"
        }
        
        response = self.http_client.get(
            f"investigation-hub/investigations/{self.investigation_id}/evidence/{self.evidence_id}/comments",
            params=params
        )
        return [InvestigationComment(**comment) for comment in response["result"]]


class GetInvestigationActivitiesQuery(Query[List[InvestigationActivity]]):
    """Query to get activities for a specific investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str,
                 page_size: int = 20, page_number: int = 1):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.page_size = page_size
        self.page_number = page_number
    
    def execute(self) -> List[InvestigationActivity]:
        """Execute the query."""
        params = {
            "pageSize": self.page_size,
            "pageNumber": self.page_number
        }
        response = self.http_client.get(
            f"investigation-hub/investigations/{self.investigation_id}/activities",
            params=params
        )
        return [InvestigationActivity(**activity) for activity in response["result"]]


class GetAdvancedFiltersQuery(Query[List[AdvancedFilter]]):
    """Query to get advanced filters (organization-wide, not investigation-specific)."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: Optional[str] = None):
        self.http_client = http_client
        # Investigation ID is not needed for this endpoint but kept for compatibility
        self.investigation_id = investigation_id
    
    def execute(self) -> List[AdvancedFilter]:
        """Execute the query."""
        # Add required query parameters from API validation
        params = {
            "organizationId": 0,  # Required parameter
            "tableName": "artifacts"  # Required parameter
        }
        response = self.http_client.get("investigation-hub/advanced-filters", params=params)
        return [AdvancedFilter(**filter_item) for filter_item in response["result"]["entities"]]


class GetAdvancedFilterQuery(Query[AdvancedFilter]):
    """Query to get a specific advanced filter by ID."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, filter_id: int):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.filter_id = filter_id
    
    def execute(self) -> AdvancedFilter:
        """Execute the query."""
        response = self.http_client.get(
            f"investigation-hub/advanced-filters/{self.filter_id}"
        )
        return AdvancedFilter(**response["result"])


class GetEvidenceRecordsQuery(Query[Dict[str, Any]]):
    """Query to get evidence records with filtering."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, section: str,
                 filters: Optional[Dict[str, Any]] = None, page_size: int = 50, 
                 page_number: int = 1):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.section = section
        self.filters = filters or {}
        self.page_size = page_size
        self.page_number = page_number
    
    def execute(self) -> Dict[str, Any]:
        """Execute the query."""
        payload = {
            "take": self.page_size,
            "skip": (self.page_number - 1) * self.page_size,
            "filter": [],
            "globalFilter": {
                "assignmentIds": [],
                "flagIds": [],
                "verdictScores": [],
                "createdBy": [],
                "mitreTechniqueIds": [],
                "mitreTacticIds": []
            },
            "sort": [{"column": "verdict_score", "order": "desc"}]
        }
        # Merge any additional filters provided
        if self.filters:
            payload.update(self.filters)
        
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/sections/{self.section}",
            json_data=payload
        )
        return response["result"]


class GetFindingsStructureQuery(Query[FindingsStructure]):
    """Query to get findings structure for a specific investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str):
        self.http_client = http_client
        self.investigation_id = investigation_id
    
    def execute(self) -> FindingsStructure:
        """Execute the query."""
        response = self.http_client.get(
            f"investigation-hub/investigations/{self.investigation_id}/findings/structure"
        )
        return FindingsStructure(**response["result"])


class GetFindingsQuery(Query[FindingsResult]):
    """Query to get findings for a specific investigation."""
    
    def __init__(self, http_client: HTTPClient, investigation_id: str, 
                 request: FindingsRequest):
        self.http_client = http_client
        self.investigation_id = investigation_id
        self.request = request
    
    def execute(self) -> FindingsResult:
        """Execute the query."""
        response = self.http_client.post(
            f"investigation-hub/investigations/{self.investigation_id}/findings",
            json_data=self.request.model_dump(by_alias=True, exclude_none=True)
        )
        return FindingsResult(**response["result"]) 