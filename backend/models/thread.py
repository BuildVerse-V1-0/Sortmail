"""
Thread Model
------------
SQLAlchemy model for email threads.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
import enum

from core.storage.database import Base

class IntelStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Thread(Base):
    __tablename__ = "threads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    external_id = Column(String, nullable=False)  # Provider's thread ID
    
    # Thread data
    subject = Column(String)
    participants = Column(ARRAY(String))
    provider = Column(String, nullable=False)  # "gmail" or "outlook"
    
    # Meta
    labels = Column(ARRAY(String), default=list) # e.g. ["INBOX", "UNREAD", "IMPORTANT"]
    is_unread = Column(Integer, default=0) # 0=read, 1=unread (using int for bool compat if needed, or Boolean)
    is_starred = Column(Boolean, default=False)
    has_attachments = Column(Boolean, default=False)
    
    # Intelligence cache
    summary = Column(Text)
    intent = Column(String)
    urgency_score = Column(Integer)
    intel_json = Column(JSONB)  # Full ThreadIntelV1 cache
    
    # Timestamps
    last_email_at = Column(DateTime(timezone=True))
    last_synced_at = Column(DateTime(timezone=True))
    intel_generated_at = Column(DateTime(timezone=True))
    rag_embedded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False, index=True)
    
    # Message data
    from_address = Column(String, nullable=False)
    to_addresses = Column(ARRAY(String))
    cc_addresses = Column(ARRAY(String))
    subject = Column(String)
    body_text = Column(Text)
    
    # Meta
    is_from_user = Column(String, default=False)
    sent_at = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
