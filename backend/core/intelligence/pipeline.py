"""
Intelligence Pipeline
----------------------
Orchestrates the full AI analysis of a saved thread.

Flow:
  1. Load thread + messages from DB
  2. Run gemini_engine.run_intelligence() — single Gemini Flash call
  3. Each module extracts its slice from the Gemini JSON:
       - summarizer        → summary, key_points, suggested_action
       - intent_classifier → intent, urgency_score, follow_up
       - deadline_extractor→ calendar events / deadlines
       - entity_extractor  → people, companies, action_items
  4. Save enriched intel back to Thread model (intel_json, summary, intent, urgency_score)
  5. Auto-create Tasks from action_items (no duplicates)
  6. Publish SSE event so frontend refreshes instantly
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.thread import Thread
from models.task import Task, TaskStatus, TaskType, PriorityLevel

# Intelligence modules — each is a pure extractor, no extra LLM calls
from .gemini_engine import run_intelligence
from .summarizer import extract_summary, extract_key_points, extract_suggested_action
from .intent_classifier import extract_intent, extract_priority_level, should_follow_up
from .deadline_extractor import extract_deadlines, extract_expected_reply_by
from .entity_extractor import extract_entities, extract_action_items

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Public entry point
# ─────────────────────────────────────────────────────────────────────────────

async def process_thread_intelligence(
    thread_id: str,
    user_id: str,
    db: AsyncSession,
) -> Optional[dict]:
    """
    Full intelligence pipeline for one thread.
    Safe to call in background — never raises, always returns.
    """
    try:
        # ── 1. Load thread ────────────────────────────────────────────
        thread = await _load_thread(thread_id, user_id, db)
        if not thread:
            return None

        # Skip if already processed recently (< 24h)
        if thread.intel_generated_at:
            age = (datetime.now(timezone.utc) - thread.intel_generated_at).total_seconds() / 3600
            if age < 24:
                logger.debug(f"Thread {thread_id} intel fresh, skipping")
                return None

        # ── 2. Load messages ──────────────────────────────────────────
        messages = await _load_messages(thread_id, db)

        # ── 3. Single Gemini Flash call ───────────────────────────────
        raw_intel = await run_intelligence(
            thread_id=thread_id,
            subject=thread.subject or "",
            participants=list(thread.participants or []),
            messages=messages,
        )

        # ── 4. Module extraction (pure functions, no LLM calls) ───────
        summary          = extract_summary(raw_intel)
        key_points       = extract_key_points(raw_intel)
        suggested_action = extract_suggested_action(raw_intel)

        intent, urgency_score  = extract_intent(raw_intel)
        priority_level         = extract_priority_level(raw_intel)
        follow_up, reply_by    = should_follow_up(raw_intel)

        deadlines              = extract_deadlines(raw_intel)
        entities               = extract_entities(raw_intel)
        action_items           = extract_action_items(raw_intel)

        # ── 5. Assemble final intel dict ──────────────────────────────
        final_intel = {
            **raw_intel,                          # keep all Gemini fields
            "summary"          : summary,
            "key_points"       : key_points,
            "suggested_action" : suggested_action,
            "intent"           : intent,
            "urgency_score"    : urgency_score,
            "priority_level"   : priority_level,
            "follow_up_needed" : follow_up,
            "expected_reply_by": reply_by,
            "deadlines"        : deadlines,
            "entities"         : entities,
            "action_items"     : action_items,
            "processed_at"     : datetime.now(timezone.utc).isoformat(),
        }

        # ── 6. Persist intel to Thread model ─────────────────────────
        thread.summary              = summary
        thread.intent               = intent
        thread.urgency_score        = urgency_score
        thread.intel_json           = final_intel
        thread.intel_generated_at   = datetime.now(timezone.utc)
        await db.commit()
        logger.info(f"Intel saved: thread={thread_id} intent={intent} score={urgency_score}")

        # ── 6.5 Embed thread into ChromaDB if valuable ─────────────────
        from core.intelligence.embedding_strategy import embed_thread_if_valuable
        messages_text = "\\n".join([m.get("body", "") for m in messages])
        await embed_thread_if_valuable(thread, user_id, messages_text, db)


        # ── 7. Auto-create Tasks from action items ────────────────────
        for item in action_items:
            await _create_task(user_id, thread_id, item, db)

        # ── 8. Publish SSE event → frontend invalidates cache ─────────
        await _publish_intel_ready(user_id, thread_id, final_intel)

        return final_intel

    except Exception as exc:
        logger.error(f"Intel pipeline failed for {thread_id}: {exc}", exc_info=True)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _load_thread(thread_id: str, user_id: str, db: AsyncSession) -> Optional[Thread]:
    stmt = select(Thread).where(Thread.id == thread_id, Thread.user_id == user_id)
    return (await db.execute(stmt)).scalars().first()


async def _load_messages(thread_id: str, db: AsyncSession) -> list[dict]:
    from models.email import Email
    stmt = select(Email).where(Email.thread_id == thread_id).order_by(Email.received_at)
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "from": m.sender,
            "date": m.sent_at.isoformat() if m.sent_at else m.received_at.isoformat() if m.received_at else "",
            "body": (m.body_plain or m.body_html or "")[:2000],
        }
        for m in rows
    ]


_PRIORITY_MAP = {
    "urgent": ("do_now", 90),
    "high"  : ("do_now", 80),
    "medium": ("do_today", 55),
    "low"   : ("can_wait", 20),
}


async def _create_task(
    user_id: str,
    thread_id: str,
    item: dict,
    db: AsyncSession,
) -> None:
    """Create a Task from an action item. Idempotent — skips if duplicate exists."""
    title = item.get("title", "")
    if not title:
        return

    # Dedup check
    existing = (await db.execute(
        select(Task).where(
            Task.user_id == user_id,
            Task.source_thread_id == thread_id,
            Task.title == title,
        )
    )).scalars().first()
    if existing:
        return

    priority_str = (item.get("priority") or "medium").lower()
    priority_value, priority_score = _PRIORITY_MAP.get(priority_str, ("do_today", 55))

    # Parse due_date
    due_date = None
    raw_due = item.get("due_date")
    if raw_due and raw_due.lower() != "null":
        try:
            from datetime import date
            due_date = datetime.strptime(raw_due, "%Y-%m-%d").date()
        except ValueError:
            pass

    task = Task(
        id=str(uuid.uuid4()),
        user_id=user_id,
        source_thread_id=thread_id,
        title=title,
        description=item.get("description"),
        task_type=TaskType.GENERAL,
        priority_level=priority_value,
        priority_score=priority_score,
        due_date=due_date,
        status=TaskStatus.PENDING,
        source_type="ai_generated",
        ai_confidence=85,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(task)
    await db.commit()
    logger.info(f"Auto-task created: '{title}' (thread={thread_id})")


async def _publish_intel_ready(user_id: str, thread_id: str, intel: dict) -> None:
    """Best-effort SSE publish via Redis pub/sub."""
    try:
        import json
        from core.redis import get_redis
        r = await get_redis()
        if not r:
            return
        payload = json.dumps({
            "type"              : "intel_ready",
            "thread_id"         : thread_id,
            "summary"           : (intel.get("summary") or "")[:120],
            "intent"            : intel.get("intent"),
            "urgency_score"     : intel.get("urgency_score", 0),
            "action_items_count": len(intel.get("action_items") or []),
        })
        await r.publish(f"user:{user_id}:events", payload)
    except Exception as e:
        logger.debug(f"SSE publish skipped: {e}")
