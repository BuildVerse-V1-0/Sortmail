"""
Task Model
----------
SQLAlchemy model for tasks table.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum
import enum

from core.storage import Base


class TaskType(str, enum.Enum):
    REPLY = "reply"
    SCHEDULE = "schedule"
    REVIEW = "review"
    FOLLOWUP = "followup"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISMISSED = "dismissed"


class PriorityLevel(str, enum.Enum):
    DO_NOW = "do_now"
    DO_TODAY = "do_today"
    CAN_WAIT = "can_wait"


class EffortLevel(str, enum.Enum):
    QUICK = "quick"
    DEEP_WORK = "deep_work"


class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False, index=True)
    
    # Task details
    title = Column(String, nullable=False)
    description = Column(Text)
    task_type = Column(Enum(TaskType), nullable=False)
    
    # Priority
    priority = Column(Enum(PriorityLevel), default=PriorityLevel.CAN_WAIT)
    priority_score = Column(Integer, default=0)
    priority_explanation = Column(Text)
    
    # Effort
    effort = Column(Enum(EffortLevel), default=EffortLevel.QUICK)
    
    # Deadline
    deadline = Column(DateTime)
    deadline_source = Column(String)
    
    # Status
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
