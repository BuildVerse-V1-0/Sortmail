"""
Draft Model
-----------
SQLAlchemy model for draft replies.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Enum
import enum

from core.storage import Base


class ToneType(str, enum.Enum):
    BRIEF = "brief"
    NORMAL = "normal"
    FORMAL = "formal"


class Draft(Base):
    """Draft reply storage."""
    __tablename__ = "drafts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False, index=True)
    
    # Draft content
    content = Column(Text, nullable=False)
    tone = Column(Enum(ToneType), default=ToneType.NORMAL)
    placeholders_json = Column(Text)  # JSON array of placeholders
    
    # Flags
    has_unresolved_placeholders = Column(Boolean, default=False)
    references_attachments = Column(Boolean, default=False)
    references_deadlines = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Metadata
    model_version = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sent_at = Column(DateTime)
