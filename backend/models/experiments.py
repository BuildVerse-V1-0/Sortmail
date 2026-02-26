"""
Experiments & Feature Flags Models
----------------------------------
SQLAlchemy models for feature flags and A/B testing (Module 13).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB

from core.storage.database import Base
import enum


class FeatureFlagType(str, enum.Enum):
    BOOLEAN = "boolean"
    STRING = "string"
    NUMBER = "number"
    JSON = "json"


class ExperimentStatus(str, enum.Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    flag_key = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    flag_type = Column(Enum(FeatureFlagType), default=FeatureFlagType.BOOLEAN, nullable=False)
    default_value = Column(JSONB, nullable=False)
    
    is_active = Column(Boolean, default=True)
    rollout_percentage = Column(Integer, default=0)
    targeting_rules = Column(JSONB, default=list)
    
    created_by_admin_id = Column(String, ForeignKey("admin_users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserFeatureOverride(Base):
    __tablename__ = "user_feature_overrides"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    feature_flag_id = Column(String, ForeignKey("feature_flags.id"), nullable=False, index=True)
    
    override_value = Column(JSONB, nullable=False)
    reason = Column(Text, nullable=True)
    set_by_admin_id = Column(String, ForeignKey("admin_users.id"), nullable=True)
    
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('user_id', 'feature_flag_id', name='uq_user_feature_override'),
    )


class ABExperiment(Base):
    __tablename__ = "ab_experiments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_key = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=True)
    
    variants = Column(JSONB, nullable=False)
    traffic_allocation = Column(JSONB, nullable=False)
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(ExperimentStatus), default=ExperimentStatus.DRAFT, nullable=False)
    winning_variant = Column(String(50), nullable=True)
    
    created_by_admin_id = Column(String, ForeignKey("admin_users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ABExperimentAssignment(Base):
    __tablename__ = "ab_experiment_assignments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    experiment_id = Column(String, ForeignKey("ab_experiments.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    variant_key = Column(String(50), nullable=False)
    assigned_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        UniqueConstraint('experiment_id', 'user_id', name='uq_experiment_user_assignment'),
        # Indexes managed via migration
    )
