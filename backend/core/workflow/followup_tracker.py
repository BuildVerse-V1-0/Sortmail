"""
Follow-up Tracker
-----------------
Tracks threads waiting for reply.

Output: WaitingForDTOv1 (Boundary Contract)
"""

from datetime import datetime, timedelta, timezone
from typing import List
import uuid

from contracts import ThreadIntelV1, WaitingForDTOv1


async def check_waiting_for(
    intel: ThreadIntelV1,
    user_id: str,
    user_email: str,
) -> WaitingForDTOv1:
    """
    Check if user is waiting for a reply on this thread.
    
    A thread is "waiting for" if:
    - User sent the last message
    - More than 24 hours have passed
    
    Returns:
        WaitingForDTOv1 if waiting, else None
    """
    # This would need message data from EmailThreadV1
    # For now, return None as stub
    return None


def calculate_days_waiting(last_sent: datetime) -> int:
    """Calculate number of days since last outbound message."""
    delta = datetime.now(timezone.utc) - last_sent
    return delta.days


async def create_waiting_for_entry(
    thread_id: str,
    user_id: str,
    recipient: str,
    last_sent: datetime,
    subject: str,
    summary: str,
) -> WaitingForDTOv1:
    """Create a new waiting-for tracking entry."""
    return WaitingForDTOv1(
        waiting_id=f"wait-{uuid.uuid4().hex[:8]}",
        thread_id=thread_id,
        user_id=user_id,
        last_sent_at=last_sent,
        days_waiting=calculate_days_waiting(last_sent),
        recipient=recipient,
        reminded=False,
        last_reminded_at=None,
        thread_subject=subject,
        thread_summary=summary,
    )
