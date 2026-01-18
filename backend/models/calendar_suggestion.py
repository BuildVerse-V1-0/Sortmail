"""
Calendar Suggestion Model
-------------------------
SQLAlchemy model for calendar event suggestions.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey

from core.storage import Base


class CalendarSuggestion(Base):
    """AI-suggested calendar events."""
    __tablename__ = "calendar_suggestions"
    
    id = Column(String, primary_key=True)
    thread_id = Column(String, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Suggestion details
    title = Column(String(512), nullable=False)
    suggested_time = Column(DateTime)
    extracted_from = Column(Text)  # Original text that triggered suggestion
    
    # Status
    is_accepted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
