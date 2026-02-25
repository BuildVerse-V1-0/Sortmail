from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User
from models.task import Task, TaskStatus as DBTaskStatus
from contracts import TaskDTOv1, PriorityLevel, TaskStatus

router = APIRouter()

@router.get("/", response_model=List[TaskDTOv1])
async def list_tasks(
    status: Optional[str] = None,
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tasks for current user, sorted by priority_score descending."""
    stmt = select(Task).where(Task.user_id == current_user.id)

    if status:
        stmt = stmt.where(Task.status == status)

    stmt = stmt.order_by(desc(Task.priority_score)).limit(limit)

    result = await db.execute(stmt)
    tasks = result.scalars().all()

    return [
        TaskDTOv1(
            task_id=t.id,
            thread_id=t.source_thread_id,   # model: source_thread_id
            user_id=t.user_id,
            title=t.title,
            description=t.description,
            task_type=t.task_type,
            priority=t.priority_level,       # model: priority_level
            priority_score=t.priority_score,
            status=t.status,
            deadline=t.due_date,             # model: due_date
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in tasks
    ]


# ─── Calendar Suggestions ──────────────────────────────────────────────────────

from models.calendar_suggestion import CalendarSuggestion
from contracts.workflow import CalendarSuggestionV1


@router.get("/calendar-suggestions", response_model=list[CalendarSuggestionV1])
async def list_calendar_suggestions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List pending AI-detected calendar suggestions."""
    try:
        stmt = (
            select(CalendarSuggestion)
            .where(
                CalendarSuggestion.user_id == current_user.id,
                CalendarSuggestion.status == "pending",
            )
            .order_by(desc(CalendarSuggestion.suggested_time))
        )
        result = await db.execute(stmt)
        suggestions = result.scalars().all()
        return [
            CalendarSuggestionV1(
                suggestion_id=s.id,
                thread_id=s.thread_id,
                title=s.title,
                suggested_time=s.suggested_time,
                duration_minutes=s.duration_minutes or 60,
                location=s.location,
                participants=s.participants or [],
                confidence=s.confidence or 0.8,
            )
            for s in suggestions
        ]
    except Exception:
        # If CalendarSuggestion table doesn't exist yet, return empty
        return []


@router.post("/calendar-suggestions/{suggestion_id}/accept")
async def accept_calendar_suggestion(
    suggestion_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a calendar suggestion as accepted."""
    try:
        stmt = select(CalendarSuggestion).where(
            CalendarSuggestion.id == suggestion_id,
            CalendarSuggestion.user_id == current_user.id,
        )
        result = await db.execute(stmt)
        suggestion = result.scalars().first()
        if suggestion:
            suggestion.status = "accepted"
            await db.commit()
    except Exception:
        pass
    return {"accepted": True}


@router.delete("/calendar-suggestions/{suggestion_id}")
async def dismiss_calendar_suggestion(
    suggestion_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dismiss a calendar suggestion."""
    try:
        stmt = select(CalendarSuggestion).where(
            CalendarSuggestion.id == suggestion_id,
            CalendarSuggestion.user_id == current_user.id,
        )
        result = await db.execute(stmt)
        suggestion = result.scalars().first()
        if suggestion:
            suggestion.status = "dismissed"
            await db.commit()
    except Exception:
        pass
    return {"dismissed": True}


@router.get("/{task_id}", response_model=TaskDTOv1)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific task by ID."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await db.execute(stmt)
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskDTOv1(
        task_id=task.id,
        thread_id=task.source_thread_id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        priority=task.priority_level,
        priority_score=task.priority_score,
        status=task.status,
        deadline=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.patch("/{task_id}")
async def update_task(
    task_id: str,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update task status."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await db.execute(stmt)
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if status:
        task.status = status
        task.updated_at = datetime.now(timezone.utc)
        await db.commit()

    return {"task_id": task_id, "status": task.status, "updated": True}


@router.delete("/{task_id}")
async def dismiss_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dismiss/cancel a task."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await db.execute(stmt)
    task = result.scalars().first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = DBTaskStatus.CANCELLED   # model: CANCELLED (no DISMISSED)
    task.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {"task_id": task_id, "dismissed": True}



# Calendar suggestions routes moved up to prevent shadowing by /{task_id}
