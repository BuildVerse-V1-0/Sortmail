"""
API Routes - Reminders
----------------------
Follow-up reminder endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter
from datetime import datetime, timezone

from contracts import WaitingForDTOv1
from contracts.mocks import create_mock_waiting_for

router = APIRouter()


@router.get("/", response_model=List[WaitingForDTOv1])
async def list_reminders():
    """
    List all threads waiting for reply.
    """
    # TODO: Replace with real DB query
    return [create_mock_waiting_for()]


@router.post("/{waiting_id}/remind")
async def send_reminder(waiting_id: str):
    """Mark that a reminder was sent."""
    # TODO: Implement reminder tracking
    return {"waiting_id": waiting_id, "reminded": True, "reminded_at": datetime.now(timezone.utc)}


@router.delete("/{waiting_id}")
async def dismiss_reminder(waiting_id: str):
    """Dismiss a waiting-for entry."""
    return {"waiting_id": waiting_id, "dismissed": True}
