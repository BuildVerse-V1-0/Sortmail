"""
Document Model
--------------
SQLAlchemy model for vector-indexed documents.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from core.storage import Base


class Document(Base):
    """Vector store document reference."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    attachment_id = Column(String, ForeignKey("attachments.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Vector index reference
    vector_index_id = Column(String, nullable=False)
    
    # Metadata
    doc_metadata = Column(JSONB, default=dict)
    
    # Timestamps
    indexed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
