"""
Gemini Intelligence Engine
--------------------------
Single Gemini Flash call with robust retries and production-grade extraction.
"""

import json
import re
import logging
import asyncio
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# ── Prompt ────────────────────────────────────────────────────────────────────

PRODUCTION_EMAIL_PROMPT = """You are an expert email analyst. Analyze this email thread and extract actionable intelligence.

<email_thread>
<subject>{subject}</subject>
<participants>{participants}</participants>
<messages>
{messages}
</messages>
</email_thread>

Respond ONLY with this JSON structure:
{{
  "summary": "2-3 sentence executive summary",
  "intent": "action_required|fyi|scheduling|urgent|unknown",
  "urgency_score": 0,
  "urgency_reason": "Why this urgency score?",
  "sentiment": "positive|neutral|negative|mixed",
  "key_points": ["point 1", "point 2"],
  "action_items": [
    {{
      "task": "What to do",
      "owner": "Who should do it (YOU or THEM)",
      "deadline": "YYYY-MM-DD or null",
      "priority": "urgent|high|medium|low"
    }}
  ],
  "entities": {{
    "people": [],
    "companies": [],
    "dates": [],
    "amounts": []
  }},
  "follow_up_needed": true,
  "reply_deadline": "YYYY-MM-DD or null",
  "topics": ["budget", "contract", "hiring"],
  "meeting_detected": {{
    "has_meeting": true,
    "date": "YYYY-MM-DD or null",
    "time": "HH:MM or null",
    "location": "string or null"
  }}
}}

CRITICAL: Only use information from the email. Do not hallucinate. Do not wrap in markdown fences.
"""

# ── Engine ────────────────────────────────────────────────────────────────────

async def generate_with_retry(model, prompt: str, max_retries: int = 3, thread_id: str = "") -> dict:
    """Production-grade retry logic with exponential backoff"""
    for attempt in range(max_retries):
        try:
            response = await model.generate_content_async(prompt)
            raw = response.text.strip()
            # Strip markdown code fences if model wrapped response
            raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.DOTALL).strip()
            return json.loads(raw)
            
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Quota" in error_str:
                logger.warning(f"Gemini Rate Limit on {thread_id}. Retrying in {2 ** attempt}s...")
                await asyncio.sleep(2 ** attempt)
                continue
            elif "API_KEY_INVALID" in error_str or "API key not valid" in error_str:
                logger.error(f"❌ Gemini API key invalid! Skipping {thread_id}.")
                return _fallback_intel("", thread_id)
            elif "400" in error_str:
                logger.error(f"Gemini Bad Request on {thread_id}: {error_str}. Skipping.")
                return _fallback_intel("", thread_id)
            elif attempt == max_retries - 1:
                logger.error(f"Gemini failed after {max_retries} attempts for thread {thread_id}: {error_str}")
                return _fallback_intel("", thread_id)
            else:
                logger.warning(f"Unexpected error on {thread_id}, retrying... {error_str}")
                await asyncio.sleep(1)
                continue

async def run_intelligence(
    thread_id: str,
    subject: str,
    participants: list[str],
    messages: list[dict],
) -> dict:
    """Run the intelligence engine on a thread."""
    try:
        from app.config import settings
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        logger.error(f"Gemini configuration error: {e}")
        return _fallback_intel(subject, thread_id)

    # Build messages XML block (trim long bodies to save tokens, escape XML)
    messages_xml = ""
    for msg in messages[:10]:  # max 10 messages per thread
        body = (msg.get("body") or "")[:2000]
        body = body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        messages_xml += (
            f"<message>\n"
            f"  <from>{msg.get('from', '')}</from>\n"
            f"  <date>{msg.get('date', '')}</date>\n"
            f"  <body>{body}</body>\n"
            f"</message>\n"
        )

    prompt = PRODUCTION_EMAIL_PROMPT.replace(
        "{subject}", subject or "(No Subject)"
    ).replace(
        "{participants}", ", ".join(participants[:10])
    ).replace(
        "{messages}", messages_xml
    )

    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        generation_config={
            "temperature": 0.2,
            "max_output_tokens": 2048,
        },
    )

    intel = await generate_with_retry(model, prompt, max_retries=3, thread_id=thread_id)
    if not isinstance(intel, dict) or "summary" not in intel:
        intel = _fallback_intel(subject, thread_id)
        
    intel["thread_id"] = thread_id
    intel["processed_at"] = datetime.now(timezone.utc).isoformat()
    intel["model"] = "gemini-2.0-flash"

    logger.info(
        f"Intel generated for thread {thread_id}: "
        f"intent={intel.get('intent')}, score={intel.get('urgency_score')}"
    )
    return intel


def _fallback_intel(subject: str, thread_id: str) -> dict:
    """Return minimal safe intel when Gemini fails."""
    return {
        "thread_id": thread_id,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "summary": f"Email thread: {subject or '(No Subject)'}",
        "intent": "fyi",
        "urgency_score": 10,
        "sentiment": "neutral",
        "key_points": [],
        "action_items": [],
        "entities": {"people": [], "companies": [], "dates": [], "amounts": []},
        "follow_up_needed": False,
        "reply_deadline": None,
        "topics": [],
        "meeting_detected": {"has_meeting": False},
        "model": "fallback",
    }
