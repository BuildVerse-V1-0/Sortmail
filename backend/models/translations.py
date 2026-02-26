"""
Multi-Language Translation Models
---------------------------------
SQLAlchemy models for UI translations (Module 19).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text, UniqueConstraint

from core.storage.database import Base


class Translation(Base):
    __tablename__ = "translations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(255), nullable=False)
    locale = Column(String(10), nullable=False)
    
    value = Column(Text, nullable=False)
    context = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('key', 'locale', name='uq_translation_key_locale'),
    )
