"""
Evidence-related data models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from ..base import AIRBaseModel


class EvidencePPC(AIRBaseModel):
    """Evidence PPC (Portable Pre-processor Configuration) model for binary file downloads."""
    
    endpoint_id: str
    task_id: str
    content: bytes  # Binary content of the PPC file
    content_type: Optional[str] = None  # MIME type of the file
    content_length: Optional[int] = None  # Size of the file in bytes
    filename: Optional[str] = None  # Suggested filename
    
    def save_to_file(self, filepath: str) -> bool:
        """Save the PPC content to a file."""
        try:
            with open(filepath, 'wb') as f:
                f.write(self.content)
            return True
        except Exception:
            return False


class EvidenceReportFileInfo(AIRBaseModel):
    """Evidence report file info model."""
    
    endpoint_id: str
    task_id: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    created_at: Optional[datetime] = None
    status: Optional[str] = None
    # Additional fields from API
    file_path: Optional[str] = None  # Full path to the file
    encoding: Optional[str] = None  # File encoding (e.g., "7bit")
    mime_type: Optional[str] = None  # MIME type (e.g., "application/octet-stream")
    file_hash: Optional[str] = None  # File hash/checksum
    organization_id: Optional[int] = None  # Organization ID
    is_purged: Optional[bool] = None  # Whether file has been purged


class EvidenceReport(AIRBaseModel):
    """Evidence report model."""
    
    endpoint_id: str
    task_id: str
    content: bytes  # Binary content of the report file
    content_type: Optional[str] = None
    content_length: Optional[int] = None
    filename: Optional[str] = None
    
    def save_to_file(self, filepath: str) -> bool:
        """Save the report content to a file."""
        try:
            with open(filepath, 'wb') as f:
                f.write(self.content)
            return True
        except Exception:
            return False 