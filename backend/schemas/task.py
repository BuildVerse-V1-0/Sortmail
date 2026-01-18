"""
Task Schemas
------------
Request/response models for task endpoints.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskUpdateRequest(BaseModel):
    """Request to update a task."""
    status: Optional[str] = None
    priority: Optional[str] = None


class TaskListResponse(BaseModel):
    """Paginated task list."""
    tasks: list
    total: int
    page: int
    per_page: int
