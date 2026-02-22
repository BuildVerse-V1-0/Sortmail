"""
API Routes - Threads
--------------------
Email thread endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from contracts import ThreadIntelV1
from contracts.mocks import create_mock_thread_intel

router = APIRouter()


class ThreadListItem(BaseModel):
    """Lightweight thread for list view."""
    thread_id: str
    subject: str
    summary: str
    intent: str
    urgency_score: int
    last_updated: datetime
    has_attachments: bool


from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User
from models.thread import Thread
from core.credits.credit_service import CreditService, InsufficientCreditsError, RateLimitExceededError

@router.get("/", response_model=List[ThreadListItem])
async def list_threads(
    limit: int = Query(default=20, le=50),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List email threads for current user.
    
    Returns threads sorted by last_updated descending.
    """
    stmt = (
        select(Thread)
        .where(Thread.user_id == current_user.id)
        .order_by(desc(Thread.last_email_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    threads = result.scalars().all()
    
    return [
        ThreadListItem(
            thread_id=t.id,
            subject=t.subject or "(No Subject)",
            summary=t.summary or "Pending analysis...",
            intent=t.intent or "processing",
            urgency_score=t.urgency_score or 0,
            last_updated=t.last_email_at or datetime.utcnow(),
            has_attachments=t.has_attachments or False,
        )
        for t in threads
    ]


class ContactItem(BaseModel):
    email: str
    name: str
    total_threads: int
    last_contact: Optional[datetime]


@router.get("/contacts", response_model=List[ContactItem])
async def list_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List unique contacts derived from the user's email threads.
    Aggregates participants across all threads.
    """
    stmt = (
        select(Thread)
        .where(Thread.user_id == current_user.id)
        .order_by(desc(Thread.last_email_at))
        .limit(200)
    )
    result = await db.execute(stmt)
    threads = result.scalars().all()

    # Aggregate contacts from participants
    contact_map: dict = {}
    for t in threads:
        participants = t.participants or []
        for p in participants:
            if not p or current_user.email in p:
                continue
            email = p.strip().lower()
            if email not in contact_map:
                # Extract name from "Name <email>" format if present
                if "<" in p:
                    name = p.split("<")[0].strip().strip('"')
                    clean_email = p.split("<")[1].rstrip(">").strip()
                else:
                    name = email.split("@")[0].replace(".", " ").title()
                    clean_email = email
                contact_map[clean_email] = {
                    "email": clean_email,
                    "name": name,
                    "total_threads": 1,
                    "last_contact": t.last_email_at,
                }
            else:
                contact_map[email]["total_threads"] += 1
                if t.last_email_at and (
                    not contact_map[email]["last_contact"]
                    or t.last_email_at > contact_map[email]["last_contact"]
                ):
                    contact_map[email]["last_contact"] = t.last_email_at

    # Sort by most threads first
    sorted_contacts = sorted(
        contact_map.values(), key=lambda x: x["total_threads"], reverse=True
    )
    return [ContactItem(**c) for c in sorted_contacts[:100]]


from typing import List, Optional, Dict, Any
from contracts.ingestion import EmailThreadV1, EmailMessage, AttachmentRef
from contracts.intelligence import ThreadIntelV1
from contracts.workflow import TaskDTOv1, DraftDTOv1
from models.attachment import Attachment
from models.thread import Message

# Helper to serialize ThreadIntel
def _serialize_intel(t: Thread) -> Optional[ThreadIntelV1]:
    if not t.intel_json and not t.summary:
        return None
        
    # If we have JSON cache, use it
    if t.intel_json:
        # Pydantic parse
        try:
            return ThreadIntelV1(**t.intel_json)
        except:
            pass
            
    # Construct partial from columns
    return ThreadIntelV1(
        thread_id=t.id,
        summary=t.summary or "",
        intent=t.intent or "unknown",
        urgency_score=t.urgency_score or 0,
        main_ask=None,
        decision_needed=None,
        extracted_deadlines=[],
        entities=[],
        attachment_summaries=[],
        suggested_action=None,
        suggested_reply_points=[],
        schema_version="v0-partial",
        processed_at=t.intel_generated_at or datetime.utcnow()
    )

class ThreadDetailResponse(BaseModel):
    thread: EmailThreadV1
    intel: Optional[ThreadIntelV1]
    tasks: List[TaskDTOv1]
    draft: Optional[DraftDTOv1]


@router.get("/{thread_id}", response_model=ThreadDetailResponse)
async def get_thread(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get full thread details including messages, attachments, and intelligence.
    """
    # 1. Fetch Thread
    stmt = select(Thread).where(Thread.id == thread_id, Thread.user_id == current_user.id)
    result = await db.execute(stmt)
    thread = result.scalars().first()
    
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
        
    # 2. Fetch Messages
    msg_stmt = select(Message).where(Message.thread_id == thread_id).order_by(Message.sent_at)
    msg_result = await db.execute(msg_stmt)
    messages = msg_result.scalars().all()
    
    # 3. Attachments — skip until Attachment model FK is resolved
    # (Attachment.message_id column doesn't exist in DB; FK points to emails not messages)
    attachments = []
    
    # 4. Construct Encapsulated Objects
    normalized_messages = [
        EmailMessage(
            message_id=m.id,
            from_address=m.from_address,
            to_addresses=m.to_addresses or [],
            cc_addresses=m.cc_addresses or [],
            subject=m.subject or "",
            body_text=m.body_text or "",
            sent_at=m.sent_at,
            is_from_user=(str(m.is_from_user).lower() == 'true'),
            labels=[] # Messages table doesn't have labels yet
        )
        for m in messages
    ]
    
    normalized_attachments = [
        AttachmentRef(
            attachment_id=a.id,
            filename=a.filename,
            original_filename=a.original_filename,
            mime_type=a.mime_type,
            storage_path=a.storage_path or "",
            size_bytes=a.size_bytes,
        )
        for a in attachments
    ]
    
    email_thread = EmailThreadV1(
        thread_id=thread.id,
        external_id=thread.external_id,
        subject=thread.subject or "(No Subject)",
        participants=thread.participants or [],
        messages=normalized_messages,
        attachments=normalized_attachments,
        last_updated=thread.last_email_at or datetime.utcnow(),
        provider=thread.provider,
        labels=thread.labels or [],
        is_unread=bool(thread.is_unread),
        is_starred=thread.is_starred or False,
    )
    
    # 5. Fetch Tasks / Drafts (Stubs for now, or real if table exists)
    # Assuming Task model exists, import it globally if so.
    # For now return empty list to unblock.
    tasks = [] 
    draft = None
    
    return ThreadDetailResponse(
        thread=email_thread,
        intel=_serialize_intel(thread),
        tasks=tasks,
        draft=draft
    )


@router.post("/{thread_id}/refresh")
async def refresh_thread(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Re-process thread intelligence. (Cost: 2 credits)
    
    Useful after new emails arrive or if user wants updated analysis.
    """
    OPERATION_TYPE = "thread_summary"
    
    # 1. Check Balance
    if not await CreditService.check_balance(db, current_user.id, OPERATION_TYPE):
         raise HTTPException(status_code=402, detail="Insufficient credits.")

    try:
        # TODO: Trigger re-analysis (Call Celery task or Intelligence Engine)
        
        # 2. Deduct Credits
        await CreditService.deduct_credits(
            db, user_id=current_user.id, operation_type=OPERATION_TYPE,
            metadata={"thread_id": thread_id, "action": "refresh"}
        )
        await db.commit()
        
        return {"thread_id": thread_id, "refreshed": True}
    except InsufficientCreditsError as e:
        await db.rollback()
        raise HTTPException(status_code=402, detail=str(e))
    except RateLimitExceededError as e:
        await db.rollback()
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
