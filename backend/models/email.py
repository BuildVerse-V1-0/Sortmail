"""
Email Model
-----------
SQLAlchemy model for raw email storage (if needed).
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey

from core.storage import Base


class Email(Base):
    """Individual email message (separate from Thread/Message if needed)."""
    __tablename__ = "emails"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False, index=True)
    
    # Email data
    external_id = Column(String, nullable=False)  # Provider's message ID
    from_address = Column(String, nullable=False)
    to_addresses = Column(Text)  # JSON array
    cc_addresses = Column(Text)  # JSON array
    subject = Column(String)
    snippet = Column(Text)  # Preview text
    body_text = Column(Text)
    body_html = Column(Text)
    
    # Flags
    is_read = Column(Boolean, default=False)
    is_starred = Column(Boolean, default=False)
    is_from_user = Column(Boolean, default=False)
    
    # Timestamps
    sent_at = Column(DateTime, nullable=False)
    received_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
