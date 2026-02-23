"""
Gemini Intelligence Engine
--------------------------
Single Gemini Flash call that returns ALL email intelligence in one JSON response.

Cost: ~₹0.04–0.30 per thread (Gemini Flash pricing)
Speed: ~3–5 seconds per thread
"""

import json
import re
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# ── Prompt ────────────────────────────────────────────────────────────────────

INTELLIGENCE_PROMPT = """\
You are an AI email intelligence assistant. Analyze the email thread below and return \
ALL intelligence in ONE JSON response — no markdown, no extra text.

<thread>
<subject>{subject}</subject>
<participants>{participants}</participants>
<messages>
{messages}
</messages>
</thread>

Return ONLY this exact JSON structure:
{{
  "summary": "2-3 sentence summary of the thread — what happened, what's needed",
  "intent": "urgent|action_required|scheduling|fyi|question|social|newsletter|other",
  "urgency_score": 0,
  "main_ask": "The single most important thing the sender needs (null if none)",
  "sentiment": "positive|neutral|negative|mixed",
  "priority_level": "urgent|high|medium|low",
  "follow_up_needed": true,
  "expected_reply_by": "YYYY-MM-DD or null",
  "action_items": [
    {{
      "title": "Short action title",
      "description": "What needs to be done",
      "due_date": "YYYY-MM-DD or null",
      "priority": "urgent|high|medium|low"
    }}
  ],
  "calendar_events": [
    {{
      "type": "meeting|deadline|reminder",
      "title": "Event title",
      "date": "YYYY-MM-DD or null",
      "time": "HH:MM or null",
      "confidence": 0.0
    }}
  ],
  "entities": {{
    "people": [],
    "companies": [],
    "dates": [],
    "amounts": []
  }},
  "suggested_reply_points": ["point 1", "point 2"]
}}

Rules:
- urgency_score: 0-100 (70+ = urgent, 40-69 = high, 20-39 = medium, 0-19 = low)
- action_items: only real tasks the user must do (empty list if none)
- calendar_events: only concrete dates/meetings (empty list if none)
- Respond ONLY with the JSON object, nothing else.
"""


# ── Engine ────────────────────────────────────────────────────────────────────

async def run_intelligence(
    thread_id: str,
    subject: str,
    participants: list[str],
    messages: list[dict],
) -> dict:
    """
    Run the single-call intelligence engine on a thread.

    Args:
        thread_id: Thread ID (for logging)
        subject: Thread subject
        participants: List of participant email strings
        messages: List of {"from": str, "date": str, "body": str}

    Returns:
        Parsed intel dict ready to save to Thread model
    """
    try:
        from app.config import settings
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Gemini not configured: {e}")
        return _fallback_intel(subject)

    # Build messages XML block (trim long bodies to save tokens)
    messages_xml = ""
    for msg in messages[:10]:  # max 10 messages per thread
        body = (msg.get("body") or "")[:2000]  # 2000 chars max per message
        messages_xml += (
            f"<message>\n"
            f"  <from>{msg.get('from', '')}</from>\n"
            f"  <date>{msg.get('date', '')}</date>\n"
            f"  <body>{body}</body>\n"
            f"</message>\n"
        )

    prompt = INTELLIGENCE_PROMPT.format(
        subject=subject or "(No Subject)",
        participants=", ".join(participants[:10]),
        messages=messages_xml,
    )

    try:
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            generation_config={
                "temperature": 0.2,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json",
            },
        )
        response = await model.generate_content_async(prompt)
        raw = response.text.strip()

        # Strip markdown code fences if model wrapped response
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL).strip()

        intel = json.loads(raw)
        intel["thread_id"] = thread_id
        intel["processed_at"] = datetime.utcnow().isoformat()
        intel["model"] = "gemini-2.0-flash"

        logger.info(
            f"Intel generated for thread {thread_id}: "
            f"intent={intel.get('intent')}, score={intel.get('urgency_score')}"
        )
        return intel

    except json.JSONDecodeError as e:
        logger.error(f"Intel JSON parse error for thread {thread_id}: {e}")
        return _fallback_intel(subject)
    except Exception as e:
        logger.error(f"Intel generation failed for thread {thread_id}: {e}")
        return _fallback_intel(subject)


def _fallback_intel(subject: str) -> dict:
    """Return minimal safe intel when Gemini fails."""
    return {
        "summary": f"Email thread: {subject or '(No Subject)'}",
        "intent": "fyi",
        "urgency_score": 10,
        "main_ask": None,
        "sentiment": "neutral",
        "priority_level": "low",
        "follow_up_needed": False,
        "expected_reply_by": None,
        "action_items": [],
        "calendar_events": [],
        "entities": {"people": [], "companies": [], "dates": [], "amounts": []},
        "suggested_reply_points": [],
        "model": "fallback",
    }
