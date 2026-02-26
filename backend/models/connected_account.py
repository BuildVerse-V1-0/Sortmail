"""
Connected Account Model
-----------------------
SQLAlchemy model for OAuth provider connections.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, UniqueConstraint, Boolean, Integer
from sqlalchemy.dialects.postgresql import JSONB
import enum

from core.storage.database import Base


class ProviderType(str, enum.Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"

class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    DISCONNECTED = "disconnected"
    ERROR = "error"

class SyncStatus(str, enum.Enum):
    IDLE = "idle"
    SYNCING = "syncing"
    FAILED = "failed"


class ConnectedAccount(Base):
    """OAuth connected accounts per provider."""
    __tablename__ = "connected_accounts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    
    # Provider info
    provider = Column(Enum(ProviderType, native_enum=False, length=50), nullable=False)
    provider_user_id = Column(String, nullable=False)
    provider_email = Column(String, nullable=False)
    
    # Tokens (encrypt in production!)
    access_token = Column(String, nullable=False) # In prod: access_token_encrypted
    refresh_token = Column(String) # In prod: refresh_token_encrypted
    token_expires_at = Column(DateTime(timezone=True))
    scopes = Column(String, nullable=False) # Stored as comma-separated or JSON if using JSONB
    
    # Status
    status = Column(Enum(AccountStatus, native_enum=False, length=50), default=AccountStatus.ACTIVE, nullable=False)
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    
    # Sync tracking
    last_sync_at = Column(DateTime(timezone=True))
    last_history_id = Column(String)
    sync_status = Column(Enum(SyncStatus, native_enum=False, length=50), default=SyncStatus.IDLE, nullable=False)
    sync_error = Column(String)
    
    # Sync Config
    initial_sync_done = Column(Boolean, default=False)
    sync_window_days = Column(Integer, default=90)
    sync_enabled = Column(Boolean, default=True)
    sync_frequency_minutes = Column(Integer, default=15)
    last_watch_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    metadata_json = Column(JSONB, default=dict)
    
    # Timestamps & Soft Delete
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('user_id', 'provider', 'deleted_at', name='unique_user_provider_deleted'),
    )


class OAuthStateToken(Base):
    """Temporary storage for OAuth CSRF protection."""
    __tablename__ = "oauth_state_tokens"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    state_token = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, nullable=True) # Null for signup
    
    code_verifier = Column(String, nullable=False)
    provider = Column(Enum(ProviderType), nullable=False)
    
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=False)
    redirect_after_auth = Column(String, nullable=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=False)
    consumed = Column(Boolean, default=False)
    consumed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
