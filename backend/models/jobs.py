"""
Jobs & Queues Models
--------------------
SQLAlchemy models for background jobs and scheduled tasks (Module 15).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

from core.storage.database import Base
import enum


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RESERVED = "reserved"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Job(Base):
    __tablename__ = "job_queue"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String(100), nullable=False)
    priority = Column(Integer, default=5) # 1=Highest, 10=Lowest
    
    payload = Column(JSONB, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    reserved_at = Column(DateTime(timezone=True), nullable=True)
    reserved_by_worker = Column(String(100), nullable=True)
    reservation_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    scheduled_for = Column(DateTime(timezone=True), nullable=True) # Delayed jobs
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        # Indexes managed via migration
    )


class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_name = Column(String(255), unique=True, nullable=False)
    job_type = Column(String(100), nullable=False)
    
    schedule_expression = Column(String(100), nullable=False) # Cron
    payload_template = Column(JSONB, nullable=False)
    
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    next_run_at = Column(DateTime(timezone=True), nullable=False)
    
    run_count = Column(BigInteger, default=0)
    failure_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
