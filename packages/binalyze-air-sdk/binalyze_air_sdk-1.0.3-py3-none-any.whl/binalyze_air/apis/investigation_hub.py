"""
Investigation Hub API for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any

from ..http_client import HTTPClient
from ..models.investigation_hub import (
    Investigation, InvestigationAsset, FlagSummary, EvidenceSection,
    EvidenceStructure, SQLQueryResult, FindingsSummary, FindingsStructure,
    FindingsResult, FindingsRequest, MitreMatch, InvestigationComment, 
    InvestigationActivity, AdvancedFilter, UpdateInvestigationRequest, 
    FlagEvidenceRequest, AddNoteRequest, CreateCommentRequest, 
    MarkActivityAsReadRequest, CreateAdvancedFilterRequest,
    UpdateAdvancedFilterRequest, ExportRequest
)
from ..queries.investigation_hub import (
    GetInvestigationQuery, GetInvestigationAssetsQuery, GetInvestigationFlagSummaryQuery,
    GetEvidenceSectionsQuery, GetEvidenceStructureQuery, ExecuteSQLQuery,
    GetFindingsSummaryQuery, GetFindingsStructureQuery, GetFindingsQuery,
    GetMitreMatchesQuery, GetInvestigationCommentsQuery,
    GetInvestigationActivitiesQuery, GetAdvancedFiltersQuery, GetAdvancedFilterQuery,
    GetEvidenceRecordsQuery
)
from ..commands.investigation_hub import (
    UpdateInvestigationCommand, DeleteInvestigationCommand, FlagEvidenceCommand,
    UnflagEvidenceCommand, AddNoteToEvidenceCommand, CreateCommentCommand,
    UpdateCommentCommand, DeleteCommentCommand, MarkActivitiesAsReadCommand,
    CreateAdvancedFilterCommand, UpdateAdvancedFilterCommand, DeleteAdvancedFilterCommand,
    ExportEvidenceCommand, GenerateReportCommand, RefreshInvestigationCommand,
    ArchiveInvestigationCommand, RestoreInvestigationCommand
)


class InvestigationHubAPI:
    """Investigation Hub API with CQRS pattern - separated queries and commands."""
    
    def __init__(self, http_client: HTTPClient):
        self.http_client = http_client
    
    # QUERIES (Read operations)
    def get_investigation(self, investigation_id: str) -> Investigation:
        """Get a specific investigation by ID."""
        query = GetInvestigationQuery(self.http_client, investigation_id)
        return query.execute()
    
    def get_assets(self, investigation_id: str) -> List[InvestigationAsset]:
        """Get assets for a specific investigation."""
        query = GetInvestigationAssetsQuery(self.http_client, investigation_id)
        return query.execute()
    
    def get_flag_summary(self, investigation_id: str) -> List[FlagSummary]:
        """Get flag summary for a specific investigation."""
        query = GetInvestigationFlagSummaryQuery(self.http_client, investigation_id)
        return query.execute()
    
    def get_evidence_sections(self, investigation_id: str, task_assignment_ids: List[str]) -> List[EvidenceSection]:
        """Get evidence sections for a specific investigation with task assignment IDs."""
        query = GetEvidenceSectionsQuery(self.http_client, investigation_id, task_assignment_ids)
        return query.execute()
    
    def get_evidence_structure(self, investigation_id: str, section: str) -> List[EvidenceStructure]:
        """Get evidence structure for a specific section."""
        query = GetEvidenceStructureQuery(self.http_client, investigation_id, section)
        return query.execute()
    
    def execute_sql_query(self, investigation_id: str, query: str, 
                         page_size: int = 10, page_number: int = 1) -> SQLQueryResult:
        """Execute SQL query against investigation database."""
        sql_query = ExecuteSQLQuery(self.http_client, investigation_id, query, page_size, page_number)
        return sql_query.execute()
    
    def get_findings_summary(self, investigation_id: str) -> FindingsSummary:
        """Get findings summary for a specific investigation."""
        query = GetFindingsSummaryQuery(self.http_client, investigation_id)
        return query.execute()
    
    def get_findings_structure(self, investigation_id: str) -> FindingsStructure:
        """Get findings structure for a specific investigation."""
        query = GetFindingsStructureQuery(self.http_client, investigation_id)
        return query.execute()
    
    def get_findings(self, investigation_id: str, request: Optional[FindingsRequest] = None) -> FindingsResult:
        """Get findings for a specific investigation."""
        if request is None:
            request = FindingsRequest()
        query = GetFindingsQuery(self.http_client, investigation_id, request)
        return query.execute()
    
    def get_mitre_matches(self, investigation_id: str) -> List[MitreMatch]:
        """Get MITRE ATT&CK matches for a specific investigation."""
        query = GetMitreMatchesQuery(self.http_client, investigation_id)
        return query.execute()
    
    def get_comments(self, investigation_id: str, evidence_id: Optional[str] = None) -> List[InvestigationComment]:
        """Get comments for a specific investigation."""
        query = GetInvestigationCommentsQuery(self.http_client, investigation_id, evidence_id)
        return query.execute()
    
    def get_activities(self, investigation_id: str, page_size: int = 20, 
                      page_number: int = 1) -> List[InvestigationActivity]:
        """Get activities for a specific investigation."""
        query = GetInvestigationActivitiesQuery(self.http_client, investigation_id, page_size, page_number)
        return query.execute()
    
    def get_advanced_filters(self, investigation_id: Optional[str] = None) -> List[AdvancedFilter]:
        """Get advanced filters (organization-wide, not investigation-specific)."""
        query = GetAdvancedFiltersQuery(self.http_client, investigation_id)
        return query.execute()
    
    def get_advanced_filter(self, investigation_id: str, filter_id: str) -> AdvancedFilter:
        """Get a specific advanced filter by ID."""
        query = GetAdvancedFilterQuery(self.http_client, investigation_id, int(filter_id))
        return query.execute()
    
    def get_evidence_records(self, investigation_id: str, section: str,
                            filters: Optional[Dict[str, Any]] = None, 
                            page_size: int = 50, page_number: int = 1) -> Dict[str, Any]:
        """Get evidence records with filtering."""
        query = GetEvidenceRecordsQuery(
            self.http_client, investigation_id, section, filters, page_size, page_number
        )
        return query.execute()
    
    # COMMANDS (Write operations)
    def update_investigation(self, investigation_id: str, request: UpdateInvestigationRequest) -> Investigation:
        """Update an investigation."""
        command = UpdateInvestigationCommand(self.http_client, investigation_id, request)
        return command.execute()
    
    def delete_investigation(self, investigation_id: str) -> Dict[str, Any]:
        """Delete an investigation."""
        command = DeleteInvestigationCommand(self.http_client, investigation_id)
        return command.execute()
    
    def flag_evidence(self, investigation_id: str, request: FlagEvidenceRequest) -> Dict[str, Any]:
        """Flag evidence records."""
        command = FlagEvidenceCommand(self.http_client, investigation_id, request)
        return command.execute()
    
    def unflag_evidence(self, investigation_id: str, records: List[Dict[str, Any]], 
                       section: str) -> Dict[str, Any]:
        """Unflag evidence records."""
        command = UnflagEvidenceCommand(self.http_client, investigation_id, records, section)
        return command.execute()
    
    def add_note_to_evidence(self, investigation_id: str, request: AddNoteRequest) -> Dict[str, Any]:
        """Add a note to evidence records."""
        command = AddNoteToEvidenceCommand(self.http_client, investigation_id, request)
        return command.execute()
    
    def create_comment(self, investigation_id: str, request: CreateCommentRequest) -> InvestigationComment:
        """Create a comment in an investigation."""
        command = CreateCommentCommand(self.http_client, investigation_id, request)
        return command.execute()
    
    def update_comment(self, investigation_id: str, comment_id: str, content: str) -> InvestigationComment:
        """Update a comment in an investigation."""
        command = UpdateCommentCommand(self.http_client, investigation_id, comment_id, content)
        return command.execute()
    
    def delete_comment(self, investigation_id: str, comment_id: str) -> Dict[str, Any]:
        """Delete a comment from an investigation."""
        command = DeleteCommentCommand(self.http_client, investigation_id, comment_id)
        return command.execute()
    
    def mark_activities_as_read(self, investigation_id: str, 
                               request: MarkActivityAsReadRequest) -> Dict[str, Any]:
        """Mark activities as read."""
        command = MarkActivitiesAsReadCommand(self.http_client, investigation_id, request)
        return command.execute()
    
    def create_advanced_filter(self, investigation_id: str, 
                              request: CreateAdvancedFilterRequest) -> AdvancedFilter:
        """Create an advanced filter."""
        command = CreateAdvancedFilterCommand(self.http_client, investigation_id, request)
        return command.execute()
    
    def update_advanced_filter(self, investigation_id: str, filter_id: str, 
                              request: UpdateAdvancedFilterRequest) -> AdvancedFilter:
        """Update an advanced filter."""
        command = UpdateAdvancedFilterCommand(self.http_client, investigation_id, int(filter_id), request)
        return command.execute()
    
    def delete_advanced_filter(self, investigation_id: str, filter_id: str) -> Dict[str, Any]:
        """Delete an advanced filter."""
        command = DeleteAdvancedFilterCommand(self.http_client, investigation_id, int(filter_id))
        return command.execute()
    
    def export_evidence(self, investigation_id: str, request: ExportRequest) -> Dict[str, Any]:
        """Export evidence data."""
        command = ExportEvidenceCommand(self.http_client, investigation_id, request)
        return command.execute()
    
    def generate_report(self, investigation_id: str, report_type: str = "comprehensive", 
                       include_evidence: bool = True) -> Dict[str, Any]:
        """Generate an investigation report."""
        command = GenerateReportCommand(self.http_client, investigation_id, report_type, include_evidence)
        return command.execute()
    
    def refresh_investigation(self, investigation_id: str) -> Investigation:
        """Refresh/rebuild an investigation."""
        command = RefreshInvestigationCommand(self.http_client, investigation_id)
        return command.execute()
    
    def archive_investigation(self, investigation_id: str) -> Dict[str, Any]:
        """Archive an investigation."""
        command = ArchiveInvestigationCommand(self.http_client, investigation_id)
        return command.execute()
    
    def restore_investigation(self, investigation_id: str) -> Investigation:
        """Restore an archived investigation."""
        command = RestoreInvestigationCommand(self.http_client, investigation_id)
        return command.execute()
    
    # Convenience methods
    def sql_query(self, investigation_id: str, query: str, page_size: int = 10, 
                 page_number: int = 1) -> SQLQueryResult:
        """Alias for execute_sql_query for convenience."""
        return self.execute_sql_query(investigation_id, query, page_size, page_number)
    
    def get_investigation_data(self, investigation_id: str, task_assignment_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get comprehensive investigation data including assets, flags, and sections."""
        result = {
            "investigation": self.get_investigation(investigation_id),
            "assets": self.get_assets(investigation_id),
            "flag_summary": self.get_flag_summary(investigation_id)
        }
        
        # Only include evidence sections if task assignment IDs are provided
        if task_assignment_ids:
            result["evidence_sections"] = self.get_evidence_sections(investigation_id, task_assignment_ids)
        
        return result 