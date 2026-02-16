"""
Email Schemas
-------------
Request/response models for email endpoints.
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ThreadListResponse(BaseModel):
    """Thread list item for UI."""
    thread_id: str
    subject: str
    summary: Optional[str] = None
    intent: Optional[str] = None
    urgency_score: int = 0
    last_updated: datetime
    has_attachments: bool = False
    message_count: int = 0


class SyncStatusResponse(BaseModel):
    """Email sync status."""
    status: str  # "idle", "syncing", "error"
    last_sync: Optional[datetime] = None
    threads_synced: int = 0
    error_message: Optional[str] = None


class SyncRequest(BaseModel):
    """Trigger sync request."""
    full_sync: bool = False  # If true, re-sync all emails
