"""
Email Rules & Automation Models
-------------------------------
SQLAlchemy models for user-defined email rules and automation (Module 18).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text, BigInteger
from sqlalchemy.dialects.postgresql import JSONB

from core.storage.database import Base


class EmailRule(Base):
    __tablename__ = "email_rules"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=0)
    
    is_active = Column(Boolean, default=True)
    conditions = Column(JSONB, nullable=False) # Match criteria
    actions = Column(JSONB, nullable=False) # Execution steps
    
    match_all_conditions = Column(Boolean, default=True)
    apply_to_existing = Column(Boolean, default=False)
    
    times_triggered = Column(BigInteger, default=0)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class RuleExecutionLog(Base):
    __tablename__ = "rule_execution_log"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id = Column(String, ForeignKey("email_rules.id"), nullable=False, index=True)
    
    thread_id = Column(String, ForeignKey("threads.id"), nullable=False)
    email_id = Column(String, ForeignKey("emails.id"), nullable=False)
    
    conditions_matched = Column(JSONB, nullable=False)
    actions_executed = Column(JSONB, nullable=False)
    
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
