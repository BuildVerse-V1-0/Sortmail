"""
Intent Classifier Module
-------------------------
Extracts intent and urgency from the Gemini intel JSON.

Architecture: pure extractor — no LLM calls, normalizes Gemini output
              into typed values compatible with the Thread model.
"""

from typing import Tuple


# Valid intent values (mirror IntentType contract enum)
VALID_INTENTS = {
    "urgent", "action_required", "scheduling", "fyi",
    "question", "social", "newsletter", "other",
}

# Intent → urgency score range (used for validation/clamping)
INTENT_MIN_SCORES = {
    "urgent": 70,
    "action_required": 40,
    "scheduling": 30,
    "question": 20,
    "fyi": 0,
    "social": 0,
    "newsletter": 0,
    "other": 0,
}


def extract_intent(intel_json: dict) -> Tuple[str, int]:
    """
    Extract intent label and urgency score from Gemini output.

    Returns:
        (intent: str, urgency_score: int)  — both safe for DB storage
    """
    raw_intent = (intel_json.get("intent") or "fyi").lower().strip()
    intent = raw_intent if raw_intent in VALID_INTENTS else "fyi"

    # Clamp urgency score 0–100
    raw_score = intel_json.get("urgency_score")
    try:
        score = max(0, min(100, int(raw_score or 0)))
    except (TypeError, ValueError):
        score = 0

    # Ensure score is consistent with intent
    min_score = INTENT_MIN_SCORES.get(intent, 0)
    score = max(score, min_score)

    return intent, score


def extract_priority_level(intel_json: dict) -> str:
    """
    Extract priority level string (urgent/high/medium/low).
    Falls back from urgency_score if not present.
    """
    priority = (intel_json.get("priority_level") or "").lower().strip()
    if priority in ("urgent", "high", "medium", "low"):
        return priority

    # Derive from urgency_score
    score = int(intel_json.get("urgency_score") or 0)
    if score >= 70:
        return "urgent"
    elif score >= 45:
        return "high"
    elif score >= 20:
        return "medium"
    return "low"


def should_follow_up(intel_json: dict) -> Tuple[bool, str | None]:
    """
    Returns (follow_up_needed, expected_reply_by).
    """
    needed = bool(intel_json.get("follow_up_needed", False))
    reply_by = intel_json.get("expected_reply_by")  # "YYYY-MM-DD" or None
    return needed, reply_by
