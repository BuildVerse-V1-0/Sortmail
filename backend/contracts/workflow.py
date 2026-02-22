"""
Workflow Module Contracts
-------------------------
Contracts: TaskDTOv1, DraftDTOv1, CalendarSuggestionV1, WaitingForDTOv1

Owner: Team C (Workflow)
Consumers: API Layer, Frontend

These contracts represent actionable decisions and outputs.
All data is ready for direct API/UI consumption.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Enums
# ============================================================================

class PriorityLevel(str, Enum):
    """Human-readable priority levels for UI display."""
    DO_NOW = "do_now"
    DO_TODAY = "do_today"
    CAN_WAIT = "can_wait"


class EffortLevel(str, Enum):
    """Estimated effort required for a task."""
    QUICK = "quick"       # < 5 minutes
    DEEP_WORK = "deep_work"  # > 30 minutes


class TaskType(str, Enum):
    """Type of action required."""
    REPLY = "reply"
    REVIEW = "review"
    SCHEDULE = "schedule"
    FOLLOWUP = "followup"
    OTHER = "other"


class TaskStatus(str, Enum):
    """Current status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISMISSED = "dismissed"


class ToneType(str, Enum):
    """Tone options for draft generation."""
    BRIEF = "brief"
    NORMAL = "normal"
    FORMAL = "formal"


# ============================================================================
# Supporting Models
# ============================================================================

class Placeholder(BaseModel):
    """A placeholder in a draft that needs user input."""
    
    key: str = Field(
        description="Placeholder text in draft (e.g., '[Confirm time]')"
    )
    description: str = Field(
        description="What the user should fill in"
    )
    suggested_value: Optional[str] = Field(
        default=None,
        description="Suggested value if any"
    )


# ============================================================================
# Main DTOs
# ============================================================================

class TaskDTOv1(BaseModel):
    """
    Contract Version 1: Task representation.
    
    Represents a single actionable task derived from email analysis.
    
    Version History:
    - v1.0 (2026-01-18): Initial version
    """
    
    task_id: str = Field(
        description="Unique identifier for this task"
    )
    thread_id: Optional[str] = Field(
        default=None,
        description="References the source email thread"
    )
    user_id: str = Field(
        description="Owner of this task"
    )
    
    # Core task info
    title: str = Field(
        description="Short, actionable title"
    )
    description: Optional[str] = Field(
        default=None,
        description="Additional context if needed"
    )
    task_type: TaskType = Field(
        description="Type of action required"
    )
    
    # Priority
    priority: PriorityLevel = Field(
        description="Human-readable priority level"
    )
    priority_score: int = Field(
        ge=0, le=100,
        description="Numeric score for sorting (0-100)"
    )
    priority_explanation: Optional[str] = Field(
        default=None,
        description="Why this priority was assigned (e.g., 'High: CEO + deadline tomorrow')"
    )
    
    # Effort & timing
    effort: Optional[EffortLevel] = Field(
        default=None,
        description="Estimated effort level"
    )
    deadline: Optional[datetime] = Field(
        default=None,
        description="When this task should be completed"
    )
    deadline_source: Optional[str] = Field(
        default=None,
        description="Where the deadline came from (e.g., 'Email said by Friday')"
    )
    
    # Status
    status: TaskStatus = Field(
        default=TaskStatus.PENDING,
        description="Current task status"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When task was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "task-001",
                "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-001",
                "title": "Reply to Sarah - Contract Review",
                "description": "Review contract terms and respond with approval or concerns",
                "task_type": "reply",
                "priority": "do_now",
                "priority_score": 85,
                "priority_explanation": "High: CEO sender + deadline Friday + waiting 3 days",
                "effort": "quick",
                "deadline": "2026-01-24T17:00:00Z",
                "deadline_source": "Email: 'by Friday EOD'",
                "status": "pending",
                "created_at": "2026-01-18T14:00:00Z",
                "updated_at": "2026-01-18T14:00:00Z"
            }
        }


class DraftDTOv1(BaseModel):
    """
    Contract Version 1: Draft reply representation.
    
    Contains a generated draft reply with metadata.
    
    Version History:
    - v1.0 (2026-01-18): Initial version
    """
    
    draft_id: str = Field(
        description="Unique identifier for this draft"
    )
    thread_id: str = Field(
        description="References the source email thread"
    )
    user_id: str = Field(
        description="Owner of this draft"
    )
    
    # Content
    content: str = Field(
        description="The draft text content"
    )
    tone: ToneType = Field(
        description="Tone used in generation"
    )
    
    # Placeholders
    placeholders: List[Placeholder] = Field(
        default_factory=list,
        description="Placeholders that need user input"
    )
    has_unresolved_placeholders: bool = Field(
        default=False,
        description="True if placeholders still need filling"
    )
    
    # Context flags
    references_attachments: bool = Field(
        default=False,
        description="True if draft mentions attachments"
    )
    references_deadlines: bool = Field(
        default=False,
        description="True if draft references detected deadlines"
    )
    
    # Metadata
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When draft was generated"
    )
    schema_version: str = Field(
        description="LLM model used for generation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "draft_id": "draft-001",
                "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-001",
                "content": "Hi Sarah,\n\nThank you for sending the contract. I've reviewed the terms and [approve/request changes].\n\nBest regards",
                "tone": "normal",
                "placeholders": [
                    {"key": "[approve/request changes]", "description": "Confirm your decision", "suggested_value": None}
                ],
                "has_unresolved_placeholders": True,
                "references_attachments": True,
                "references_deadlines": False,
                "created_at": "2026-01-18T14:30:00Z",
                "schema_version": "gemini-1.5-pro"
            }
        }


class CalendarSuggestionV1(BaseModel):
    """
    Contract Version 1: Calendar event suggestion.
    
    Suggests a calendar event based on detected meeting times or deadlines.
    IMPORTANT: This is a SUGGESTION only. System never auto-books.
    
    Version History:
    - v1.0 (2026-01-18): Initial version
    """
    
    suggestion_id: str = Field(
        description="Unique identifier for this suggestion"
    )
    thread_id: str = Field(
        description="References the source email thread"
    )
    user_id: str = Field(
        description="User receiving this suggestion"
    )
    
    # Event details
    title: str = Field(
        description="Suggested event title"
    )
    suggested_time: datetime = Field(
        description="Detected/suggested event time"
    )
    duration_minutes: int = Field(
        default=30,
        ge=5,
        description="Suggested duration in minutes"
    )
    location: Optional[str] = Field(
        default=None,
        description="Location if detected"
    )
    
    # Source
    extracted_from: str = Field(
        description="The text that triggered this suggestion"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in the extraction"
    )
    
    # Status
    is_accepted: bool = Field(
        default=False,
        description="User accepted this suggestion"
    )
    is_dismissed: bool = Field(
        default=False,
        description="User dismissed this suggestion"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When suggestion was created"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "suggestion_id": "cal-001",
                "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-001",
                "title": "Sync call with Sarah",
                "suggested_time": "2026-01-21T14:00:00Z",
                "duration_minutes": 30,
                "location": None,
                "extracted_from": "Tuesday at 2pm works for me",
                "confidence": 0.85,
                "is_accepted": False,
                "is_dismissed": False,
                "created_at": "2026-01-18T14:30:00Z"
            }
        }


class WaitingForDTOv1(BaseModel):
    """
    Contract Version 1: Waiting-for tracking.
    
    Tracks threads where user is waiting for a reply.
    
    Version History:
    - v1.0 (2026-01-18): Initial version
    """
    
    waiting_id: str = Field(
        description="Unique identifier"
    )
    thread_id: str = Field(
        description="References the email thread"
    )
    user_id: str = Field(
        description="User who is waiting"
    )
    
    # Tracking
    last_sent_at: datetime = Field(
        description="When the user last sent a message in this thread"
    )
    days_waiting: int = Field(
        ge=0,
        description="Number of days waiting for response"
    )
    recipient: str = Field(
        description="Who we're waiting for (email address)"
    )
    
    # Status
    reminded: bool = Field(
        default=False,
        description="Whether user has been reminded"
    )
    last_reminded_at: Optional[datetime] = Field(
        default=None,
        description="When the last reminder was sent"
    )
    
    # Thread context (for quick display)
    thread_subject: str = Field(
        description="Subject line for display"
    )
    thread_summary: str = Field(
        description="Brief summary for display"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "waiting_id": "wait-001",
                "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-001",
                "last_sent_at": "2026-01-13T10:00:00Z",
                "days_waiting": 5,
                "recipient": "john@bigclient.com",
                "reminded": False,
                "last_reminded_at": None,
                "thread_subject": "Proposal Follow-up",
                "thread_summary": "Sent proposal, awaiting feedback"
            }
        }
