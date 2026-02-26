"""
AI Core Models
--------------
SQLAlchemy models for AI processing queue and usage tracking.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Enum, Boolean, BigInteger, Date, UniqueConstraint, Float
from sqlalchemy.dialects.postgresql import JSONB
import enum

from core.storage.database import Base


class AIOperationType(str, enum.Enum):
    EMAIL_SUMMARY = "email_summary"
    THREAD_SUMMARY = "thread_summary"
    DRAFT_REPLY = "draft_reply"
    TASK_GENERATION = "task_generation"
    ATTACHMENT_SUMMARY = "attachment_summary"
    CALENDAR_DETECTION = "calendar_detection"

class AIQueueStatus(str, enum.Enum):
    PENDING = "pending"
    RESERVED = "reserved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AIProvider(str, enum.Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    CUSTOM = "custom"


class AIProcessingQueue(Base):
    """Queue for asynchronous AI operations."""
    __tablename__ = "ai_processing_queue"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    operation_type = Column(Enum(AIOperationType), nullable=False)
    entity_type = Column(String, nullable=False) # thread, email, attachment
    entity_id = Column(String, nullable=False, index=True)
    
    priority = Column(Integer, default=5) # 1=high, 10=low
    status = Column(Enum(AIQueueStatus), default=AIQueueStatus.PENDING, nullable=False)
    
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    reserved_at = Column(DateTime(timezone=True), nullable=True)
    reserved_by_worker = Column(String, nullable=True)
    reservation_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    input_context = Column(JSONB, nullable=True)
    result = Column(JSONB, nullable=True)
    metadata_json = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        # Indexes are complex to define in SQLAlchemy inline sometimes, usually better in migration script via SQL,
        # but we can declare them here if we want Alembic to pick them up.
        # For this planner, I rely on the migration script for explicit index creation.
    )


class AIUsageLog(Base):
    """Track AI API usage and costs."""
    __tablename__ = "ai_usage_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    operation_type = Column(String, nullable=False)
    provider = Column(Enum(AIProvider), nullable=False)
    model_name = Column(String, nullable=False)
    
    tokens_input = Column(Integer, nullable=False)
    tokens_output = Column(Integer, nullable=False)
    tokens_total = Column(Integer, nullable=False)
    cost_cents = Column(Integer, nullable=False)
    credits_charged = Column(Integer, nullable=True)
    
    latency_ms = Column(Integer, nullable=True)
    cache_hit = Column(Boolean, default=False)
    
    related_entity_type = Column(String, nullable=True)
    related_entity_id = Column(String, nullable=True)
    
    request_id = Column(String, nullable=True)
    error_occurred = Column(Boolean, default=False)
    error_type = Column(String, nullable=True)
    
    metadata_json = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AIUsageDailySummary(Base):
    """Pre-aggregated daily usage stats."""
    __tablename__ = "ai_usage_daily_summary"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(Date, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=True) # Null = system wide
    
    operation_type = Column(String, nullable=True)
    
    total_operations = Column(Integer, nullable=False)
    total_tokens = Column(BigInteger, nullable=False)
    total_cost_cents = Column(BigInteger, nullable=False)
    total_credits_charged = Column(BigInteger, nullable=True)
    
    avg_latency_ms = Column(Integer, nullable=True)
    cache_hit_rate = Column(Float, nullable=True) # Stored as percentage
    error_rate = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('date', 'user_id', 'operation_type', name='unique_daily_usage'),
    )
