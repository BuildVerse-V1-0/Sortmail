"""
Email Intelligence Engine
--------------------------
Analyzes email threads and produces ThreadIntelV1 contracts.

Input: EmailThreadV1 (from Ingestion)
Output: ThreadIntelV1 (Boundary Contract to Workflow)
"""

from datetime import datetime
from typing import Optional

from contracts import (
    EmailThreadV1,
    ThreadIntelV1,
    IntentType,
    ExtractedDeadline,
    ExtractedEntity,
    AttachmentIntel,
)
from .summarizer import summarize_thread
from .intent_classifier import classify_intent
from .deadline_extractor import extract_deadlines
from .entity_extractor import extract_entities
from .attachment_intel import analyze_attachments


async def analyze_thread(
    thread: EmailThreadV1,
    model: str = "gemini-1.5-pro",
) -> ThreadIntelV1:
    """
    Analyze an email thread and produce complete intelligence.
    
    This is the MAIN entry point for the Intelligence layer.
    All sub-analyses are combined into a single ThreadIntelV1 output.
    
    Args:
        thread: EmailThreadV1 from Ingestion
        model: LLM model to use
        
    Returns:
        ThreadIntelV1 containing all analysis results
    """
    # Run all analyses (can be parallelized)
    summary = await summarize_thread(thread, model)
    intent, urgency = await classify_intent(thread, model)
    deadlines = await extract_deadlines(thread, model)
    entities = await extract_entities(thread, model)
    attachment_summaries = await analyze_attachments(thread.attachments, model)
    
    # Extract main ask and decision needed from summary
    main_ask = _extract_main_ask(summary)
    decision_needed = _extract_decision(summary, intent)
    
    # Generate suggested action
    suggested_action = _generate_suggested_action(intent, deadlines, main_ask)
    
    # Generate reply points
    reply_points = _generate_reply_points(thread, intent, deadlines)
    
    return ThreadIntelV1(
        thread_id=thread.thread_id,
        summary=summary,
        intent=intent,
        urgency_score=urgency,
        main_ask=main_ask,
        decision_needed=decision_needed,
        extracted_deadlines=deadlines,
        entities=entities,
        attachment_summaries=attachment_summaries,
        suggested_action=suggested_action,
        suggested_reply_points=reply_points,
        model_version=model,
        processed_at=datetime.utcnow(),
    )


def _extract_main_ask(summary: str) -> Optional[str]:
    """Extract the main ask from summary."""
    # TODO: Use LLM to extract main ask
    # For now, return None
    return None


def _extract_decision(summary: str, intent: IntentType) -> Optional[str]:
    """Determine what decision is needed."""
    if intent == IntentType.ACTION_REQUIRED:
        return "Action required - review and respond"
    elif intent == IntentType.SCHEDULING:
        return "Confirm or propose meeting time"
    return None


def _generate_suggested_action(
    intent: IntentType,
    deadlines: list,
    main_ask: Optional[str],
) -> Optional[str]:
    """Generate suggested action based on analysis."""
    if intent == IntentType.URGENT:
        return "Respond immediately"
    elif intent == IntentType.ACTION_REQUIRED:
        if deadlines:
            return f"Respond before {deadlines[0].raw_text}"
        return "Review and respond"
    elif intent == IntentType.SCHEDULING:
        return "Confirm availability or propose alternative"
    return None


def _generate_reply_points(
    thread: EmailThreadV1,
    intent: IntentType,
    deadlines: list,
) -> list:
    """Generate key points to include in reply."""
    points = []
    
    if intent == IntentType.ACTION_REQUIRED:
        points.append("Acknowledge receipt")
        points.append("State your decision or next steps")
    
    if deadlines:
        points.append(f"Reference the deadline: {deadlines[0].raw_text}")
    
    if thread.attachments:
        points.append("Confirm you reviewed the attachments")
    
    return points
