"""
API Routes - Dashboard
----------------------
Aggregation endpoints for the main dashboard.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from pydantic import BaseModel

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User
from models.thread import Thread
from api.routes.threads import ThreadListItem
from contracts import (
    TaskDTOv1, 
    BriefingDTO,
    DashboardStats,
    DashboardData
)
from models.task import Task, TaskStatus
from core.intelligence.dashboard_briefing import get_dashboard_briefing

router = APIRouter()

@router.get("/stats", response_model=DashboardData)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get aggregated dashboard statistics and briefing.
    """
    # 1. Stats
    # Unread
    unread_stmt = select(func.count()).where(
        Thread.user_id == current_user.id,
        Thread.is_unread > 0
    )
    unread_count = (await db.execute(unread_stmt)).scalar() or 0
    
    # Urgent
    urgent_stmt = select(func.count()).where(
        Thread.user_id == current_user.id,
        Thread.urgency_score >= 80
    )
    urgent_count = (await db.execute(urgent_stmt)).scalar() or 0
    
    # Tasks Due (Pending and deadline exists)
    tasks_due_stmt = select(func.count()).where(
        Task.user_id == current_user.id,
        Task.status == TaskStatus.PENDING,
        Task.due_date != None
    )
    tasks_due_count = (await db.execute(tasks_due_stmt)).scalar() or 0
    
    # Awaiting Reply (Mock or logic: last message is from user)
    # This requires complex join (Thread -> Message order by sent_at desc limit 1).
    # For MVP, let's keep it 0 or use a simpler proxy if possible?
    # Maybe use `Thread.last_message_is_from_user` if we had it.
    awaiting_reply_count = 0 
    
    # 2. Briefing (Mock / LLM Placeholder)
    briefing = BriefingDTO(
        summary=f"You have {unread_count} unread emails. {urgent_count} require immediate attention.",
        suggested_actions=["Review urgent threads", "Check calendar"]
    )
    
    # 3. Recent Threads
    threads_stmt = (
        select(Thread)
        .where(Thread.user_id == current_user.id)
        .order_by(desc(Thread.last_email_at))
        .limit(5)
    )
    threads_result = await db.execute(threads_stmt)
    recent_threads_db = threads_result.scalars().all()
    
    recent_threads = [
        ThreadListItem(
            thread_id=t.id,
            subject=t.subject or "(No Subject)",
            summary=t.summary or "Pending analysis...",
            intent=t.intent or "processing",
            urgency_score=t.urgency_score or 0,
            last_updated=t.last_email_at or datetime.now(timezone.utc),
            has_attachments=t.has_attachments or False,
        )
        for t in recent_threads_db
    ]
    
    # 4. Priority Tasks
    tasks_stmt = (
        select(Task)
        .where(
            Task.user_id == current_user.id,
            Task.status == TaskStatus.PENDING
        )
        .order_by(desc(Task.priority_score))
        .limit(5)
    )
    tasks_result = await db.execute(tasks_stmt)
    tasks_db = tasks_result.scalars().all()
    
    priority_tasks = [
        TaskDTOv1(
            task_id=t.id,
            thread_id=t.thread_id,
            user_id=t.user_id,
            title=t.title,
            description=t.description,
            task_type=t.task_type or "other", # Default to other
            # Map model fields to contract fields with safe defaults
            priority=t.priority_level or "can_wait", # Default to can_wait
            priority_score=t.priority_score,
            priority_explanation=t.metadata_json.get("priority_explanation", ""), 
            effort=t.metadata_json.get("effort") or "quick", # Default to quick
            deadline=t.due_date, # Model: due_date
            deadline_source=t.metadata_json.get("deadline_source"), # In metadata
            status=t.status,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in tasks_db
    ]
    
    return DashboardData(
        stats=DashboardStats(
            unread=unread_count,
            unread_delta="+2 since yesterday", # Mock delta
            urgent=urgent_count,
            tasks_due=tasks_due_count,
            awaiting_reply=awaiting_reply_count
        ),
        briefing=briefing,
        # Convert Pydantic models to dicts because Contract uses List[dict] to avoid circular imports
        recent_threads=[t.model_dump() for t in recent_threads],
        priority_tasks=[t.model_dump() for t in priority_tasks]
    )


@router.get("/briefing")
async def get_realtime_ai_briefing(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get lightning-fast aggregated view of all high priority/high urgency AI discoveries.
    """
    briefing = await get_dashboard_briefing(user_id=current_user.id, db=db)
    return briefing
