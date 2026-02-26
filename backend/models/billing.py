"""
Billing Models
--------------
SQLAlchemy models for subscriptions and invoices (Module 8 Part 2).
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Enum, Date, Text
from sqlalchemy.dialects.postgresql import JSONB

from core.storage.database import Base
import enum


class SubscriptionPlan(str, enum.Enum):
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"
    PAUSED = "paused"


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    UNCOLLECTIBLE = "uncollectible"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=True)
    
    stripe_customer_id = Column(String(255), nullable=False, index=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=False)
    stripe_price_id = Column(String(255), nullable=False)
    
    plan = Column(Enum(SubscriptionPlan), nullable=False)
    status = Column(Enum(SubscriptionStatus), nullable=False, index=True)
    
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    
    cancel_at_period_end = Column(Boolean, default=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    trial_start = Column(DateTime(timezone=True), nullable=True)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    
    metadata_json = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    stripe_invoice_id = Column(String(255), unique=True, nullable=False)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default='usd')
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, index=True, nullable=False)
    
    invoice_pdf_url = Column(Text, nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    
    metadata_json = Column(JSONB, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
