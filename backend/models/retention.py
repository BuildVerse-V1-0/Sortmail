"""
Retention & Compliance Models
-----------------------------
SQLAlchemy models for data retention, GDPR requests, and consent records (Module 14).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

from core.storage.database import Base
import enum


class GDPRRequestType(str, enum.Enum):
    DATA_EXPORT = "data_export"
    DATA_DELETION = "data_deletion"
    DATA_RECTIFICATION = "data_rectification"
    OPT_OUT = "opt_out"


class GDPRRequestStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ConsentType(str, enum.Enum):
    TERMS_OF_SERVICE = "terms_of_service"
    PRIVACY_POLICY = "privacy_policy"
    MARKETING_EMAILS = "marketing_emails"
    DATA_PROCESSING = "data_processing"
    COOKIES = "cookies"
    ANALYTICS = "analytics"


class ConsentMethod(str, enum.Enum):
    SIGNUP = "signup"
    SETTINGS_UPDATE = "settings_update"
    EXPLICIT_CHECKBOX = "explicit_checkbox"
    IMPLIED = "implied"


class DataRetentionPolicy(Base):
    __tablename__ = "data_retention_policies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(100), nullable=False)
    retention_days = Column(Integer, nullable=False)
    
    applies_to_deleted = Column(Boolean, default=True)
    applies_to_active = Column(Boolean, default=False)
    user_configurable = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class GDPRRequest(Base):
    __tablename__ = "gdpr_requests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    request_type = Column(Enum(GDPRRequestType), nullable=False)
    status = Column(Enum(GDPRRequestStatus), default=GDPRRequestStatus.PENDING, nullable=False)
    
    requested_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    export_file_url = Column(Text, nullable=True)
    export_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    deletion_confirmed = Column(Boolean, default=False)
    deletion_completed_at = Column(DateTime(timezone=True), nullable=True)
    
    admin_notes = Column(Text, nullable=True)
    metadata_json = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        # Indexes managed via migration
    )


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    consent_type = Column(Enum(ConsentType), nullable=False)
    version = Column(String(20), nullable=False)
    consented = Column(Boolean, nullable=False)
    
    consent_method = Column(Enum(ConsentMethod), nullable=True)
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        # Indexes managed via migration
    )
