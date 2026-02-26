"""
Template Model
--------------
SQLAlchemy model for email templates.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from core.storage.database import Base


class EmailTemplate(Base):
    """Reusable email template."""
    __tablename__ = "email_templates"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=True) # Shared templates
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    subject = Column(String(500), nullable=True)
    body = Column(Text, nullable=False)
    variables = Column(JSONB, default=list) # e.g. ["name", "date"]
    
    category = Column(String(100), nullable=True)
    is_public = Column(Boolean, default=False) # Shared with team
    
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        # Indexes managed via migration
        # idx_templates_workspace handled in migration
    )
