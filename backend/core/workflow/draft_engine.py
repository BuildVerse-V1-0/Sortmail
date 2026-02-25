"""
Draft Engine
------------
Generates draft replies from ThreadIntelV1.

Input: ThreadIntelV1 (from Intelligence)
Output: DraftDTOv1 (Boundary Contract)
"""

from datetime import datetime, timezone
from typing import Optional
import uuid

from contracts import (
    ThreadIntelV1,
    DraftDTOv1,
    ToneType,
    Placeholder,
)
from app.config import settings


async def generate_draft(
    intel: ThreadIntelV1,
    user_id: str,
    tone: ToneType = ToneType.NORMAL,
) -> DraftDTOv1:
    """
    Generate a draft reply for an email thread.
    
    Args:
        intel: ThreadIntelV1 from Intelligence layer
        user_id: User who owns this draft
        tone: Desired tone (brief/normal/formal)
        
    Returns:
        DraftDTOv1 contract (never auto-sent!)
    """
    # Build prompt with context
    prompt = _build_prompt(intel, tone)
    
    # Generate draft with LLM
    content = await _generate_with_llm(prompt, tone)
    
    # Extract placeholders
    placeholders = _extract_placeholders(content)
    
    return DraftDTOv1(
        draft_id=f"draft-{uuid.uuid4().hex[:8]}",
        thread_id=intel.thread_id,
        user_id=user_id,
        content=content,
        tone=tone,
        placeholders=placeholders,
        has_unresolved_placeholders=len(placeholders) > 0,
        references_attachments=len(intel.attachment_summaries) > 0,
        references_deadlines=len(intel.extracted_deadlines) > 0,
        created_at=datetime.now(timezone.utc),
        model_version=settings.LLM_PROVIDER,
    )


def _build_prompt(intel: ThreadIntelV1, tone: ToneType) -> str:
    """Build LLM prompt for draft generation."""
    tone_instructions = {
        ToneType.BRIEF: "Keep the response very short and direct. Maximum 2-3 sentences.",
        ToneType.NORMAL: "Write a professional but friendly response.",
        ToneType.FORMAL: "Use formal business language and proper salutations.",
    }
    
    prompt = f"""Write a reply email based on this context:

Thread Summary: {intel.summary}

Main Ask: {intel.main_ask or 'Not specified'}

Key Points to Address:
{chr(10).join(f'- {p}' for p in intel.suggested_reply_points)}

Attachments:
{chr(10).join(f'- {a.document_type}: {a.summary[:50]}...' for a in intel.attachment_summaries) or 'None'}

Deadlines:
{chr(10).join(f'- {d.raw_text}' for d in intel.extracted_deadlines) or 'None'}

Tone: {tone_instructions.get(tone, tone_instructions[ToneType.NORMAL])}

If any information is missing that the user needs to fill in, use placeholders like [Confirm time] or [Add decision].

Draft:"""
    
    return prompt


async def _generate_with_llm(prompt: str, tone: ToneType) -> str:
    """Generate draft content with LLM."""
    # TODO: Implement actual LLM call
    # For now, return a template
    
    template = """Hi,

Thank you for your email.

[Confirm your response or decision here]

Best regards"""
    
    if tone == ToneType.BRIEF:
        template = """Thanks for this.

[Your response]

Best"""
    elif tone == ToneType.FORMAL:
        template = """Dear [Recipient],

Thank you for your correspondence regarding this matter.

[State your response or decision]

We look forward to your response at your earliest convenience.

Kind regards"""
    
    return template


def _extract_placeholders(content: str) -> list:
    """Extract placeholders from draft content."""
    import re
    
    pattern = r'\[([^\]]+)\]'
    matches = re.findall(pattern, content)
    
    return [
        Placeholder(
            key=f"[{m}]",
            description=f"Please specify: {m}",
            suggested_value=None,
        )
        for m in matches
    ]
