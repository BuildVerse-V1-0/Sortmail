"""
Attachment Model
----------------
SQLAlchemy model for email attachments.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey

from core.storage import Base


class Attachment(Base):
    """Email attachment storage."""
    __tablename__ = "attachments"
    
    id = Column(String, primary_key=True)
    message_id = Column(String, ForeignKey("messages.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # File info
    filename = Column(String, nullable=False)
    original_filename = Column(String)
    mime_type = Column(String, nullable=False)
    size_bytes = Column(Integer, default=0)
    storage_path = Column(String)
    
    # Intelligence cache
    summary = Column(String)
    key_points = Column(String)  # JSON array
    document_type = Column(String)  # contract, invoice, etc.
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)  # When AI processed it
