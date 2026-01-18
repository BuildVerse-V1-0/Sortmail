"""
Waiting For Model
-----------------
SQLAlchemy model for follow-up tracking.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Boolean, ForeignKey, UniqueConstraint

from core.storage import Base


class WaitingFor(Base):
    """Track threads waiting for reply."""
    __tablename__ = "waiting_for"
    
    id = Column(String, primary_key=True)
    thread_id = Column(String, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Tracking info
    last_sent_at = Column(DateTime, nullable=False)
    days_waiting = Column(Integer, default=0)
    reminded = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('thread_id', 'user_id', name='unique_thread_user_waiting'),
    )
