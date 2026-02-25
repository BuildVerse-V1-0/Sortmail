"""
Task Generator
--------------
Generates tasks from ThreadIntelV1.

Input: ThreadIntelV1 (from Intelligence)
Output: TaskDTOv1 (Boundary Contract)
"""

from datetime import datetime, timezone
from typing import List
import uuid

from contracts import (
    ThreadIntelV1,
    TaskDTOv1,
    TaskType,
    TaskStatus,
    PriorityLevel,
    EffortLevel,
    IntentType,
)
from .priority_engine import calculate_priority


async def generate_tasks(
    intel: ThreadIntelV1,
    user_id: str,
) -> List[TaskDTOv1]:
    """
    Generate tasks from thread intelligence.
    
    Args:
        intel: ThreadIntelV1 from Intelligence layer
        user_id: User who owns these tasks
        
    Returns:
        List of TaskDTOv1 contracts
    """
    tasks = []
    
    # Generate task based on intent
    task_type = _intent_to_task_type(intel.intent)
    
    if task_type:
        priority, priority_score, explanation = calculate_priority(intel)
        effort = _estimate_effort(intel)
        deadline = _get_deadline(intel)
        
        task = TaskDTOv1(
            task_id=f"task-{uuid.uuid4().hex[:8]}",
            thread_id=intel.thread_id,
            user_id=user_id,
            title=_generate_title(intel),
            description=intel.suggested_action,
            task_type=task_type,
            priority=priority,
            priority_score=priority_score,
            priority_explanation=explanation,
            effort=effort,
            deadline=deadline,
            deadline_source=intel.extracted_deadlines[0].raw_text if intel.extracted_deadlines else None,
            status=TaskStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        tasks.append(task)
    
    # Generate additional tasks for attachments that need review
    for att in intel.attachment_summaries:
        if att.importance == "high":
            tasks.append(_create_review_task(intel, user_id, att))
    
    return tasks


def _intent_to_task_type(intent: IntentType) -> TaskType:
    """Map intent to task type."""
    mapping = {
        IntentType.ACTION_REQUIRED: TaskType.REPLY,
        IntentType.SCHEDULING: TaskType.SCHEDULE,
        IntentType.URGENT: TaskType.REPLY,
        IntentType.FYI: None,  # No task for FYI
        IntentType.UNKNOWN: None,
    }
    return mapping.get(intent)


def _generate_title(intel: ThreadIntelV1) -> str:
    """Generate task title from intelligence."""
    if intel.main_ask:
        return f"Respond: {intel.main_ask[:50]}"
    
    intent_titles = {
        IntentType.ACTION_REQUIRED: "Action required",
        IntentType.SCHEDULING: "Schedule meeting",
        IntentType.URGENT: "URGENT: Respond",
    }
    
    prefix = intent_titles.get(intel.intent, "Review")
    return f"{prefix} - Thread"


def _estimate_effort(intel: ThreadIntelV1) -> EffortLevel:
    """Estimate effort required for task."""
    # Deep work if attachments need review
    if any(a.importance == "high" for a in intel.attachment_summaries):
        return EffortLevel.DEEP_WORK
    
    # Quick task for simple responses
    if intel.intent == IntentType.SCHEDULING:
        return EffortLevel.QUICK
    
    # Default based on urgency
    if intel.urgency_score > 70:
        return EffortLevel.QUICK  # Urgent = do it quickly
    
    return EffortLevel.QUICK


def _get_deadline(intel: ThreadIntelV1) -> datetime:
    """Get deadline from intelligence."""
    if intel.extracted_deadlines:
        return intel.extracted_deadlines[0].normalized
    return None


def _create_review_task(intel: ThreadIntelV1, user_id: str, attachment) -> TaskDTOv1:
    """Create a task to review an important attachment."""
    return TaskDTOv1(
        task_id=f"task-{uuid.uuid4().hex[:8]}",
        thread_id=intel.thread_id,
        user_id=user_id,
        title=f"Review: {attachment.document_type.title()}",
        description=attachment.summary,
        task_type=TaskType.REVIEW,
        priority=PriorityLevel.DO_TODAY,
        priority_score=60,
        priority_explanation="High-importance document attached",
        effort=EffortLevel.DEEP_WORK,
        deadline=None,
        deadline_source=None,
        status=TaskStatus.PENDING,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
