"""
API Keys Models
---------------
SQLAlchemy models for developer API keys (Module 20).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text, BigInteger
from sqlalchemy.dialects.postgresql import ARRAY

from core.storage.database import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    key_prefix = Column(String(20), nullable=False)
    key_hash = Column(String(64), unique=True, nullable=False)
    
    scopes = Column(ARRAY(Text), nullable=False)
    rate_limit_per_hour = Column(Integer, default=1000)
    
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    last_used_ip = Column(String(45), nullable=True)
    usage_count = Column(BigInteger, default=0)
    
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
