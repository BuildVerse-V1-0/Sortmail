"""
Draft Schemas
-------------
Request/response models for draft endpoints.
"""

from pydantic import BaseModel
from typing import Optional


class DraftGenerateRequest(BaseModel):
    """Request to generate a draft."""
    thread_id: str
    tone: str = "normal"  # brief, normal, formal
    additional_context: Optional[str] = None


class DraftRegenerateRequest(BaseModel):
    """Request to regenerate a draft."""
    tone: Optional[str] = None
    additional_context: Optional[str] = None
