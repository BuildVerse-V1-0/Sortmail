"""
Mock Data for Contract Testing
------------------------------
Provides realistic mock data for BOUNDARY CONTRACTS:
  - EmailThreadV1 (Ingestion → Intelligence)
  - ThreadIntelV1 (Intelligence → Workflow)  
  - TaskDTOv1, DraftDTOv1, etc. (Workflow → API)

Use these for parallel team development and integration testing.
"""

from datetime import datetime, timedelta, timezone
from .ingestion import AttachmentRef, EmailMessage, EmailThreadV1
from .intelligence import (
    IntentType, ExtractedDeadline, ExtractedEntity, 
    AttachmentIntel, ThreadIntelV1
)
from .workflow import (
    PriorityLevel, EffortLevel, TaskType, TaskStatus, ToneType,
    Placeholder, TaskDTOv1, DraftDTOv1, CalendarSuggestionV1, WaitingForDTOv1
)


# ============================================================================
# Mock Ingestion Data
# ============================================================================

def create_mock_attachment() -> AttachmentRef:
    """Create a realistic attachment reference."""
    return AttachmentRef(
        attachment_id="att-550e8400-e29b-41d4-a716-446655440001",
        filename="Contract_ClientA_Jan2026.pdf",
        original_filename="scan001.pdf",
        mime_type="application/pdf",
        storage_path="/storage/attachments/att-550e8400.pdf",
        size_bytes=245760,
    )


def create_mock_email_message(
    is_from_user: bool = False,
    hours_ago: int = 0
) -> EmailMessage:
    """Create a realistic email message."""
    return EmailMessage(
        message_id=f"msg-{hours_ago:03d}",
        from_address="sarah@client.com" if not is_from_user else "you@company.com",
        to_addresses=["you@company.com"] if not is_from_user else ["sarah@client.com"],
        cc_addresses=[],
        subject="Contract Review - Final Terms",
        body_text="""Hi,

Please find the final contract terms attached. We need your approval by Friday EOD.

Key changes from the last version:
- Payment terms moved to NET 30
- Liability cap increased to $500K

Let me know if you have any questions.

Best,
Sarah""",
        sent_at=datetime.now(timezone.utc) - timedelta(hours=hours_ago),
        received_at=datetime.now(timezone.utc) - timedelta(hours=hours_ago) + timedelta(minutes=1),
        is_from_user=is_from_user,
    )


def create_mock_email_thread() -> EmailThreadV1:
    """Create a complete mock email thread."""
    return EmailThreadV1(
        thread_id="thread-550e8400-e29b-41d4-a716-446655440000",
        external_id="18d5f6a7b8c9d0e1",
        subject="Contract Review - Final Terms",
        participants=["sarah@client.com", "you@company.com"],
        messages=[
            create_mock_email_message(is_from_user=True, hours_ago=48),
            create_mock_email_message(is_from_user=False, hours_ago=2),
        ],
        attachments=[create_mock_attachment()],
        last_updated=datetime.now(timezone.utc) - timedelta(hours=2),
        provider="gmail",
    )


# ============================================================================
# Mock Intelligence Data
# ============================================================================

def create_mock_deadline() -> ExtractedDeadline:
    """Create a realistic extracted deadline."""
    return ExtractedDeadline(
        raw_text="by Friday EOD",
        normalized=datetime.now(timezone.utc) + timedelta(days=3),
        confidence=0.92,
        source="msg-002",
    )


def create_mock_entity() -> ExtractedEntity:
    """Create a realistic extracted entity."""
    return ExtractedEntity(
        entity_type="amount",
        value="$500K",
        confidence=0.95,
    )


def create_mock_attachment_intel() -> AttachmentIntel:
    """Create mock attachment intelligence."""
    return AttachmentIntel(
        attachment_id="att-550e8400-e29b-41d4-a716-446655440001",
        summary="Master Services Agreement between Company and ClientA. Covers 12-month engagement with defined deliverables and payment terms.",
        key_points=[
            "12-month contract term",
            "NET 30 payment terms",
            "$500K liability cap",
            "Includes IP assignment clause",
        ],
        document_type="contract",
        importance="high",
    )


def create_mock_thread_intel() -> ThreadIntelV1:
    """Create complete mock thread intelligence."""
    return ThreadIntelV1(
        thread_id="thread-550e8400-e29b-41d4-a716-446655440000",
        summary="Sarah sent the final contract terms and needs approval by Friday EOD. Key changes include NET 30 payment terms and $500K liability cap.",
        intent=IntentType.ACTION_REQUIRED,
        urgency_score=75,
        main_ask="Approve or request changes to contract",
        decision_needed="Contract approval",
        extracted_deadlines=[create_mock_deadline()],
        entities=[create_mock_entity()],
        attachment_summaries=[create_mock_attachment_intel()],
        suggested_action="Review attached contract and respond with approval or concerns",
        suggested_reply_points=[
            "Confirm receipt of contract",
            "Acknowledge the updated terms",
            "State your decision",
        ],
        model_version="gemini-1.5-pro",
        processed_at=datetime.now(timezone.utc),
        schema_version="1.0",
    )


# ============================================================================
# Mock Workflow Data
# ============================================================================

def create_mock_task() -> TaskDTOv1:
    """Create a realistic task."""
    return TaskDTOv1(
        task_id="task-001",
        thread_id="thread-550e8400-e29b-41d4-a716-446655440000",
        user_id="user-001",
        title="Reply to Sarah - Contract Review",
        description="Review contract terms and respond with approval or concerns",
        task_type=TaskType.REPLY,
        priority=PriorityLevel.DO_NOW,
        priority_score=85,
        priority_explanation="High: Key client + deadline Friday + contract value significant",
        effort=EffortLevel.QUICK,
        deadline=datetime.now(timezone.utc) + timedelta(days=3),
        deadline_source="Email: 'by Friday EOD'",
        status=TaskStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def create_mock_draft() -> DraftDTOv1:
    """Create a realistic draft reply."""
    return DraftDTOv1(
        draft_id="draft-001",
        thread_id="thread-550e8400-e29b-41d4-a716-446655440000",
        user_id="user-001",
        content="""Hi Sarah,

Thank you for sending over the final contract. I've reviewed the updated terms including the NET 30 payment schedule and $500K liability cap.

[Confirm approval OR request specific changes]

I'll have this finalized by Friday EOD as requested.

Best regards""",
        tone=ToneType.NORMAL,
        placeholders=[
            Placeholder(
                key="[Confirm approval OR request specific changes]",
                description="State your decision on the contract",
                suggested_value="Everything looks good - approved",
            )
        ],
        has_unresolved_placeholders=True,
        references_attachments=True,
        references_deadlines=True,
        created_at=datetime.now(timezone.utc),
        model_version="gemini-1.5-pro",
        schema_version="1.0",
    )


def create_mock_calendar_suggestion() -> CalendarSuggestionV1:
    """Create a realistic calendar suggestion."""
    return CalendarSuggestionV1(
        suggestion_id="cal-001",
        thread_id="thread-550e8400-e29b-41d4-a716-446655440000",
        user_id="user-001",
        title="Contract review deadline",
        suggested_time=datetime.now(timezone.utc) + timedelta(days=3, hours=-2),
        duration_minutes=30,
        location=None,
        extracted_from="by Friday EOD",
        confidence=0.85,
        is_accepted=False,
        is_dismissed=False,
        created_at=datetime.now(timezone.utc),
    )


def create_mock_waiting_for() -> WaitingForDTOv1:
    """Create a realistic waiting-for entry."""
    return WaitingForDTOv1(
        waiting_id="wait-001",
        thread_id="thread-other-123",
        user_id="user-001",
        last_sent_at=datetime.now(timezone.utc) - timedelta(days=5),
        days_waiting=5,
        recipient="john@bigclient.com",
        reminded=False,
        last_reminded_at=None,
        thread_subject="Proposal Follow-up",
        thread_summary="Sent proposal for Q2 project, awaiting feedback on pricing",
    )
