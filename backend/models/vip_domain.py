"""
VIP Domain Model
----------------
SQLAlchemy model for user-configured VIP domains.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint

from core.storage import Base


class VIPDomain(Base):
    """User-configured VIP sender domains."""
    __tablename__ = "vip_domains"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Domain (e.g., "ceo@company.com" or "@company.com")
    domain = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('user_id', 'domain', name='unique_user_domain'),
    )
