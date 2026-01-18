"""
API Routes - Tasks
------------------
Task management endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime

from contracts import TaskDTOv1, PriorityLevel, TaskStatus
from contracts.mocks import create_mock_task

router = APIRouter()


@router.get("/", response_model=List[TaskDTOv1])
async def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[PriorityLevel] = None,
    limit: int = Query(default=50, le=100),
):
    """
    List tasks for current user.
    
    Returns tasks sorted by priority_score descending.
    """
    # TODO: Replace with real DB query
    mock_tasks = [create_mock_task() for _ in range(3)]
    return mock_tasks


@router.get("/{task_id}", response_model=TaskDTOv1)
async def get_task(task_id: str):
    """Get a specific task by ID."""
    # TODO: Replace with real DB query
    task = create_mock_task()
    task.task_id = task_id
    return task


@router.patch("/{task_id}")
async def update_task(task_id: str, status: Optional[TaskStatus] = None):
    """Update task status."""
    # TODO: Implement task update
    return {"task_id": task_id, "status": status, "updated": True}


@router.delete("/{task_id}")
async def dismiss_task(task_id: str):
    """Dismiss a task."""
    # TODO: Implement task dismissal
    return {"task_id": task_id, "dismissed": True}
