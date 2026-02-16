"""
Priority Engine
---------------
Calculates task priority with explainability.
"""

from typing import Tuple, List

from contracts import ThreadIntelV1, PriorityLevel, IntentType


# VIP domains get automatic priority boost
DEFAULT_VIP_DOMAINS = [
    "ceo", "founder", "investor", "board",
]


def calculate_priority(
    intel: ThreadIntelV1,
    vip_domains: List[str] = None,
) -> Tuple[PriorityLevel, int, str]:
    """
    Calculate priority with explainable reasoning.
    
    Args:
        intel: ThreadIntelV1 from Intelligence layer
        vip_domains: List of VIP domain strings
        
    Returns:
        Tuple of (PriorityLevel, score 0-100, explanation string)
    """
    vip_domains = vip_domains or DEFAULT_VIP_DOMAINS
    
    score = 0
    reasons = []
    
    # Base score from urgency
    score += intel.urgency_score
    if intel.urgency_score > 70:
        reasons.append(f"High urgency ({intel.urgency_score})")
    
    # Intent modifier
    intent_scores = {
        IntentType.URGENT: 30,
        IntentType.ACTION_REQUIRED: 20,
        IntentType.SCHEDULING: 10,
        IntentType.FYI: -20,
        IntentType.UNKNOWN: 0,
    }
    intent_boost = intent_scores.get(intel.intent, 0)
    score += intent_boost
    if intent_boost > 0:
        reasons.append(f"{intel.intent.value.replace('_', ' ').title()}")
    
    # Deadline modifier
    if intel.extracted_deadlines:
        score += 15
        reasons.append(f"Deadline: {intel.extracted_deadlines[0].raw_text}")
    
    # Attachment modifier
    high_importance_attachments = [
        a for a in intel.attachment_summaries 
        if a.importance == "high"
    ]
    if high_importance_attachments:
        score += 10
        reasons.append(f"{len(high_importance_attachments)} important attachment(s)")
    
    # TODO: VIP sender check (requires participant info)
    
    # Cap score
    score = max(0, min(100, score))
    
    # Convert to level
    level = _score_to_level(score)
    
    # Build explanation
    explanation = f"{level.value.replace('_', ' ').title()}: " + " + ".join(reasons) if reasons else "Normal priority"
    
    return level, score, explanation


def _score_to_level(score: int) -> PriorityLevel:
    """Convert numeric score to priority level."""
    if score >= 70:
        return PriorityLevel.DO_NOW
    elif score >= 40:
        return PriorityLevel.DO_TODAY
    else:
        return PriorityLevel.CAN_WAIT
