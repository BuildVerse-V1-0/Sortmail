"""
Attachment Model
----------------
SQLAlchemy model for email attachments.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Enum, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
import enum

from core.storage.database import Base

class StorageProvider(str, enum.Enum):
    S3 = "s3"
    R2 = "r2"
    GCS = "gcs"

class AttachmentStatus(str, enum.Enum):
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"
    SKIPPED = "skipped"
    QUARANTINED = "quarantined"

class VectorSourceType(str, enum.Enum):
    EMAIL_BODY = "email_body"
    ATTACHMENT = "attachment"
    SUMMARY = "summary"
    TASK_DESCRIPTION = "task_description"


class Attachment(Base):
    """Email attachment storage."""
    __tablename__ = "attachments"
    
    id = Column(String, primary_key=True)
    # FK to emails table (not messages) — only email_id column exists in DB
    email_id = Column(String, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)

    
    # File info
    external_id = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    filename_sanitized = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    sha256_hash = Column(String, nullable=True, index=True)
    
    # Storage
    storage_provider = Column(Enum(StorageProvider), default=StorageProvider.S3)
    storage_path = Column(Text, nullable=True)
    storage_bucket = Column(String, nullable=True)
    
    # Processing Status
    status = Column(Enum(AttachmentStatus), default=AttachmentStatus.PENDING)
    skip_reason = Column(String, nullable=True)
    
    # Extraction & AI
    extracted_text = Column(Text, nullable=True)
    extraction_method = Column(String, nullable=True)
    extraction_language = Column(String, nullable=True)
    extraction_confidence = Column(Integer, nullable=True) # Decimal in prompt, Integer scaled 0-100 here effectively or Float
    chunk_count = Column(Integer, default=0)
    
    virus_scan_result = Column(String, nullable=True)
    virus_scan_details = Column(Text, nullable=True)
    
    metadata_json = Column(JSONB, default={})
    
    # Timestamps
    downloaded_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('email_id', 'sha256_hash', name='unique_email_attachment_hash'),
    )


class VectorDocument(Base):
    """Vector database chunk tracking."""
    __tablename__ = "vector_documents"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    source_type = Column(Enum(VectorSourceType), nullable=False)
    source_id = Column(String, nullable=False, index=True) # email_id, attachment_id
    
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_tokens = Column(Integer, nullable=False)
    embedding_model = Column(String, nullable=False)
    
    vector_db_id = Column(String, unique=True, nullable=False) # Chroma ID
    vector_db_collection = Column(String, nullable=False)
    
    indexed_at = Column(DateTime, nullable=False)
    metadata_json = Column(JSONB, default={})
    
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        # Index for user params
    )
