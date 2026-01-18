"""
User Model
----------
SQLAlchemy model for users table.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.dialects.postgresql import JSONB
import enum

from core.storage import Base


class EmailProvider(str, enum.Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"


class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String)
    picture_url = Column(String)
    
    # Provider tokens (encrypted in production!)
    provider = Column(Enum(EmailProvider), nullable=False)
    access_token = Column(String)
    refresh_token = Column(String)
    token_expires_at = Column(DateTime)
    
    # Settings
    settings = Column(JSONB, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    last_sync = Column(DateTime)
    
    # Soft delete
    is_active = Column(Boolean, default=True)
