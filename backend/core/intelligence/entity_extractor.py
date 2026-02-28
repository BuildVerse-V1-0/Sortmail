"""
Entity Extractor Module
------------------------
Extracts people, companies, dates, and amounts from the Gemini intel JSON.

Architecture: pure extractor — no LLM calls. Normalizes Gemini's entities
              output into clean, deduplicated lists.
"""


def extract_entities(intel_json: dict) -> dict:
    """
    Extract and deduplicate named entities from Gemini intel output.

    Returns:
        {
            "people": [...],
            "companies": [...],
            "dates": [...],
            "amounts": [...],
        }
    """
    raw = intel_json.get("entities") or {}
    if not isinstance(raw, dict):
        return _empty_entities()

    return {
        "people": _clean_list(raw.get("people")),
        "companies": _clean_list(raw.get("companies")),
        "dates": _clean_list(raw.get("dates")),
        "amounts": _clean_list(raw.get("amounts")),
    }


def extract_people(intel_json: dict) -> list[str]:
    """Convenience: just the people list."""
    return extract_entities(intel_json)["people"]


def extract_action_items(intel_json: dict) -> list[dict]:
    """
    Extract and validate action items from Gemini intel output.

    Returns list of dicts with keys: title, description, due_date, priority.
    Skips items without a title.
    """
    raw = intel_json.get("action_items") or []
    valid = []

    for item in raw:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or item.get("task") or "").strip()
        if not title:
            continue

        priority = (item.get("priority") or "medium").lower()
        if priority not in ("urgent", "high", "medium", "low"):
            priority = "medium"
            
        owner = (item.get("owner") or "YOU").strip()

        valid.append({
            "title": title[:255],
            "description": f"Assigned to: {owner}",
            "due_date": item.get("due_date") or item.get("deadline"),
            "priority": priority,
        })

    return valid


def _clean_list(raw) -> list[str]:
    """Deduplicate and clean a list of strings."""
    if not raw or not isinstance(raw, list):
        return []
    seen = set()
    result = []
    for item in raw:
        s = str(item).strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            result.append(s)
    return result[:20]  # Cap at 20 per category


def _empty_entities() -> dict:
    return {"people": [], "companies": [], "dates": [], "amounts": []}
