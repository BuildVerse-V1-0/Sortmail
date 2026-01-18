"""
Thread Model
------------
SQLAlchemy model for email threads.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

from core.storage import Base


class Thread(Base):
    __tablename__ = "threads"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    external_id = Column(String, nullable=False)  # Provider's thread ID
    
    # Thread data
    subject = Column(String)
    participants = Column(ARRAY(String))
    provider = Column(String, nullable=False)  # "gmail" or "outlook"
    
    # Intelligence cache
    summary = Column(Text)
    intent = Column(String)
    urgency_score = Column(Integer)
    intel_json = Column(JSONB)  # Full ThreadIntelV1 cache
    
    # Timestamps
    last_email_at = Column(DateTime)
    last_synced_at = Column(DateTime)
    intel_generated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False, index=True)
    
    # Message data
    from_address = Column(String, nullable=False)
    to_addresses = Column(ARRAY(String))
    cc_addresses = Column(ARRAY(String))
    subject = Column(String)
    body_text = Column(Text)
    
    # Meta
    is_from_user = Column(String, default=False)
    sent_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
