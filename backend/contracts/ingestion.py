"""
Ingestion Module Contracts
--------------------------
Contract: EmailThreadV1

Owner: Team A (Ingestion)
Consumers: Team B (Intelligence)

These contracts represent clean, normalized, provider-agnostic email data.
No Gmail/Outlook specific fields should leak through.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class AttachmentRef(BaseModel):
    """Reference to an extracted and stored attachment."""
    
    attachment_id: str = Field(
        description="Internal UUID for this attachment"
    )
    email_id: str = Field(
        default="",
        description="ID of the email this attachment belongs to (msg-{provider_id})"
    )
    filename: str = Field(
        description="Smart/contextual filename (e.g., Contract_ClientA_2026.pdf)"
    )
    original_filename: str = Field(
        description="Original filename from the email"
    )
    mime_type: str = Field(
        description="MIME type (e.g., application/pdf)"
    )
    storage_path: str = Field(
        default="",
        description="Path where file is stored (local or cloud)"
    )
    size_bytes: int = Field(
        ge=0,
        description="File size in bytes"
    )


class EmailMessage(BaseModel):
    """A single email message within a thread."""
    
    message_id: str = Field(
        description="Internal UUID for this message"
    )
    from_address: str = Field(
        description="Sender email address (normalized)"
    )
    to_addresses: List[str] = Field(
        default_factory=list,
        description="List of recipient email addresses"
    )
    cc_addresses: List[str] = Field(
        default_factory=list,
        description="List of CC email addresses"
    )
    subject: str = Field(
        description="Email subject line"
    )
    body_text: str = Field(
        description="Plain text version of email body"
    )
    body_html: str = Field(
        default="",
        description="HTML version of email body"
    )
    sent_at: datetime = Field(
        description="When the email was sent"
    )
    received_at: datetime = Field(
        description="When the email was received by the provider"
    )
    is_from_user: bool = Field(
        default=False,
        description="True if this message was sent by the connected user"
    )
    labels: List[str] = Field(
        default_factory=list,
        description="Provider-specific labels (e.g. UNREAD, SENT)"
    )


class EmailThreadV1(BaseModel):
    """
    Contract Version 1: Complete email thread data.
    
    This is the primary contract between Ingestion and Intelligence.
    All fields are provider-agnostic and normalized.
    
    Version History:
    - v1.0 (2026-01-18): Initial version
    """
    
    thread_id: str = Field(
        description="Internal UUID for this thread"
    )
    external_id: str = Field(
        description="Provider-specific thread ID (Gmail/Outlook)"
    )
    subject: str = Field(
        description="Thread subject line"
    )
    participants: List[str] = Field(
        default_factory=list,
        description="All email addresses that participated in this thread"
    )
    messages: List[EmailMessage] = Field(
        default_factory=list,
        description="Messages in chronological order (oldest first)"
    )
    attachments: List[AttachmentRef] = Field(
        default_factory=list,
        description="All attachments from all messages in thread"
    )
    last_updated: datetime = Field(
        description="Timestamp of most recent message"
    )
    provider: str = Field(
        description="Email provider: 'gmail' or 'outlook'"
    )
    labels: List[str] = Field(
        default_factory=list,
        description="Aggregated labels e.g. ['INBOX', 'UNREAD', 'IMPORTANT']"
    )
    is_unread: bool = Field(
        default=False,
        description="True if any message in thread is unread"
    )
    is_starred: bool = Field(
        default=False,
        description="True if thread is starred/flagged"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                "external_id": "18d5f6a7b8c9d0e1",
                "subject": "Contract Review - Final Terms",
                "participants": ["sarah@client.com", "you@company.com"],
                "messages": [],
                "attachments": [],
                "last_updated": "2026-01-18T14:30:00Z",
                "provider": "gmail"
            }
        }
