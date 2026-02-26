"""
Analytics Models
----------------
SQLAlchemy models for user activity and system analytics (Module 11).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text, Date, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

from core.storage.database import Base
import enum


class ActionType(str, enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    EMAIL_SENT = "email_sent"
    EMAIL_READ = "email_read"
    THREAD_ARCHIVED = "thread_archived"
    SEARCH_PERFORMED = "search_performed"
    RULE_CREATED = "rule_created"
    CREDITS_PURCHASED = "credits_purchased"
    SETTINGS_UPDATED = "settings_updated"


class UserActivityLog(Base):
    __tablename__ = "user_activity_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    action_type = Column(Enum(ActionType), nullable=False)
    description = Column(Text, nullable=True)
    metadata_json = Column(JSONB, default=dict)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class UserAnalyticsDaily(Base):
    __tablename__ = "user_analytics_daily"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    
    emails_received = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    threads_processed = Column(Integer, default=0)
    time_saved_minutes = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        # Unique constraint managed via migration/index
    )


class SystemAnalyticsDaily(Base):
    __tablename__ = "system_analytics_daily"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    date = Column(Date, unique=True, nullable=False)
    
    total_users = Column(Integer, default=0)
    active_users_daily = Column(Integer, default=0)
    total_emails_processed = Column(BigInteger, default=0)
    total_api_calls = Column(BigInteger, default=0)
    revenue_cents = Column(BigInteger, default=0)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
