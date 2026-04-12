"""
Intelligence Pipeline
----------------------
Orchestrates the full AI analysis of a saved thread.

Flow:
  1. Load thread + messages from DB
   2. Run llama_engine.run_intelligence() â€” single Llama 3.3 70B call via HF API
  3. Each module extracts its slice from the Gemini JSON:
       - summarizer        â†’ summary, key_points, suggested_action
       - intent_classifier â†’ intent, urgency_score, follow_up
       - deadline_extractorâ†’ calendar events / deadlines
       - entity_extractor  â†’ people, companies, action_items
  4. Save enriched intel back to Thread model (intel_json, summary, intent, urgency_score)
  5. Auto-create Tasks from action_items (no duplicates)
  6. Publish SSE event so frontend refreshes instantly
"""

import logging
import json
import re
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from models.thread import Thread
from models.task import Task, TaskStatus, TaskType, PriorityLevel
from models.follow_up import FollowUp, FollowUpStatus
from models.email import Email
from models.attachment import Attachment

# Intelligence engine â€” Llama 3.3 70B via HF Inference API
from .llama_engine import run_intelligence_with_usage
from .summarizer import extract_summary, extract_key_points, extract_suggested_action, extract_suggested_draft
from .intent_classifier import extract_intent, extract_priority_level, should_follow_up
from .deadline_extractor import extract_deadlines, extract_expected_reply_by
from .entity_extractor import extract_entities, extract_action_items, extract_tags
from models.contact import Contact
from models.tag import Tag
from models.draft import Draft, DraftStatus, DraftTone
from core.app_metrics import record_metric
from core.redis import RedisClient
from app.config import settings

logger = logging.getLogger(__name__)

REPLY_INTENTS = {"ACTION_REQUIRED", "URGENT", "QUESTION", "SCHEDULING"}
TASK_INTENTS = {"ACTION_REQUIRED", "URGENT", "SCHEDULING"}
LOW_VALUE_MARKERS = (
    "unsubscribe",
    "manage preferences",
    "view in browser",
    "newsletter",
    "weekly digest",
    "daily digest",
    "marketing",
    "promotion",
    "promotional",
    "sale",
    "discount",
    "coupon",
    "special offer",
    "limited time",
    "subscribe",
    "subscription",
    "product update",
    "webinar",
    "announcement",
    "event invite",
    "register now",
    "learn more",
    "view our website",
    "visit our site",
    "watch now",
)
ACTION_MARKERS = (
    "please review",
    "approve",
    "approval",
    "confirm",
    "sign",
    "schedule",
    "meeting",
    "deadline",
    "due",
    "question",
    "follow up",
)
PAYMENT_MARKERS = (
    "bill",
    "invoice",
    "payment",
    "pay now",
    "pay by",
    "due amount",
    "overdue",
    "last date",
    "service disruption",
    "outstanding balance",
    "renewal due",
    "recharge",
)

BILLING_STRONG_MARKERS = (
    "bill",
    "invoice",
    "statement",
    "statement period",
    "closing balance",
    "opening balance",
    "charges",
    "tax",
    "gst",
    "account number",
    "due date",
    "payment due",
    "service disruption",
)

PROMOTIONAL_TASK_SUPPRESS_MARKERS = (
    "bug bounty",
    "credited to your account",
    "webinar",
    "free session",
    "make money",
    "reward",
    "invitation",
    "join now",
    "register now",
)
SOCIAL_NOTIFICATION_MARKERS = (
    "linkedin",
    "invited you to connect",
    "connection request",
    "accept or decline",
    "view profile",
    "new follower",
    "started following you",
    "commented on your post",
    "liked your post",
    "mentioned you",
    "webinar",
    "event invite",
    "join us",
    "watch now",
    "learn more",
    "visit our site",
    "view our website",
)
STALE_WORKFLOW_DAYS = 14
PAYMENT_TASK_WINDOW_DAYS = 3
PASS2_TRIGGER_INTENTS = {"ACTION_REQUIRED", "URGENT", "SCHEDULING", "QUESTION"}
IMPORTANT_FYI_MARKERS = (
    "event",
    "incident",
    "outage",
    "downtime",
    "security",
    "breach",
    "policy update",
    "deadline",
    "compliance",
    "maintenance",
)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Public entry point
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

async def process_thread_intelligence(
    thread_id: str,
    user_id: str,
    db: AsyncSession,
) -> Optional[dict]:
    """
    Full intelligence pipeline for one thread.
    Safe to call in background â€” never raises, always returns.
    """
    lock_acquired = False
    redis_client = None
    lock_key = f"intel:inflight:{user_id}:{thread_id}"
    lock_token = str(uuid.uuid4())
    record_metric("intel_request")

    try:
        # â”€â”€ 1. Load thread â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        thread = await _load_thread(thread_id, user_id, db)
        if not thread:
            return None

        redis_client, lock_acquired = await _acquire_intel_lock(lock_key, lock_token)
        if not lock_acquired:
            record_metric("intel_lock_contended")
            logger.debug(f"Thread {thread_id} intel already in progress, skipping duplicate run")
            return None

        # Skip if already processed recently (< 24h)
        if thread.intel_generated_at:
            age = (datetime.now(timezone.utc) - thread.intel_generated_at).total_seconds() / 3600
            if age < 24:
                record_metric("intel_skipped_fresh")
                logger.debug(f"Thread {thread_id} intel fresh, skipping")
                await _remove_from_processing_queue(thread_id)
                return None

        # â”€â”€ 2. Load messages â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        messages = await _load_messages(thread_id, db)

        if messages and bool(messages[-1].get("is_from_user")):
            record_metric("intel_skipped_latest_outbound")
            logger.info("Intel skipped for outbound-latest thread=%s", thread_id)
            await _remove_from_processing_queue(thread_id)
            return None

        # Do not run AI intel for unsubscribed contacts.
        if await _is_unsubscribed_sender_thread(user_id, thread, messages, db):
            record_metric("intel_skipped_unsubscribed")
            logger.info("Intel skipped for unsubscribed sender thread=%s", thread_id)
            await _remove_from_processing_queue(thread_id)
            return None

        low_value_reason = _detect_low_value_thread(thread, messages)
        if low_value_reason:
            record_metric("intel_skipped_low_value")
            final_intel = _build_low_value_intel(thread, low_value_reason)
            thread.summary = final_intel["summary"]
            thread.intent = final_intel["intent"]
            thread.urgency_score = final_intel["urgency_score"]
            thread.intel_json = final_intel
            thread.intel_generated_at = datetime.now(timezone.utc)

            await _process_contacts(user_id, messages, db)
            await _sync_follow_up(
                user_id=user_id,
                thread=thread,
                follow_up_needed=False,
                expected_reply_by=None,
                messages=messages,
                db=db,
            )
            await db.commit()
            logger.info(f"Intel skipped for low-value thread={thread_id} reason={low_value_reason}")
            _log_intel_payload(thread_id, final_intel, source="low_value")
            await _publish_intel_ready(user_id, thread_id, final_intel)
            await _remove_from_processing_queue(thread_id)
            return final_intel

        try:
            # Two-pass intelligence: pass-1 micro for all threads, pass-2 only when needed.
            raw_intel, pass_meta = await _run_two_pass_intelligence(
                thread=thread,
                thread_id=thread_id,
                user_id=user_id,
                subject=thread.subject or "",
                participants=list(thread.participants or []),
                messages=messages,
            )

            # â”€â”€ 4. Module extraction (pure functions, no LLM calls) â”€â”€â”€â”€â”€â”€â”€
            summary = extract_summary(raw_intel)
            key_points = extract_key_points(raw_intel)
            suggested_action = extract_suggested_action(raw_intel)
            attachment_context = await _load_attachment_context(thread_id, db)
            summary, key_points = _merge_attachment_context(summary, key_points, attachment_context)

            intent, urgency_score = extract_intent(raw_intel)
            priority_level = extract_priority_level(raw_intel)
            follow_up, reply_by = should_follow_up(raw_intel)

            deadlines = extract_deadlines(raw_intel)
            entities = extract_entities(raw_intel)
            action_items = extract_action_items(raw_intel)
            tags_list = extract_tags(raw_intel)
            suggested_draft = extract_suggested_draft(raw_intel)
            should_create_reply = _coerce_optional_bool(raw_intel.get("should_create_reply"))
            should_create_tasks = _coerce_optional_bool(raw_intel.get("should_create_tasks"))

            bill_task = _extract_bill_payment_task(thread, messages, raw_intel)
            if bill_task:
                action_items = [bill_task]
                should_create_tasks = True
                if urgency_score < 80:
                    urgency_score = 80
                if priority_level not in {"urgent", "high"}:
                    priority_level = "urgent"

            if should_create_reply is None:
                should_create_reply = intent in REPLY_INTENTS and not _is_low_value_intent(intent)
            if should_create_tasks is None:
                should_create_tasks = intent in TASK_INTENTS and bool(action_items) and not _is_low_value_intent(intent)

            if _should_suppress_task_generation(thread, messages, raw_intel):
                should_create_tasks = False
                action_items = []

            if not should_create_reply:
                suggested_draft = None
            if not should_create_tasks:
                action_items = []

            stale_workflow_reason = _stale_workflow_reason(thread)
            if stale_workflow_reason:
                should_create_reply = False
                should_create_tasks = False
                suggested_draft = None
                action_items = []

            workflow_reason = stale_workflow_reason or raw_intel.get("workflow_reason") or _build_workflow_reason(
                intent=intent,
                should_create_reply=should_create_reply,
                should_create_tasks=should_create_tasks,
                action_items_count=len(action_items),
            )

            # â”€â”€ 5. Assemble final intel dict â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            final_intel = {
                **raw_intel,
                "summary": summary,
                "key_points": key_points,
                "suggested_action": suggested_action,
                "intent": intent,
                "urgency_score": urgency_score,
                "should_create_reply": bool(should_create_reply),
                "should_create_tasks": bool(should_create_tasks),
                "is_promotional": _coerce_bool(raw_intel.get("is_promotional")),
                "is_subscription": _coerce_bool(raw_intel.get("is_subscription")),
                "workflow_reason": workflow_reason,
                "priority_level": priority_level,
                "follow_up_needed": follow_up,
                "expected_reply_by": reply_by,
                "deadlines": deadlines,
                "entities": entities,
                "action_items": action_items,
                "tags": tags_list,
                "attachment_intel": attachment_context,
                "suggested_draft": suggested_draft,
                "pass_strategy": pass_meta,
                "processed_at": datetime.now(timezone.utc).isoformat(),
            }

            # â”€â”€ 6. Persist intel to Thread model â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            thread.summary = summary
            thread.intent = intent
            thread.urgency_score = urgency_score
            thread.intel_json = final_intel
            thread.intel_generated_at = datetime.now(timezone.utc)

            # â”€â”€ 6a. Process Contacts FIRST (so tags can be linked) â”€â”€â”€â”€â”€â”€â”€â”€â”€
            await _process_contacts(user_id, messages, db)

            # â”€â”€ 6b. Process Tags (Gemini tags + Contact tags) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            await _process_tags(user_id, thread, tags_list, db)
            await _sync_follow_up(
                user_id=user_id,
                thread=thread,
                follow_up_needed=bool(follow_up),
                expected_reply_by=reply_by,
                messages=messages,
                db=db,
            )

            # Background intelligence must not auto-create reply drafts.
            # Drafts are generated only when the user explicitly requests them.

            await db.commit()
            logger.info(f"Intel saved: thread={thread_id} intent={intent} score={urgency_score}")
            _log_intel_payload(thread_id, final_intel, source="full")

            # â”€â”€ 6.5 Embed thread into ChromaDB if valuable â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            from core.intelligence.embedding_strategy import embed_thread_if_valuable
            messages_text = "\n".join([m.get("body", "") for m in messages])
            await embed_thread_if_valuable(thread, user_id, messages_text, db)

            # â”€â”€ 6.7 Check if sender is unsubscribed â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            # If the thread sender is unsubscribed, skip auto-creating tasks.
            is_unsubscribed = False
            import re
            email_regex = re.compile(r"<([^>]+)>|([^\s<>]+@[^\s<>]+)")
            for p in list(thread.participants or []):
                match = email_regex.search(p)
                if match:
                    email = (match.group(1) or match.group(2)).lower()
                    stmt_unsub = select(Contact.is_unsubscribed).where(
                        Contact.user_id == user_id,
                        Contact.email_address == email,
                    )
                    if (await db.execute(stmt_unsub)).scalar():
                        is_unsubscribed = True
                        break

            # â”€â”€ 7. Auto-create Tasks from action items â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
            if not is_unsubscribed and should_create_tasks:
                for item in action_items:
                    confidence = item.get("confidence")
                    if confidence is not None and isinstance(confidence, (int, float)) and confidence < 0.75:
                        continue
                    await _create_task(user_id, thread_id, item, db)

            # â”€â”€ 8. Publish SSE event â†’ frontend invalidates cache â”€â”€â”€â”€â”€â”€â”€â”€â”€
            await _publish_intel_ready(user_id, thread_id, final_intel)
            record_metric("intel_completed")
            await _remove_from_processing_queue(thread_id)

            return final_intel

        except Exception as exc:
            record_metric("intel_failed")
            await db.rollback()
            logger.error(f"Intel pipeline failed for {thread_id}: {exc}", exc_info=True)
            return None

    except Exception as exc:
        record_metric("intel_failed")
        await db.rollback()
        logger.error(f"Intel pipeline failed for {thread_id}: {exc}", exc_info=True)
        return None
    finally:
        if lock_acquired:
            await _release_intel_lock(redis_client, lock_key, lock_token)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Helpers
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

async def _load_thread(thread_id: str, user_id: str, db: AsyncSession) -> Optional[Thread]:
    """Load thread with tags eagerly to avoid lazy-load in async context."""
    from sqlalchemy.orm import selectinload
    stmt = (
        select(Thread)
        .where(Thread.id == thread_id, Thread.user_id == user_id)
        .options(selectinload(Thread.tags))
    )
    return (await db.execute(stmt)).scalars().first()


def _log_intel_payload(thread_id: str, intel: dict, source: str) -> None:
    """Log a compact summary plus payload snapshot after intel generation."""
    if not isinstance(intel, dict):
        logger.info("Intel payload: thread=%s source=%s payload_type=%s", thread_id, source, type(intel).__name__)
        return

    summary = (intel.get("summary") or "").strip().replace("\n", " ")[:220]
    payload = json.dumps(intel, default=str, ensure_ascii=False)
    max_chars = 8000
    if len(payload) > max_chars:
        payload = payload[:max_chars] + " ...<truncated>"

    logger.info(
        "Intel produced: thread=%s source=%s intent=%s urgency=%s action_items=%s tags=%s attachment_intel=%s summary=%s",
        thread_id,
        source,
        intel.get("intent"),
        intel.get("urgency_score"),
        len(intel.get("action_items") or []),
        len(intel.get("tags") or []),
        len(intel.get("attachment_intel") or []),
        summary,
    )
    logger.info("Intel payload: thread=%s source=%s data=%s", thread_id, source, payload)


async def _remove_from_processing_queue(thread_id: str) -> None:
    """Remove thread from Redis queue after processing."""
    try:
        rc = RedisClient.get_instance()
        await rc.zrem("intel:pending", thread_id)
        record_metric("queue_item_removed")
    except Exception:
        pass


async def _load_messages(thread_id: str, db: AsyncSession) -> list[dict]:
    from models.email import Email
    stmt = select(Email).where(Email.thread_id == thread_id).order_by(
        func.coalesce(Email.sent_at, Email.received_at, Email.created_at)
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "from": m.sender,
            "date": m.sent_at.isoformat() if m.sent_at else m.received_at.isoformat() if m.received_at else "",
            "body": (m.body_plain or m.body_html or "")[:2000],
            "is_from_user": bool(m.is_from_user),
        }
        for m in rows
    ]


def _parse_message_datetime(raw_value: str | None) -> Optional[datetime]:
    if not raw_value:
        return None
    try:
        value = datetime.fromisoformat(raw_value.replace("Z", "+00:00"))
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    except ValueError:
        return None


def _derive_follow_up_context(thread: Thread, messages: list[dict], user_email: Optional[str] = None) -> tuple[datetime, str]:
    last_sent_at = thread.last_email_at or datetime.now(timezone.utc)
    recipient = "Unknown"

    for msg in reversed(messages):
        if msg.get("is_from_user"):
            sent_at = _parse_message_datetime(msg.get("date"))
            if sent_at:
                last_sent_at = sent_at
            break

    user_email_lower = (user_email or "").lower()
    for participant in list(thread.participants or []):
        candidate = (participant or "").strip()
        if not candidate:
            continue
        if user_email_lower and user_email_lower in candidate.lower():
            continue
        recipient = candidate
        break

    return last_sent_at, recipient


def _parse_expected_reply_by(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        if len(value) == 10:
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
            return datetime(parsed_date.year, parsed_date.month, parsed_date.day, 23, 59, tzinfo=timezone.utc)
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


async def _sync_follow_up(
    user_id: str,
    thread: Thread,
    follow_up_needed: bool,
    expected_reply_by: Optional[str],
    messages: list[dict],
    db: AsyncSession,
) -> None:
    stmt = select(FollowUp).where(
        FollowUp.user_id == user_id,
        FollowUp.thread_id == thread.id,
        FollowUp.deleted_at.is_(None),
    )
    follow_up = (await db.execute(stmt)).scalars().first()

    if not follow_up_needed:
        if follow_up:
            follow_up.status = FollowUpStatus.CANCELLED
            follow_up.deleted_at = datetime.now(timezone.utc)
            follow_up.updated_at = datetime.now(timezone.utc)
        return

    last_sent_at, recipient = _derive_follow_up_context(thread, messages)
    metadata = dict((follow_up.metadata_json if follow_up else {}) or {})
    metadata["last_sent_at"] = last_sent_at.isoformat()
    metadata["recipient"] = recipient

    expected_reply_dt = _parse_expected_reply_by(expected_reply_by)

    if not follow_up:
        now = datetime.now(timezone.utc)
        days_waiting = max((now - last_sent_at).days, 0)
        follow_up = FollowUp(
            id=str(uuid.uuid4()),
            user_id=user_id,
            thread_id=thread.id,
            last_sent_at=last_sent_at,
            days_waiting=days_waiting,
            expected_reply_by=expected_reply_dt,
            status=FollowUpStatus.WAITING,
            auto_detected=True,
            detection_confidence=85,
            metadata_json=metadata,
            created_at=now,
            updated_at=now,
        )
        db.add(follow_up)
        return

    follow_up.deleted_at = None
    if follow_up.status in {FollowUpStatus.CANCELLED, FollowUpStatus.REPLIED}:
        follow_up.status = FollowUpStatus.WAITING
        follow_up.reply_received_at = None
    follow_up.last_sent_at = last_sent_at
    follow_up.days_waiting = max((datetime.now(timezone.utc) - last_sent_at).days, 0)
    follow_up.expected_reply_by = expected_reply_dt
    follow_up.auto_detected = True
    follow_up.metadata_json = metadata
    follow_up.updated_at = datetime.now(timezone.utc)


def _detect_low_value_thread(thread: Thread, messages: list[dict]) -> Optional[str]:
    """Return a short reason when the thread looks promotional or subscription-like."""
    parts = [thread.subject or "", " ".join(thread.participants or [])]
    parts.extend(msg.get("body", "") for msg in messages[:3])
    text = " ".join(parts).lower()

    if any(marker in text for marker in ("unsubscribe", "manage preferences", "view in browser", "newsletter", "weekly digest", "daily digest")):
        if not any(marker in text for marker in ACTION_MARKERS):
            return "promotional_or_subscription"

    if any(marker in text for marker in LOW_VALUE_MARKERS):
        if not any(marker in text for marker in ACTION_MARKERS):
            return "marketing_blast"

    if any(marker in text for marker in ("no-reply", "noreply", "do-not-reply")) and any(marker in text for marker in ("newsletter", "promotion", "sale", "discount", "coupon", "special offer", "unsubscribe")):
        return "no_reply_marketing_mail"

    if any(marker in text for marker in SOCIAL_NOTIFICATION_MARKERS):
        return "social_notification"

    return None


async def _is_unsubscribed_sender_thread(
    user_id: str,
    thread: Thread,
    messages: list[dict],
    db: AsyncSession,
) -> bool:
    """Return True when any sender/participant maps to an unsubscribed contact."""

    def _extract_email(text: str | None) -> str | None:
        if not text:
            return None
        match = re.search(r"<([^>]+)>", text)
        if match:
            return match.group(1).strip().lower()
        if "@" in text:
            return text.strip().lower()
        return None

    candidates: set[str] = set()
    for msg in messages:
        email = _extract_email(msg.get("from"))
        if email:
            candidates.add(email)

    for participant in list(thread.participants or []):
        email = _extract_email(participant)
        if email:
            candidates.add(email)

    if not candidates:
        return False

    stmt = select(Contact.email_address).where(
        Contact.user_id == user_id,
        Contact.is_unsubscribed == True,
        Contact.email_address.in_(list(candidates)),
    )
    row = (await db.execute(stmt)).first()
    return row is not None


def _build_low_value_intel(thread: Thread, reason: str) -> dict:
    subject = thread.subject or "(No Subject)"
    intent = "NEWSLETTER" if "subscription" in reason or "newsletter" in reason else "FYI"
    if reason == "social_notification":
        intent = "SOCIAL"
    summary = f"Low-value email: {subject}"

    if reason == "promotional_or_subscription":
        summary = f"Newsletter or subscription update: {subject}"
    elif reason == "marketing_blast":
        summary = f"Promotional email: {subject}"
    elif reason == "social_notification":
        summary = f"Social notification: {subject}"

    return {
        "thread_id": thread.id,
        "summary": summary,
        "intent": intent,
        "urgency_score": 0,
        "should_create_reply": False,
        "should_create_tasks": False,
        "is_promotional": True,
        "is_subscription": intent == "NEWSLETTER",
        "workflow_reason": reason,
        "main_ask": None,
        "decision_needed": None,
        "extracted_deadlines": [],
        "entities": [],
        "attachment_summaries": [],
        "suggested_action": None,
        "suggested_reply_points": [],
        "key_points": [],
        "deadlines": [],
        "tags": ["Newsletter"] if intent == "NEWSLETTER" else (["Social"] if intent == "SOCIAL" else ["Promotional"]),
        "action_items": [],
        "suggested_draft": None,
        "follow_up_needed": False,
        "expected_reply_by": None,
        "priority_level": "low",
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": "heuristic-low-value",
        "model": "heuristic-low-value",
    }


def _is_low_value_intent(intent: str) -> bool:
    return intent in {"FYI", "NEWSLETTER", "SOCIAL", "OTHER", "UNKNOWN"}


def _build_workflow_reason(
    intent: str,
    should_create_reply: bool,
    should_create_tasks: bool,
    action_items_count: int,
) -> str:
    if _is_low_value_intent(intent):
        return "Informational mail only; no workflow action needed."
    if should_create_reply and should_create_tasks:
        return f"Actionable thread with {action_items_count} task(s) and a reply needed."
    if should_create_reply:
        return "Reply needed, but no task should be created."
    if should_create_tasks:
        return f"Task-only thread with {action_items_count} task(s)."
    return "No workflow action needed."


def _contains_important_fyi_signal(thread: Thread, messages: list[dict], raw_intel: dict) -> bool:
    parts = [
        str(thread.subject or ""),
        str(raw_intel.get("summary") or ""),
        str(raw_intel.get("workflow_reason") or ""),
        " ".join(str(topic) for topic in (raw_intel.get("topics") or [])),
        " ".join(str(tag) for tag in (raw_intel.get("tags") or [])),
    ]
    for msg in messages[:3]:
        parts.append(str(msg.get("body") or "")[:600])
    text = " ".join(parts).lower()
    return any(marker in text for marker in IMPORTANT_FYI_MARKERS)


def _meeting_detected(raw_intel: dict) -> bool:
    meeting = raw_intel.get("meeting_detected")
    if isinstance(meeting, dict):
        return bool(meeting.get("has_meeting") or meeting.get("detected"))
    return bool(meeting)


def _has_deadline_or_followup(raw_intel: dict) -> bool:
    return bool(
        raw_intel.get("reply_deadline")
        or raw_intel.get("expected_reply_by")
        or raw_intel.get("follow_up_needed")
        or raw_intel.get("deadlines")
        or raw_intel.get("extracted_deadlines")
    )


def _should_run_second_pass(thread: Thread, messages: list[dict], micro_intel: dict) -> bool:
    if not settings.INTEL_TWO_PASS_ENABLED:
        return False

    intent = str(micro_intel.get("intent") or "").upper()
    if intent in PASS2_TRIGGER_INTENTS:
        return True

    if bool(micro_intel.get("should_create_reply")) or bool(micro_intel.get("should_create_tasks")):
        return True

    if len(micro_intel.get("action_items") or []) > 0:
        return True

    if _meeting_detected(micro_intel) or _has_deadline_or_followup(micro_intel):
        return True

    if intent in {"FYI", "INFORMATION", "INFORMATION_SHARED"} and _contains_important_fyi_signal(thread, messages, micro_intel):
        return True

    return False


def _merge_pass_intel(primary: dict, secondary: dict) -> dict:
    merged = dict(primary or {})
    for key, value in (secondary or {}).items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, list) and not value and isinstance(merged.get(key), list) and merged.get(key):
            continue
        if isinstance(value, dict) and not value and isinstance(merged.get(key), dict) and merged.get(key):
            continue
        merged[key] = value
    return merged


async def _run_two_pass_intelligence(
    *,
    thread: Thread,
    thread_id: str,
    user_id: str,
    subject: str,
    participants: list[str],
    messages: list[dict],
) -> tuple[dict, dict]:
    pass1_model = settings.INTEL_PASS1_MODEL_ID or "amazon.nova-micro-v1:0"
    pass2_model = settings.INTEL_PASS2_MODEL_ID or settings.BEDROCK_MODEL_ID

    pass1 = await run_intelligence_with_usage(
        thread_id=thread_id,
        user_id=user_id,
        subject=subject,
        participants=participants,
        messages=messages,
        model_id=pass1_model,
        operation="thread_intel_pass1",
    )
    pass1_intel = dict(pass1.get("intel") or {})
    run_pass2 = _should_run_second_pass(thread=thread, messages=messages, micro_intel=pass1_intel)

    pass_meta = {
        "two_pass_enabled": bool(settings.INTEL_TWO_PASS_ENABLED),
        "pass1_model": pass1_model,
        "pass1_input_tokens": int(pass1.get("input_tokens") or 0),
        "pass1_output_tokens": int(pass1.get("output_tokens") or 0),
        "pass1_latency_ms": int(pass1.get("latency_ms") or 0),
        "pass1_token_source": pass1.get("token_source"),
        "pass2_executed": False,
        "pass2_model": pass2_model,
    }

    if not run_pass2:
        return pass1_intel, pass_meta

    pass2 = await run_intelligence_with_usage(
        thread_id=thread_id,
        user_id=user_id,
        subject=subject,
        participants=participants,
        messages=messages,
        model_id=pass2_model,
        first_pass_intel=pass1_intel,
        operation="thread_intel_pass2",
    )
    pass2_intel = dict(pass2.get("intel") or {})

    pass_meta.update(
        {
            "pass2_executed": True,
            "pass2_input_tokens": int(pass2.get("input_tokens") or 0),
            "pass2_output_tokens": int(pass2.get("output_tokens") or 0),
            "pass2_latency_ms": int(pass2.get("latency_ms") or 0),
            "pass2_token_source": pass2.get("token_source"),
        }
    )

    return _merge_pass_intel(pass1_intel, pass2_intel), pass_meta


def _extract_bill_payment_task(thread: Thread, messages: list[dict], raw_intel: dict) -> Optional[dict]:
    combined_parts = [
        thread.subject or "",
        thread.summary or "",
        raw_intel.get("summary") or "",
        raw_intel.get("workflow_reason") or "",
    ]
    for message in messages:
        combined_parts.append(message.get("subject") or "")
        combined_parts.append(message.get("body") or "")

    combined_text = " ".join(part for part in combined_parts if part).lower()
    if not combined_text:
        return None

    # Guardrail: do not create billing tasks for obvious promotional / bounty mail.
    if any(marker in combined_text for marker in PROMOTIONAL_TASK_SUPPRESS_MARKERS):
        return None

    if not any(marker in combined_text for marker in PAYMENT_MARKERS):
        return None

    # Require at least one concrete billing signal, not just generic "payment" language.
    if not any(marker in combined_text for marker in BILLING_STRONG_MARKERS):
        return None

    # Positive credit notification is not a payable bill.
    if "credited" in combined_text and "due" not in combined_text and "overdue" not in combined_text:
        return None

    due_date = _extract_payment_due_date(combined_text)
    today = datetime.now(timezone.utc).date()

    due_in_days: Optional[int] = None
    if due_date:
        due_in_days = (due_date - today).days
        if due_in_days > PAYMENT_TASK_WINDOW_DAYS:
            return None
    elif not any(marker in combined_text for marker in ("due today", "due tomorrow", "today", "tomorrow", "last date")):
        return None

    title = _build_bill_task_title(thread.subject, raw_intel.get("summary") or thread.summary or "")
    if not title:
        title = "Pay bill"

    if due_in_days is None or due_in_days <= 1:
        priority = "urgent"
        task_type = "FOLLOWUP"
    elif due_in_days == 2 or due_in_days == 3:
        priority = "high"
        task_type = "FOLLOWUP"
    else:
        priority = "high"
        task_type = "FOLLOWUP"

    description_bits = ["Auto-generated from bill/payment email."]
    if due_date:
        description_bits.append(f"Due date: {due_date.isoformat()}.")
    summary_text = raw_intel.get("summary") or thread.summary
    if summary_text:
        description_bits.append(summary_text[:240])

    return {
        "title": title,
        "description": " ".join(description_bits),
        "due_date": due_date.isoformat() if due_date else today.isoformat(),
        "priority": priority,
        "task_type": task_type,
        "confidence": 0.95,
    }


def _should_suppress_task_generation(thread: Thread, messages: list[dict], raw_intel: dict) -> bool:
    """Suppress tasks for promotional messages unless clear billing/payment-required signals exist."""
    combined_parts = [
        thread.subject or "",
        thread.summary or "",
        raw_intel.get("summary") or "",
        raw_intel.get("workflow_reason") or "",
    ]
    for message in messages:
        combined_parts.append(message.get("subject") or "")
        combined_parts.append(message.get("body") or "")

    combined_text = " ".join(part for part in combined_parts if part).lower()
    if not combined_text:
        return False

    is_promotional = _coerce_bool(raw_intel.get("is_promotional"))
    if not is_promotional:
        return False

    has_billing_signal = any(marker in combined_text for marker in BILLING_STRONG_MARKERS)
    has_due_signal = any(marker in combined_text for marker in ("due", "overdue", "last date", "due date", "pay now", "service disruption"))

    # Promotional + no explicit billing/due context => suppress tasks.
    if not (has_billing_signal and has_due_signal):
        return True

    # Explicit promo phrases should still suppress unless this is clearly an invoice/bill mail.
    if any(marker in combined_text for marker in PROMOTIONAL_TASK_SUPPRESS_MARKERS):
        return True

    return False


def _build_bill_task_title(subject: Optional[str], summary: str) -> str:
    text = (subject or summary or "").strip()
    if not text:
        return "Pay bill"

    lowered = text.lower()
    if "bill" in lowered:
        cleaned = re.sub(r"(?i)\b(urgent|overdue|bill|payment reminder|pay now|due today|due tomorrow|last date|service disruption|invoice)\b", "", text)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" -:|")
        if cleaned:
            return f"Pay {cleaned[:80]}"
        return "Pay bill"

    if "invoice" in lowered:
        return "Pay invoice"

    return "Pay bill"


def _extract_payment_due_date(text: str) -> Optional[datetime.date]:
    today = datetime.now(timezone.utc).date()
    if "overdue" in text or "last date" in text or "due today" in text:
        return today
    if "due tomorrow" in text:
        return today.replace(day=today.day) + timedelta(days=1)

    patterns = [
        r"\b\d{1,2}-[a-z]{3}-\d{2,4}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
        r"\b[a-z]{3,9}\s+\d{1,2}(?:,\s*\d{4})?\b",
        r"\b\d{1,2}\s+[a-z]{3,9}\s+\d{2,4}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        parsed = _parse_bill_date(match.group(0))
        if parsed:
            return parsed
    return None


def _parse_bill_date(raw: str) -> Optional[datetime.date]:
    candidates = (
        "%d-%b-%y",
        "%d-%b-%Y",
        "%d/%m/%y",
        "%d/%m/%Y",
        "%d-%m-%y",
        "%d-%m-%Y",
        "%b %d %Y",
        "%b %d, %Y",
        "%B %d %Y",
        "%B %d, %Y",
    )
    for fmt in candidates:
        try:
            return datetime.strptime(raw.title(), fmt).date()
        except ValueError:
            continue
    return None


def _stale_workflow_reason(thread: Thread) -> Optional[str]:
    """Disable auto-workflow for stale threads to avoid noise during backfills/redeploys."""
    if not thread.last_email_at:
        return None
    now = datetime.now(timezone.utc)
    age_days = (now - thread.last_email_at).total_seconds() / 86400
    if age_days >= STALE_WORKFLOW_DAYS:
        return f"Thread is {int(age_days)} days old; auto-workflow suppressed."
    return None


async def _load_attachment_context(thread_id: str, db: AsyncSession) -> list[dict]:
    """Load attachment intelligence linked to emails in this thread."""
    stmt = (
        select(Attachment)
        .join(Email, Email.id == Attachment.email_id)
        .where(Email.thread_id == thread_id)
        .order_by(Attachment.created_at.desc())
    )
    rows = (await db.execute(stmt)).scalars().all()

    payload: list[dict] = []
    for att in rows:
        intel = att.intel_json or {}
        if not intel:
            continue
        payload.append(
            {
                "attachment_id": att.id,
                "email_id": att.email_id,
                "filename": att.filename,
                "mime_type": att.mime_type,
                "summary": intel.get("summary"),
                "key_points": intel.get("key_points") or [],
                "risk_flags": intel.get("risk_flags") or [],
                "action_items": intel.get("action_items") or [],
                "security": intel.get("security") or {},
            }
        )
    return payload


def _merge_attachment_context(summary: str, key_points: list[str], attachment_context: list[dict]) -> tuple[str, list[str]]:
    """Merge attachment intel highlights into thread summary and key points."""
    if not attachment_context:
        return summary, key_points

    enriched_summary = summary
    attachment_summaries = [ctx.get("summary") for ctx in attachment_context[:2] if ctx.get("summary")]
    if attachment_summaries:
        enriched_summary = (summary or "").strip()
        attachment_suffix = " ".join(f"Attachment: {item}" for item in attachment_summaries)
        enriched_summary = f"{enriched_summary} {attachment_suffix}".strip()[:500]

    merged_points = list(key_points or [])
    for ctx in attachment_context[:3]:
        for point in (ctx.get("key_points") or [])[:2]:
            if point and point not in merged_points:
                merged_points.append(point)
    return enriched_summary, merged_points[:8]


def _coerce_optional_bool(value) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1"}:
            return True
        if lowered in {"false", "no", "0", "null", "none", ""}:
            return False
    return bool(value)


def _coerce_bool(value) -> bool:
    return bool(_coerce_optional_bool(value))


async def _acquire_intel_lock(lock_key: str, token: str) -> tuple[Optional[object], bool]:
    """Acquire a short-lived Redis lock to avoid duplicate model calls."""
    try:
        from core.redis import get_redis
        r = await get_redis()
        acquired = await r.set(lock_key, token, ex=180, nx=True)
        return r, bool(acquired)
    except Exception:
        # If Redis is unavailable, do not block processing.
        return None, True


async def _release_intel_lock(redis_client, lock_key: str, token: str) -> None:
    """Best-effort lock release with token check to avoid deleting others' locks."""
    if not redis_client:
        return
    try:
        current_token = await redis_client.get(lock_key)
        if current_token == token:
            await redis_client.delete(lock_key)
    except Exception:
        pass


_PRIORITY_MAP = {
    "urgent": ("DO_NOW", 90),
    "high"  : ("DO_NOW", 80),
    "medium": ("DO_TODAY", 55),
    "low"   : ("CAN_WAIT", 20),
}


async def _process_tags(user_id: str, thread: Thread, tags_list: list[str], db: AsyncSession) -> None:
    """Get or create tags and attach them to the thread. Also propagates contact tags."""
    # 1. Add tags suggested by Gemini
    if tags_list:
        for tag_name in tags_list:
            if not tag_name:
                continue
            
            stmt = select(Tag).where(Tag.user_id == user_id, Tag.name.ilike(tag_name))
            existing_tag = (await db.execute(stmt)).scalars().first()
            
            if not existing_tag:
                existing_tag = Tag(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    name=tag_name,
                    is_auto_applied=True
                )
                db.add(existing_tag)
                
            if existing_tag not in thread.tags:
                thread.tags.append(existing_tag)
                
    # 2. Add tags from the thread's contacts (CRM propagation)
    from sqlalchemy.orm import selectinload
    import re
    email_regex = re.compile(r"<([^>]+)>|([^\s<>]+@[^\s<>]+)")
    
    # Seen participants to avoid redundant DB lookups
    seen_emails = set()
    for participant in (thread.participants or []):
        match = email_regex.search(participant)
        if not match: continue
        email = (match.group(1) or match.group(2)).lower()
        if email in seen_emails: continue
        seen_emails.add(email)
        
        stmt = select(Contact).where(
            Contact.user_id == user_id, 
            Contact.email_address == email
        ).options(selectinload(Contact.tags))
        contact = (await db.execute(stmt)).scalars().first()
        
        if contact and contact.tags:
            for tag in contact.tags:
                if tag not in thread.tags:
                    thread.tags.append(tag)
                    logger.debug(f"Propagated contact tag '{tag.name}' to thread {thread.id}")


async def _process_contacts(user_id: str, messages: list[dict], db: AsyncSession) -> None:
    """Extract email addresses from message senders and update/create Contacts."""
    import re
    from collections import Counter
    # Match text between < > or match full string if it's just an email
    email_regex = re.compile(r"<([^>]+)>|([^\s<>]+@[^\s<>]+)")
    
    # Count occurrences per sender
    sender_counts = Counter()
    sender_full_names = {}

    for msg in messages:
        if msg.get("is_from_user"):
            continue
        
        participant = msg.get("from", "")
        match = email_regex.search(participant)
        if match:
            email = (match.group(1) or match.group(2)).lower()
            if email:
                sender_counts[email] += 1
                sender_full_names[email] = participant

    for email, count in sender_counts.items():
        stmt = select(Contact).where(Contact.user_id == user_id, Contact.email_address == email)
        contact = (await db.execute(stmt)).scalars().first()
        
        full_name = sender_full_names[email]
        if contact:
            contact.interaction_count += count
            contact.last_interaction_at = datetime.now(timezone.utc)
            contact.updated_at = datetime.now(timezone.utc)
        else:
            contact = Contact(
                id=str(uuid.uuid4()),
                user_id=user_id,
                email_address=email,
                name=full_name.split("<")[0].strip() if "<" in full_name else None,
                interaction_count=count,
                last_interaction_at=datetime.now(timezone.utc)
            )
            db.add(contact)


async def _create_draft(user_id: str, thread_id: str, content: str, db: AsyncSession) -> None:
    """Auto-create a Draft reply from Gemini's suggestion."""
    # Dedup Check: Avoid creating multiple AUTO generated drafts per thread
    stmt = select(Draft).where(
        Draft.user_id == user_id, 
        Draft.thread_id == thread_id,
        Draft.status == DraftStatus.GENERATED.value
    )
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        return
        
    draft = Draft(
        id=str(uuid.uuid4()),
        user_id=user_id,
        thread_id=thread_id,
        subject="Re: Thread", # Placeholder, relies on frontend to pull thread subject
        content=content,
        body=content,
        tone=DraftTone.NORMAL.value,
        generation_model="llama-3.3-70b-instruct",
        status=DraftStatus.GENERATED.value
    )
    db.add(draft)
    record_metric("auto_draft_created")
    logger.info(f"Auto-draft created for thread={thread_id}")


async def _create_task(
    user_id: str,
    thread_id: str,
    item: dict,
    db: AsyncSession,
) -> None:

    """Create a Task from an action item. Idempotent â€” skips if duplicate exists."""
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
    priority_value, priority_score = _PRIORITY_MAP.get(priority_str, ("DO_TODAY", 55))

    # Parse due_date
    due_date = None
    raw_due = item.get("due_date")
    if raw_due and raw_due.lower() != "null":
        try:
            from datetime import date
            due_date = datetime.strptime(raw_due, "%Y-%m-%d").date()
        except ValueError:
            pass

    raw_type = (item.get("task_type") or "REPLY").upper()
    ALLOWED_TASK_TYPES = {"REPLY", "REVIEW", "SCHEDULE", "FOLLOWUP", "OTHER"}
    
    if raw_type not in ALLOWED_TASK_TYPES:
        logger.warning(f"Invalid task type '{raw_type}', defaulting to '{TaskType.REPLY.value}'")
        final_task_type = TaskType.REPLY
    else:
        final_task_type = TaskType(raw_type)
    logger.debug(f"raw_type: {raw_type}")
    logger.debug(f"final_task_type enum: {final_task_type}")
    logger.debug(f"value being inserted: {final_task_type.value}")

    task = Task(
        id=str(uuid.uuid4()),
        user_id=user_id,
        source_thread_id=thread_id,
        title=title,
        description=item.get("description"),
        task_type=final_task_type,
        priority_level=priority_value,
        priority_score=priority_score,
        due_date=due_date,
        status=TaskStatus.PENDING,
        source_type="ai_generated",
        ai_confidence=85,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    try:
        db.add(task)
        await db.commit()
        record_metric("auto_task_created")
        logger.info(f"Auto-task created: '{title}' (thread={thread_id})")
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create auto-task '{title}': {e}")


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
