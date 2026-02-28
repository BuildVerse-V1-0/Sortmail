"""
Attachment Model
----------------
SQLAlchemy model for email attachments.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, BigInteger, Float, ForeignKey, Text, Enum, UniqueConstraint
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
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # FK to emails table (not messages) — only email_id column exists in DB
    email_id = Column(String, ForeignKey("emails.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    
    # File info
    external_id = Column(String, nullable=True)
    filename = Column(String, nullable=False)
    filename_sanitized = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size_bytes = Column(BigInteger, nullable=False)
    sha256_hash = Column(String, nullable=False, index=True)
    
    # Storage
    storage_provider = Column(Enum(StorageProvider), default=StorageProvider.S3, nullable=False)
    storage_path = Column(Text, nullable=True)
    storage_bucket = Column(String, nullable=True)
    
    # Processing Status
    status = Column(Enum(AttachmentStatus), default=AttachmentStatus.PENDING, nullable=False)
    skip_reason = Column(String, nullable=True)
    
    # Extraction & AI
    extracted_text = Column(Text, nullable=True)
    intel_json = Column(JSONB, nullable=True) # Cached Gemini Flash intelligence
    extraction_method = Column(String, nullable=True)
    extraction_language = Column(String, nullable=True)
    extraction_confidence = Column(Float, nullable=True)
    chunk_count = Column(Integer, default=0)
    
    virus_scan_result = Column(String, nullable=True)
    virus_scan_details = Column(Text, nullable=True)
    
    metadata_json = Column(JSONB, default=dict)
    
    # Timestamps
    downloaded_at = Column(DateTime(timezone=True), nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('email_id', 'sha256_hash', name='unique_email_attachment_hash'),
    )


class VectorDocument(Base):
    """Vector database chunk tracking."""
    __tablename__ = "vector_documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    source_type = Column(Enum(VectorSourceType), nullable=False)
    source_id = Column(String, nullable=False, index=True) # email_id, attachment_id
    
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_tokens = Column(Integer, nullable=False)
    embedding_model = Column(String, nullable=False)
    
    vector_db_id = Column(String, unique=True, nullable=False) # Chroma ID
    vector_db_collection = Column(String, nullable=False)
    
    indexed_at = Column(DateTime(timezone=True), nullable=False)
    metadata_json = Column(JSONB, default=dict)
    
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('source_id', 'chunk_index', name='unique_document_chunk'),
    )
