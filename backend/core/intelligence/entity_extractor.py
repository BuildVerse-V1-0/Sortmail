"""
Entity Extractor
----------------
Extracts named entities from email content.
"""

import re
from typing import List

from contracts import EmailThreadV1, ExtractedEntity


# Email pattern
EMAIL_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Money pattern
MONEY_PATTERN = r"\$[\d,]+(?:\.\d{2})?[KMB]?|\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|EUR|dollars)"

# Phone pattern
PHONE_PATTERN = r"\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"


async def extract_entities(
    thread: EmailThreadV1,
    model: str = "gemini-1.5-pro",
) -> List[ExtractedEntity]:
    """
    Extract named entities from email thread.
    
    Args:
        thread: EmailThreadV1 to analyze
        model: LLM model (for future use)
        
    Returns:
        List of ExtractedEntity objects
    """
    entities = []
    
    # Combine all message content
    all_text = " ".join(msg.body_text for msg in thread.messages)
    all_text += f" {thread.subject}"
    
    # Extract different entity types
    entities.extend(_extract_emails(all_text))
    entities.extend(_extract_money(all_text))
    entities.extend(_extract_phones(all_text))
    
    # TODO: Use LLM for more sophisticated entity extraction
    # - People names
    # - Company names
    # - Dates
    # - Project names
    
    return entities


def _extract_emails(text: str) -> List[ExtractedEntity]:
    """Extract email addresses."""
    matches = re.findall(EMAIL_PATTERN, text)
    return [
        ExtractedEntity(
            entity_type="email",
            value=email,
            confidence=0.95,
        )
        for email in set(matches)
    ]


def _extract_money(text: str) -> List[ExtractedEntity]:
    """Extract monetary amounts."""
    matches = re.findall(MONEY_PATTERN, text, re.IGNORECASE)
    return [
        ExtractedEntity(
            entity_type="amount",
            value=amount.strip(),
            confidence=0.90,
        )
        for amount in set(matches)
    ]


def _extract_phones(text: str) -> List[ExtractedEntity]:
    """Extract phone numbers."""
    matches = re.findall(PHONE_PATTERN, text)
    return [
        ExtractedEntity(
            entity_type="phone",
            value=phone,
            confidence=0.85,
        )
        for phone in set(matches)
    ]
