"""
Calendar Suggestion Model
-------------------------
SQLAlchemy model for calendar event suggestions.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, Enum, Date
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum

from core.storage.database import Base


class CalendarSuggestionStatus(str, enum.Enum):
    SUGGESTED = "suggested"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class CalendarSuggestion(Base):
    """AI-suggested calendar events."""
    __tablename__ = "calendar_suggestions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    email_id = Column(String, ForeignKey("emails.id"), nullable=False, index=True)
    
    # Suggestion details
    event_type = Column(String, nullable=False, default="meeting") # meeting, deadline, recurring, appointment
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    suggested_date = Column(Date, nullable=True)
    suggested_time = Column(DateTime(timezone=True), nullable=True) # Time or DateTime
    suggested_end_time = Column(DateTime(timezone=True), nullable=True)
    suggested_timezone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    participants = Column(ARRAY(String), default=list)
    
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String, nullable=True)
    
    confidence_score = Column(Integer, nullable=False) # Scaled decimal
    status = Column(Enum(CalendarSuggestionStatus), default=CalendarSuggestionStatus.SUGGESTED, nullable=False)
    
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    external_calendar_event_id = Column(String, nullable=True)
    
    metadata_json = Column(JSONB, default=dict)
    
    # Timestamps
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        # Indexes managed in migration
    )
