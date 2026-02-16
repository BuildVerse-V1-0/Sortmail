"""
Intent Classifier
-----------------
Classifies email intent and urgency.
"""

from typing import Tuple
from contracts import EmailThreadV1, IntentType


# Urgency keywords for rule-based scoring
URGENT_KEYWORDS = [
    "urgent", "asap", "immediately", "critical", "emergency",
    "deadline", "today", "eod", "end of day", "time sensitive",
]

SCHEDULING_KEYWORDS = [
    "meeting", "schedule", "calendar", "availability", "slot",
    "tuesday", "wednesday", "thursday", "friday", "monday",
    "pm", "am", "noon", "morning", "afternoon",
]

FYI_KEYWORDS = [
    "fyi", "for your information", "no response needed",
    "just sharing", "heads up", "letting you know",
]


async def classify_intent(
    thread: EmailThreadV1,
    model: str = "gemini-1.5-pro",
) -> Tuple[IntentType, int]:
    """
    Classify the intent of an email thread.
    
    Args:
        thread: EmailThreadV1 to classify
        model: LLM model (for future use)
        
    Returns:
        Tuple of (intent type, urgency score 0-100)
    """
    # Get the latest message (most relevant for intent)
    if not thread.messages:
        return IntentType.UNKNOWN, 0
    
    latest = thread.messages[-1]
    
    # Skip if user sent the last message (no action needed)
    if latest.is_from_user:
        return IntentType.FYI, 10
    
    body_lower = latest.body_text.lower()
    subject_lower = thread.subject.lower()
    combined = f"{subject_lower} {body_lower}"
    
    # Rule-based classification
    intent, base_urgency = _classify_by_keywords(combined)
    
    # Adjust urgency based on additional signals
    urgency = _calculate_urgency(thread, intent, base_urgency)
    
    return intent, urgency


def _classify_by_keywords(text: str) -> Tuple[IntentType, int]:
    """Classify intent based on keyword matching."""
    # Check for urgent indicators
    urgent_count = sum(1 for kw in URGENT_KEYWORDS if kw in text)
    if urgent_count >= 2:
        return IntentType.URGENT, 90
    elif urgent_count >= 1:
        return IntentType.ACTION_REQUIRED, 70
    
    # Check for scheduling
    scheduling_count = sum(1 for kw in SCHEDULING_KEYWORDS if kw in text)
    if scheduling_count >= 2:
        return IntentType.SCHEDULING, 50
    
    # Check for FYI
    fyi_count = sum(1 for kw in FYI_KEYWORDS if kw in text)
    if fyi_count >= 1:
        return IntentType.FYI, 20
    
    # Check for questions (action required)
    if "?" in text:
        return IntentType.ACTION_REQUIRED, 50
    
    # Default
    return IntentType.FYI, 30


def _calculate_urgency(
    thread: EmailThreadV1,
    intent: IntentType,
    base_urgency: int,
) -> int:
    """Calculate final urgency score with adjustments."""
    urgency = base_urgency
    
    # Boost for attachments
    if thread.attachments:
        urgency += 10
    
    # Boost for multiple participants
    if len(thread.participants) > 3:
        urgency += 5
    
    # Cap at 100
    return min(urgency, 100)
