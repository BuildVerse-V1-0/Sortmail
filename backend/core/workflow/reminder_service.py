"""
Reminder Service
----------------
Handles follow-up reminder notifications.
"""

from datetime import datetime, timedelta, timezone
from typing import List

from contracts import WaitingForDTOv1


async def check_for_reminders(
    user_id: str,
    reminder_threshold_days: int = 3,
) -> List[WaitingForDTOv1]:
    """
    Find threads that need follow-up reminders.
    
    Returns threads where:
    - User sent the last message
    - No reply received in threshold days
    """
    # TODO: Query database for waiting-for threads
    return []


async def should_remind(waiting: WaitingForDTOv1) -> bool:
    """Check if we should show a reminder for this thread."""
    if waiting.reminded:
        # Already reminded, check if enough time has passed
        if waiting.last_reminded_at:
            days_since_reminder = (datetime.now(timezone.utc) - waiting.last_reminded_at).days
            return days_since_reminder >= 2  # Re-remind every 2 days
        return False
    return waiting.days_waiting >= 3  # Initial reminder after 3 days


async def mark_reminded(waiting_id: str) -> bool:
    """Mark a waiting-for entry as reminded."""
    # TODO: Update database
    return True
