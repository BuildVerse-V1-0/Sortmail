"""
Deadline Extractor Module
--------------------------
Extracts and normalizes deadline/calendar events from the Gemini intel JSON.

Architecture: pure extractor — no LLM calls. Parses and validates dates
              from Gemini's calendar_events output.
"""

from datetime import datetime, date
from typing import Optional


def extract_deadlines(intel_json: dict) -> list[dict]:
    """
    Extract deadline-like events from intel JSON.

    Returns list of dicts:
        {title, date, time, type, confidence}

    Only returns events with confidence >= 0.5 and a valid date.
    """
    raw_events = intel_json.get("calendar_events") or []
    deadlines = []

    for event in raw_events:
        if not isinstance(event, dict):
            continue

        confidence = float(event.get("confidence") or 0.0)
        if confidence < 0.5:
            continue

        raw_date = event.get("date")
        parsed_date = _parse_date(raw_date)
        if not parsed_date:
            continue

        deadlines.append({
            "type": event.get("type", "deadline"),
            "title": (event.get("title") or "").strip(),
            "date": parsed_date.isoformat(),
            "time": event.get("time"),
            "confidence": confidence,
        })

    # Sort by date ascending
    deadlines.sort(key=lambda d: d["date"])
    return deadlines


def extract_expected_reply_by(intel_json: dict) -> Optional[str]:
    """
    Return expected_reply_by date string (YYYY-MM-DD) or None.
    """
    raw = intel_json.get("expected_reply_by")
    if not raw:
        return None
    parsed = _parse_date(str(raw))
    return parsed.isoformat() if parsed else None


def _parse_date(raw: str | None) -> Optional[date]:
    """Parse a date string gracefully. Accepts YYYY-MM-DD."""
    if not raw or raw.lower() == "null":
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None
