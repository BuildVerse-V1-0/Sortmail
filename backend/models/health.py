"""
System Health & Monitoring Models
---------------------------------
SQLAlchemy models for health checks, error logs, and rate tracking (Module 16).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import JSONB

from core.storage.database import Base
import enum


class HealthStatus(str, enum.Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class ComponentName(str, enum.Enum):
    API = "api"
    DATABASE = "database"
    REDIS = "redis"
    CHROMA = "chroma"
    S3 = "s3"
    STRIPE = "stripe"
    GMAIL_API = "gmail_api"
    ANTHROPIC_API = "anthropic_api"
    CELERY_WORKERS = "celery_workers"


class ErrorSeverity(str, enum.Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RateLimitType(str, enum.Enum):
    PER_MINUTE = "per_minute"
    PER_HOUR = "per_hour"
    PER_DAY = "per_day"


class HealthCheck(Base):
    __tablename__ = "health_checks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    component = Column(Enum(ComponentName), nullable=False)
    status = Column(Enum(HealthStatus), nullable=False)
    
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    
    checked_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    metadata_json = Column(JSONB, default=dict)


class ErrorLog(Base):
    __tablename__ = "error_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    
    severity = Column(Enum(ErrorSeverity), default=ErrorSeverity.ERROR, nullable=False)
    
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    request_path = Column(String(500), nullable=True)
    request_method = Column(String(10), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    context = Column(JSONB, default=dict)
    
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class RateLimitViolation(Base):
    __tablename__ = "rate_limit_violations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    
    ip_address = Column(String(45), nullable=False, index=True)
    endpoint = Column(String(255), nullable=False)
    
    limit_type = Column(Enum(RateLimitType), nullable=False)
    limit_value = Column(Integer, nullable=False)
    actual_value = Column(Integer, nullable=False)
    
    blocked = Column(Boolean, default=True)
    user_agent = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
