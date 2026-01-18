"""
Deadline Extractor
------------------
Extracts deadlines and time references from email content.
"""

import re
from datetime import datetime, timedelta
from typing import List

from contracts import EmailThreadV1, ExtractedDeadline


# Common deadline patterns
DEADLINE_PATTERNS = [
    (r"by\s+(friday|monday|tuesday|wednesday|thursday|saturday|sunday)", "by {day}"),
    (r"by\s+(eod|end of day|cob|close of business)", "by end of day"),
    (r"by\s+(\d{1,2}[/\-]\d{1,2})", "by date"),
    (r"before\s+(\d{1,2}[/\-]\d{1,2})", "before date"),
    (r"deadline[:\s]+([^\n\.]+)", "explicit deadline"),
    (r"(asap|immediately|urgent)", "urgent"),
    (r"within\s+(\d+)\s+(day|hour|week)", "within timeframe"),
    (r"(tomorrow|today|next week)", "relative deadline"),
]


async def extract_deadlines(
    thread: EmailThreadV1,
    model: str = "gemini-1.5-pro",
) -> List[ExtractedDeadline]:
    """
    Extract deadline mentions from email thread.
    
    Args:
        thread: EmailThreadV1 to analyze
        model: LLM model (for future use)
        
    Returns:
        List of ExtractedDeadline objects
    """
    deadlines = []
    
    for msg in thread.messages:
        # Skip user's own messages
        if msg.is_from_user:
            continue
        
        msg_deadlines = _extract_from_text(msg.body_text, msg.message_id)
        deadlines.extend(msg_deadlines)
    
    # Also check subject
    subject_deadlines = _extract_from_text(thread.subject, "subject")
    deadlines.extend(subject_deadlines)
    
    # Deduplicate by raw_text
    seen = set()
    unique_deadlines = []
    for d in deadlines:
        if d.raw_text not in seen:
            seen.add(d.raw_text)
            unique_deadlines.append(d)
    
    return unique_deadlines


def _extract_from_text(text: str, source: str) -> List[ExtractedDeadline]:
    """Extract deadlines from text using patterns."""
    deadlines = []
    text_lower = text.lower()
    
    for pattern, description in DEADLINE_PATTERNS:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            raw_text = match.group(0)
            normalized = _normalize_deadline(raw_text)
            confidence = _calculate_confidence(raw_text, description)
            
            deadlines.append(ExtractedDeadline(
                raw_text=raw_text,
                normalized=normalized,
                confidence=confidence,
                source=source,
            ))
    
    return deadlines


def _normalize_deadline(raw_text: str) -> datetime:
    """Try to convert deadline text to actual datetime."""
    now = datetime.utcnow()
    text = raw_text.lower()
    
    # Handle relative terms
    if "today" in text:
        return now.replace(hour=17, minute=0, second=0)
    elif "tomorrow" in text:
        return (now + timedelta(days=1)).replace(hour=17, minute=0, second=0)
    elif "next week" in text:
        return (now + timedelta(days=7)).replace(hour=17, minute=0, second=0)
    elif "eod" in text or "end of day" in text:
        return now.replace(hour=17, minute=0, second=0)
    
    # Handle days of week
    days = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    for day, num in days.items():
        if day in text:
            days_ahead = num - now.weekday()
            if days_ahead <= 0:
                days_ahead += 7
            return (now + timedelta(days=days_ahead)).replace(hour=17, minute=0, second=0)
    
    # Default: 3 days from now
    return now + timedelta(days=3)


def _calculate_confidence(raw_text: str, description: str) -> float:
    """Calculate confidence score for deadline extraction."""
    if "explicit deadline" in description:
        return 0.95
    elif "urgent" in description:
        return 0.90
    elif "by" in description:
        return 0.85
    elif "relative" in description:
        return 0.80
    else:
        return 0.70
