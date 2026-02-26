"""
Draft Model
-----------
SQLAlchemy model for draft replies.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Enum, Integer
from sqlalchemy.dialects.postgresql import JSONB
import enum

from core.storage.database import Base


class DraftTone(str, enum.Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CONCISE = "concise"
    FORMAL = "formal"
    ASSERTIVE = "assertive"
    CUSTOM = "custom"

ToneType = DraftTone  # Alias for backward compatibility


class DraftStatus(str, enum.Enum):
    GENERATED = "generated"
    EDITED = "edited"
    SENT = "sent"
    DISCARDED = "discarded"


class DraftFeedback(str, enum.Enum):
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    NEUTRAL = "neutral"


class Draft(Base):
    """Draft reply storage."""
    __tablename__ = "drafts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False, index=True)
    
    reply_to_email_id = Column(String, ForeignKey("emails.id"), nullable=True)
    
    # Draft content
    tone = Column(Enum(DraftTone), default=DraftTone.PROFESSIONAL, nullable=False)
    custom_instructions = Column(Text, nullable=True)
    subject = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    
    generation_model = Column(String, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    cost_cents = Column(Integer, nullable=True)
    
    status = Column(Enum(DraftStatus), default=DraftStatus.GENERATED, nullable=False)
    user_edited = Column(Boolean, default=False)
    
    copied_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    feedback = Column(Enum(DraftFeedback), nullable=True)
    feedback_comment = Column(Text, nullable=True)
    
    metadata_json = Column(JSONB, default=dict)
    version = Column(Integer, default=0)
    
    # Timestamps
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        # Indexes managed via migration
    )
