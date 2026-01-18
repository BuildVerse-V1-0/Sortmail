"""
Document Model
--------------
SQLAlchemy model for vector-indexed documents.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from core.storage import Base


class Document(Base):
    """Vector store document reference."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    attachment_id = Column(String, ForeignKey("attachments.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # Vector index reference
    vector_index_id = Column(String, nullable=False)
    
    # Metadata for filtering
    metadata = Column(JSONB, default={})
    
    # Timestamps
    indexed_at = Column(DateTime, default=datetime.utcnow)
