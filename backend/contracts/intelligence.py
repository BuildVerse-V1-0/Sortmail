"""
Intelligence Module Contracts
-----------------------------
BOUNDARY CONTRACT: ThreadIntelV1
  - Producer: Email Intelligence Engine + Attachment Intelligence Engine
  - Consumer: All Workflow Engines (Task, Draft, Follow-up)

INTERNAL TYPES (embedded in ThreadIntelV1, not standalone contracts):
  - AttachmentIntel: Summary of individual attachments
  - ExtractedDeadline: Parsed deadline information
  - ExtractedEntity: Named entities from content

The Workflow module should NEVER need to read raw email content.
All analysis flows through the single ThreadIntelV1 contract.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Classification of email intent."""
    ACTION_REQUIRED = "action_required"
    FYI = "fyi"
    SCHEDULING = "scheduling"
    URGENT = "urgent"
    UNKNOWN = "unknown"


class ExtractedDeadline(BaseModel):
    """A deadline extracted from email text."""
    
    raw_text: str = Field(
        description="Original text that contained the deadline (e.g., 'by Friday EOD')"
    )
    normalized: Optional[datetime] = Field(
        default=None,
        description="Parsed datetime if successfully normalized"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score (0.0 to 1.0)"
    )
    source: str = Field(
        description="Which message ID this was extracted from"
    )


class ExtractedEntity(BaseModel):
    """A named entity extracted from email content."""
    
    entity_type: str = Field(
        description="Type of entity: 'person', 'company', 'amount', 'date', etc."
    )
    value: str = Field(
        description="The extracted value (e.g., 'Sarah Chen', '$50,000')"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence score (0.0 to 1.0)"
    )


class AttachmentIntel(BaseModel):
    """Intelligence extracted from a single attachment."""
    
    attachment_id: str = Field(
        description="References AttachmentRef.attachment_id from ingestion"
    )
    summary: str = Field(
        description="2-3 sentence summary of the document"
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="Bullet point list of key information"
    )
    document_type: str = Field(
        default="unknown",
        description="Classified type: 'contract', 'invoice', 'proposal', 'resume', etc."
    )
    importance: str = Field(
        default="medium",
        description="Importance level: 'high', 'medium', 'low'"
    )


class ThreadIntelV1(BaseModel):
    """
    Contract Version 1: Complete thread intelligence.
    
    This is the primary contract between Intelligence and Workflow.
    Contains all interpreted meaning from email analysis.
    
    Version History:
    - v1.0 (2026-01-18): Initial version
    """
    
    thread_id: str = Field(
        description="References EmailThreadV1.thread_id"
    )
    
    # Core Intelligence
    summary: str = Field(
        description="Executive-style summary of the entire thread"
    )
    intent: IntentType = Field(
        description="Primary intent classification"
    )
    urgency_score: int = Field(
        ge=0, le=100,
        description="Urgency score from 0 (not urgent) to 100 (critical)"
    )
    
    # Extracted Data
    main_ask: Optional[str] = Field(
        default=None,
        description="What the sender is asking for (if anything)"
    )
    decision_needed: Optional[str] = Field(
        default=None,
        description="What decision the user needs to make"
    )
    extracted_deadlines: List[ExtractedDeadline] = Field(
        default_factory=list,
        description="All detected deadlines and time references"
    )
    entities: List[ExtractedEntity] = Field(
        default_factory=list,
        description="Named entities extracted from content"
    )
    
    # Attachment Intelligence
    attachment_summaries: List[AttachmentIntel] = Field(
        default_factory=list,
        description="Intelligence for each attachment"
    )
    
    # Suggestions
    suggested_action: Optional[str] = Field(
        default=None,
        description="Recommended action for the user"
    )
    suggested_reply_points: List[str] = Field(
        default_factory=list,
        description="Key points to include in a reply"
    )
    
    # Metadata
    schema_version: str = Field(
        description="LLM model used (e.g., 'gemini-1.5-pro')"
    )
    processed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this intelligence was generated"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                "summary": "Sarah sent the final contract terms and needs approval by Friday.",
                "intent": "action_required",
                "urgency_score": 75,
                "main_ask": "Approve or request changes to contract",
                "decision_needed": "Contract approval",
                "extracted_deadlines": [],
                "entities": [],
                "attachment_summaries": [],
                "suggested_action": "Review attached contract and respond",
                "suggested_reply_points": ["Confirm receipt", "Note any concerns"],
                "schema_version": "gemini-1.5-pro",
                "processed_at": "2026-01-18T14:35:00Z"
            }
        }
