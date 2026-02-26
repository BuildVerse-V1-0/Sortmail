"""
Contract Tests
--------------
Tests to ensure contracts are valid and maintain backward compatibility.
Run these before any PR merge.
"""

import pytest
from datetime import datetime, timedelta, timezone

from contracts import (
    # Ingestion
    AttachmentRef,
    EmailMessage,
    EmailThreadV1,
    # Intelligence
    IntentType,
    ExtractedDeadline,
    ExtractedEntity,
    AttachmentIntel,
    ThreadIntelV1,
    # Workflow
    PriorityLevel,
    EffortLevel,
    TaskType,
    TaskStatus,
    ToneType,
    Placeholder,
    TaskDTOv1,
    DraftDTOv1,
    CalendarSuggestionV1,
    WaitingForDTOv1,
)
from contracts.mocks import (
    create_mock_email_thread,
    create_mock_thread_intel,
    create_mock_task,
    create_mock_draft,
    create_mock_calendar_suggestion,
    create_mock_waiting_for,
)


# ============================================================================
# Ingestion Contract Tests
# ============================================================================

class TestEmailThreadV1:
    """Tests for EmailThreadV1 contract."""
    
    def test_valid_thread_creation(self):
        """Should create a valid thread from mock data."""
        thread = create_mock_email_thread()
        assert thread.thread_id is not None
        assert len(thread.messages) > 0
        assert thread.provider in ["gmail", "outlook"]
    
    def test_serialization_roundtrip(self):
        """Should serialize and deserialize without data loss."""
        original = create_mock_email_thread()
        json_data = original.model_dump_json()
        restored = EmailThreadV1.model_validate_json(json_data)
        
        assert restored.thread_id == original.thread_id
        assert len(restored.messages) == len(original.messages)
        assert len(restored.attachments) == len(original.attachments)
    
    def test_empty_messages_allowed(self):
        """Should allow empty messages list."""
        thread = EmailThreadV1(
            thread_id="test",
            external_id="ext-123",
            subject="Test",
            participants=[],
            messages=[],
            attachments=[],
            last_updated=datetime.now(timezone.utc),
            provider="gmail",
        )
        assert len(thread.messages) == 0


# ============================================================================
# Intelligence Contract Tests
# ============================================================================

class TestThreadIntelV1:
    """Tests for ThreadIntelV1 contract."""
    
    def test_valid_intel_creation(self):
        """Should create valid intelligence from mock data."""
        intel = create_mock_thread_intel()
        assert intel.thread_id is not None
        assert intel.summary != ""
        assert intel.urgency_score >= 0 and intel.urgency_score <= 100
    
    def test_all_intent_types_valid(self):
        """All intent types should be creatable."""
        for intent in IntentType:
            intel = ThreadIntelV1(
                thread_id="test",
                summary="Test summary",
                intent=intent,
                urgency_score=50,
                extracted_deadlines=[],
                entities=[],
                attachment_summaries=[],
                suggested_reply_points=[],
                model_version="test",
                processed_at=datetime.now(timezone.utc),
                schema_version="1.0",
            )
            assert intel.intent == intent
    
    def test_backward_compatibility_optional_fields(self):
        """Should work without optional fields (backward compat)."""
        intel = ThreadIntelV1(
            thread_id="test",
            summary="Test",
            intent=IntentType.FYI,
            urgency_score=0,
            # All optional fields omitted
            extracted_deadlines=[],
            entities=[],
            attachment_summaries=[],
            suggested_reply_points=[],
            model_version="test",
            schema_version="1.0",
        )
        assert intel.main_ask is None
        assert intel.decision_needed is None


# ============================================================================
# Workflow Contract Tests
# ============================================================================

class TestTaskDTOv1:
    """Tests for TaskDTOv1 contract."""
    
    def test_valid_task_creation(self):
        """Should create a valid task from mock data."""
        task = create_mock_task()
        assert task.task_id is not None
        assert task.priority_explanation != ""
    
    def test_priority_score_bounds(self):
        """Priority score should be bounded 0-100."""
        with pytest.raises(ValueError):
            TaskDTOv1(
                task_id="test",
                thread_id="test",
                user_id="test",
                title="Test",
                task_type=TaskType.OTHER,
                priority=PriorityLevel.CAN_WAIT,
                priority_score=150,  # Invalid
                priority_explanation="Test",
                effort=EffortLevel.QUICK,
                status=TaskStatus.PENDING,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )


class TestDraftDTOv1:
    """Tests for DraftDTOv1 contract."""
    
    def test_valid_draft_creation(self):
        """Should create a valid draft from mock data."""
        draft = create_mock_draft()
        assert draft.content != ""
        assert draft.tone in ToneType
    
    def test_placeholder_detection(self):
        """Should track unresolved placeholders."""
        draft = create_mock_draft()
        assert draft.has_unresolved_placeholders == True
        assert len(draft.placeholders) > 0


class TestCalendarSuggestionV1:
    """Tests for CalendarSuggestionV1 contract."""
    
    def test_never_auto_accepted(self):
        """New suggestions should never be pre-accepted."""
        suggestion = create_mock_calendar_suggestion()
        assert suggestion.is_accepted == False


class TestWaitingForDTOv1:
    """Tests for WaitingForDTOv1 contract."""
    
    def test_days_waiting_calculation(self):
        """Days waiting should be non-negative."""
        waiting = create_mock_waiting_for()
        assert waiting.days_waiting >= 0


# ============================================================================
# Cross-Contract Integration Tests
# ============================================================================

class TestContractFlow:
    """Tests the full contract flow from ingestion to workflow."""
    
    def test_ingestion_to_intelligence_flow(self):
        """EmailThreadV1 should provide all data needed for ThreadIntelV1."""
        thread = create_mock_email_thread()
        
        # Intelligence should be creatable from thread data
        intel = ThreadIntelV1(
            thread_id=thread.thread_id,  # Uses same ID
            summary=f"Summary of: {thread.subject}",
            intent=IntentType.ACTION_REQUIRED,
            urgency_score=75,
            extracted_deadlines=[],
            entities=[],
            attachment_summaries=[],
            suggested_reply_points=[],
            model_version="test",
            schema_version="1.0",
        )
        
        assert intel.thread_id == thread.thread_id
    
    def test_intelligence_to_workflow_flow(self):
        """ThreadIntelV1 should provide all data needed for TaskDTOv1."""
        intel = create_mock_thread_intel()
        
        # Task should be creatable from intel data
        task = TaskDTOv1(
            task_id="generated-task",
            thread_id=intel.thread_id,  # Uses same ID
            user_id="user-001",
            title=f"Action: {intel.main_ask or 'Review'}",
            task_type=TaskType.REPLY,
            priority=PriorityLevel.DO_NOW if intel.urgency_score > 70 else PriorityLevel.DO_TODAY,
            priority_score=intel.urgency_score,
            priority_explanation=f"Score {intel.urgency_score}: {intel.intent.value}",
            effort=EffortLevel.QUICK,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        
        assert task.thread_id == intel.thread_id
        assert task.priority_score == intel.urgency_score
