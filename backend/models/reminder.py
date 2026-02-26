"""
Reminder Model
--------------
SQLAlchemy model for task reminders.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey

from core.storage import Base


class Reminder(Base):
    """Task reminder storage."""
    __tablename__ = "reminders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), index=True)
    
    # Reminder details
    remind_at = Column(DateTime(timezone=True), nullable=False, index=True)
    is_triggered = Column(Boolean, default=False)
    message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
