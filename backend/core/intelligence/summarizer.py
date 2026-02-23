"""
Summarizer Module
-----------------
Extracts and normalizes the summary from the Gemini intel JSON.

Architecture: receives pre-computed intel_json (from gemini_engine.py),
              does NOT make any additional LLM calls.
"""

from typing import Optional


def extract_summary(intel_json: dict) -> str:
    """
    Extract a clean summary string from the Gemini intel output.

    Fallback chain:
    1. intel_json["summary"]  — from Gemini
    2. intel_json["main_ask"] — shorter version
    3. "(No summary available)"
    """
    summary = (intel_json.get("summary") or "").strip()
    if summary:
        return summary[:500]  # Truncate for DB storage safety

    main_ask = (intel_json.get("main_ask") or "").strip()
    if main_ask:
        return main_ask[:500]

    return "(No summary available)"


def extract_key_points(intel_json: dict) -> list[str]:
    """
    Extract any key points from the intel output.
    Returns a list of strings.
    """
    # Gemini returns suggested_reply_points which we re-use as key points
    points = intel_json.get("suggested_reply_points") or []
    return [str(p).strip() for p in points if p][:5]  # max 5 points


def extract_suggested_action(intel_json: dict) -> Optional[str]:
    """
    Generate a suggested action phrase from the intel output.
    """
    intent = (intel_json.get("intent") or "fyi").lower()
    urgency = int(intel_json.get("urgency_score") or 0)
    main_ask = intel_json.get("main_ask")

    if urgency >= 70:
        return f"Respond immediately — {main_ask or 'urgent action required'}"
    elif intent == "action_required":
        reply_by = intel_json.get("expected_reply_by")
        if reply_by:
            return f"Respond before {reply_by}"
        return f"Review and respond — {main_ask or 'action needed'}"
    elif intent == "scheduling":
        return "Confirm availability or propose an alternative time"
    elif intent == "question":
        return "Answer the question"
    elif intent in ("newsletter", "social"):
        return None  # No action needed
    return None
