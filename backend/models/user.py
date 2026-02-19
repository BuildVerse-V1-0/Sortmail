"""
User Model
----------
SQLAlchemy model for users table.
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum

from core.storage.database import Base

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"
    PENDING_VERIFICATION = "pending_verification"

class AccountType(str, enum.Enum):
    INDIVIDUAL = "individual"
    TEAM_MEMBER = "team_member"
    TEAM_ADMIN = "team_admin"
    ENTERPRISE = "enterprise"


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
    
    # Enhanced Metadata
    preferences = Column(JSONB, default={})
    metadata_json = Column(JSONB, default={})
    
    # Status & Type
    status = Column(Enum(UserStatus, name="user_status"), default=UserStatus.ACTIVE)
    account_type = Column(Enum(AccountType, name="account_type"), default=AccountType.INDIVIDUAL)
    is_superuser = Column(Boolean, default=False)
    
    # Multi-tenancy (Future)
    workspace_id = Column(String, nullable=True) # FK to workspaces.id
    
    # Audit
    last_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")


class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    token_hash = Column(String, unique=True, index=True, nullable=False)
    device_fingerprint = Column(String, nullable=True)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=False)
    
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")


class SecurityEventType(str, enum.Enum):
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGED = "password_changed"
    EMAIL_CHANGED = "email_changed"
    TWO_FACTOR_ENABLED = "2fa_enabled"
    TWO_FACTOR_DISABLED = "2fa_disabled"
    OAUTH_CONNECTED = "oauth_connected"
    OAUTH_DISCONNECTED = "oauth_disconnected"
    SESSION_REVOKED = "session_revoked"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

class SecuritySeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class UserSecurityEvent(Base):
    __tablename__ = "user_security_events"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), index=True)
    
    event_type = Column(Enum(SecurityEventType), nullable=False)
    ip_address = Column(String, nullable=False)
    user_agent = Column(String, nullable=False)
    device_fingerprint = Column(String, nullable=True)
    
    metadata_json = Column(JSONB, default={})
    severity = Column(Enum(SecuritySeverity), default=SecuritySeverity.INFO)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class WorkspacePlan(str, enum.Enum):
    TEAM = "team"
    ENTERPRISE = "enterprise"

class WorkspaceStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    plan = Column(Enum(WorkspacePlan), default=WorkspacePlan.TEAM)
    seat_limit = Column(Integer, nullable=False)
    seats_used = Column(Integer, default=1)
    
    settings = Column(JSONB, default={})
    billing_email = Column(String, nullable=True)
    status = Column(Enum(WorkspaceStatus), default=WorkspaceStatus.ACTIVE)
    
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
