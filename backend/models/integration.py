"""
Integration Models
------------------
SQLAlchemy models for third-party integrations (Module 10).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

from core.storage.database import Base
import enum


class IntegrationType(str, enum.Enum):
    SLACK = "slack"
    WEBHOOK = "webhook"
    ZAPIER = "zapier"
    ASANA = "asana"
    NOTION = "notion"
    CUSTOM = "custom"


class IntegrationStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class IntegrationLogStatus(str, enum.Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=True)
    
    integration_type = Column(Enum(IntegrationType), nullable=False)
    name = Column(String(255), nullable=False)
    
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.ACTIVE, nullable=False)
    config = Column(JSONB, nullable=False, default=dict)
    credentials_encrypted = Column(Text, nullable=True)
    
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    trigger_count = Column(BigInteger, default=0)
    error_count = Column(Integer, default=0)
    
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    
    metadata_json = Column(JSONB, default=dict)
    
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        # Indexes managed via migration
    )


class IntegrationLog(Base):
    __tablename__ = "integration_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    integration_id = Column(String, ForeignKey("integrations.id"), nullable=False, index=True)
    
    trigger_type = Column(String(100), nullable=False)
    payload = Column(JSONB, nullable=False)
    response = Column(JSONB, nullable=True)
    
    status = Column(Enum(IntegrationLogStatus), nullable=False)
    error_message = Column(Text, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
