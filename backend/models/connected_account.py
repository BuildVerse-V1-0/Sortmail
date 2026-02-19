"""
Connected Account Model
-----------------------
SQLAlchemy model for OAuth provider connections.
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, UniqueConstraint
import enum

from core.storage import Base


class ProviderType(str, enum.Enum):
    GMAIL = "gmail"
    OUTLOOK = "outlook"


class ConnectedAccount(Base):
    """OAuth connected accounts per provider."""
    __tablename__ = "connected_accounts"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Provider info
    provider = Column(Enum(ProviderType), nullable=False)
    
    # Tokens (encrypt in production!)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String)
    token_expires_at = Column(DateTime)
    
    # Sync tracking
    last_sync_at = Column(DateTime)
    last_history_id = Column(String)
    sync_status = Column(String, default="idle") # idle, syncing, failed, revoked
    sync_error = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='unique_user_provider'),
    )
