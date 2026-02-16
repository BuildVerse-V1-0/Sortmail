"""
API Routes - Threads
--------------------
Email thread endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from contracts import ThreadIntelV1
from contracts.mocks import create_mock_thread_intel

router = APIRouter()


class ThreadListItem(BaseModel):
    """Lightweight thread for list view."""
    thread_id: str
    subject: str
    summary: str
    intent: str
    urgency_score: int
    last_updated: datetime
    has_attachments: bool


@router.get("/", response_model=List[ThreadListItem])
async def list_threads(
    limit: int = Query(default=20, le=50),
    offset: int = Query(default=0, ge=0),
):
    """
    List email threads for current user.
    
    Returns threads sorted by last_updated descending.
    """
    # TODO: Replace with real DB query
    intel = create_mock_thread_intel()
    return [{
        "thread_id": intel.thread_id,
        "subject": "Contract Review - Final Terms",
        "summary": intel.summary,
        "intent": intel.intent.value,
        "urgency_score": intel.urgency_score,
        "last_updated": datetime.utcnow(),
        "has_attachments": len(intel.attachment_summaries) > 0,
    }]


@router.get("/{thread_id}", response_model=ThreadIntelV1)
async def get_thread(thread_id: str):
    """
    Get full thread intelligence.
    
    Includes summary, attachments, deadlines, and suggestions.
    """
    # TODO: Replace with real DB query + intelligence processing
    intel = create_mock_thread_intel()
    intel.thread_id = thread_id
    return intel


@router.post("/{thread_id}/refresh")
async def refresh_thread(thread_id: str):
    """
    Re-process thread intelligence.
    
    Useful after new emails arrive or if user wants updated analysis.
    """
    # TODO: Trigger re-analysis
    return {"thread_id": thread_id, "refreshed": True}
