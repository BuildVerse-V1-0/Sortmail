"""
API Routes - Drafts
-------------------
Draft generation endpoints.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from contracts import DraftDTOv1, ToneType
from contracts.mocks import create_mock_draft

router = APIRouter()


class DraftRequest(BaseModel):
    """Request to generate a draft reply."""
    thread_id: str
    tone: ToneType = ToneType.NORMAL
    additional_context: Optional[str] = None


@router.post("/", response_model=DraftDTOv1)
async def generate_draft(request: DraftRequest):
    """
    Generate a draft reply for a thread.
    
    Uses thread context and attachments to create a contextual reply.
    Never auto-sends - user must review and send manually.
    """
    # TODO: Implement real draft generation with LLM
    draft = create_mock_draft()
    draft.thread_id = request.thread_id
    draft.tone = request.tone
    return draft


@router.get("/{draft_id}", response_model=DraftDTOv1)
async def get_draft(draft_id: str):
    """Get an existing draft."""
    # TODO: Replace with real DB query
    draft = create_mock_draft()
    draft.draft_id = draft_id
    return draft


@router.post("/{draft_id}/regenerate", response_model=DraftDTOv1)
async def regenerate_draft(
    draft_id: str,
    tone: Optional[ToneType] = None,
):
    """Regenerate a draft with optional new tone."""
    # TODO: Implement regeneration
    draft = create_mock_draft()
    draft.draft_id = draft_id
    if tone:
        draft.tone = tone
    return draft


@router.delete("/{draft_id}")
async def delete_draft(draft_id: str):
    """Delete a draft."""
    return {"draft_id": draft_id, "deleted": True}
