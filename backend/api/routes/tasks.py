from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User
from models.task import Task, TaskStatus as DBTaskStatus, PriorityLevel as DBPriorityLevel
from contracts import TaskDTOv1, PriorityLevel, TaskStatus

router = APIRouter()

@router.get("/", response_model=List[TaskDTOv1])
async def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[PriorityLevel] = None,
    limit: int = Query(default=50, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List tasks for current user.
    
    Returns tasks sorted by priority_score descending.
    """
    stmt = select(Task).where(Task.user_id == current_user.id)
    
    if status:
        stmt = stmt.where(Task.status == status)
    else:
        # Default: exclude completed/dismissed if not specified? 
        # Usually dashboard wants pending.
        # But if status is None, maybe return all?
        # Let's filter out DISMISSED by default if not requested?
        # For now, simplistic: if None, return all (maybe UI filters).
        pass
        
    if priority:
        stmt = stmt.where(Task.priority == priority)
        
    stmt = stmt.order_by(desc(Task.priority_score)).limit(limit)
    
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    
    return [
        TaskDTOv1(
            task_id=t.id,
            thread_id=t.thread_id,
            user_id=t.user_id,
            title=t.title,
            description=t.description,
            task_type=t.task_type,
            priority=t.priority,
            priority_score=t.priority_score,
            priority_explanation=t.priority_explanation,
            effort=t.effort,
            deadline=t.deadline,
            deadline_source=t.deadline_source,
            status=t.status,
            created_at=t.created_at,
            updated_at=t.updated_at
        )
        for t in tasks
    ]


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
        thread_id=task.thread_id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        task_type=task.task_type,
        priority=task.priority,
        priority_score=task.priority_score,
        priority_explanation=task.priority_explanation,
        effort=task.effort,
        deadline=task.deadline,
        deadline_source=task.deadline_source,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.patch("/{task_id}")
async def update_task(
    task_id: str, 
    status: Optional[TaskStatus] = None,
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
        task.updated_at = datetime.utcnow()
        await db.commit()
    
    return {"task_id": task_id, "status": task.status, "updated": True}


@router.delete("/{task_id}")
async def dismiss_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dismiss a task."""
    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    result = await db.execute(stmt)
    task = result.scalars().first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    task.status = DBTaskStatus.DISMISSED
    task.updated_at = datetime.utcnow()
    await db.commit()
    
    return {"task_id": task_id, "dismissed": True}
