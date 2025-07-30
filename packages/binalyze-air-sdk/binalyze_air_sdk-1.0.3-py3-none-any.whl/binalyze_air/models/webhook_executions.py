"""
Webhook Executions models for the Binalyze AIR SDK.
"""

from typing import Optional, Dict, Any

from ..base import AIRBaseModel


class WebhookExecutionResponse(AIRBaseModel):
    """Webhook execution response model."""
    
    task_details_view_url: str
    task_details_data_url: str
    task_id: str
    status_code: int


class WebhookPostRequest(AIRBaseModel):
    """Request model for webhook POST."""
    
    data: Dict[str, Any]


class TaskDetailsData(AIRBaseModel):
    """Task details data model."""
    
    task_id: str
    task_name: Optional[str] = None
    task_status: Optional[str] = None
    task_type: Optional[str] = None
    created_at: Optional[str] = None
    assignments: Optional[Dict[str, Any]] = None 