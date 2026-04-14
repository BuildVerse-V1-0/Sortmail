from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.storage.database import get_db
from models.user import User
from api.dependencies import get_current_user
from models.thread import Thread
from models.attachment import Attachment
from core.credits.credit_service import InsufficientCreditsError
from core.rag.retriever import get_similar_context
from core.intelligence.llama_engine import llama_chat
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


async def _filter_context_items_to_user(
    items: list[dict],
    *,
    user_id: str,
    db: AsyncSession,
) -> list[dict]:
    """Defense-in-depth: only return context items whose source rows belong to user_id."""
    if not items:
        return []

    thread_ids = {
        str(item.get("source_id"))
        for item in items
        if str(item.get("source_type") or "").startswith("thread") and item.get("source_id")
    }
    attachment_ids = {
        str(item.get("source_id"))
        for item in items
        if str(item.get("source_type") or "").startswith("attachment") and item.get("source_id")
    }

    owned_thread_ids: set[str] = set()
    if thread_ids:
        owned_thread_rows = await db.execute(
            select(Thread.id).where(
                Thread.user_id == user_id,
                Thread.id.in_(list(thread_ids)),
            )
        )
        owned_thread_ids = {str(row[0]) for row in owned_thread_rows.all()}

    owned_attachment_ids: set[str] = set()
    if attachment_ids:
        owned_attachment_rows = await db.execute(
            select(Attachment.id).where(
                Attachment.user_id == user_id,
                Attachment.id.in_(list(attachment_ids)),
            )
        )
        owned_attachment_ids = {str(row[0]) for row in owned_attachment_rows.all()}

    filtered: list[dict] = []
    for item in items:
        source_type = str(item.get("source_type") or "")
        source_id = str(item.get("source_id") or "")
        if not source_id:
            continue

        if source_type.startswith("thread") and source_id in owned_thread_ids:
            filtered.append(item)
            continue
        if source_type.startswith("attachment") and source_id in owned_attachment_ids:
            filtered.append(item)

    return filtered


@router.get("/context/{thread_id}")
async def get_thread_context(
    thread_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetches RAG context related to the current thread."""
    stmt = select(Thread).where(Thread.id == thread_id, Thread.user_id == current_user.id)
    thread = (await db.execute(stmt)).scalars().first()

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    if not thread.summary:
        return {"context": []}

    query_text = f"{thread.subject} {thread.intent} {thread.summary}"
    similar_items = await get_similar_context(
        query_text=query_text,
        user_id=current_user.id,
        limit=5,
        exclude_source_id=thread.id
    )
    similar_items = await _filter_context_items_to_user(similar_items, user_id=current_user.id, db=db)
    return {"context": similar_items}


@router.post("/chat")
async def ai_chat(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Universal AI Chatbot using Llama 3.3 70B (HF Inference API).
    Returns SSE stream: 'data: <text>\\n\\n' chunks, ending with 'data: [DONE]\\n\\n'.
    """
    query = payload.get("message")
    if not query:
        raise HTTPException(status_code=400, detail="Missing chat message")

    # 1. Fetch RAG context for this user
    similar_items = await get_similar_context(
        query_text=query,
        user_id=current_user.id,
        limit=6
    )
    similar_items = await _filter_context_items_to_user(similar_items, user_id=current_user.id, db=db)

    context_str = "\n\n".join([
        f"--- {item.get('source_type', 'email')} ---\n{item.get('document', '')[:1000]}"
        for item in similar_items
    ])

    system_prompt = f"""You are the SortMail AI assistant. Help the user manage their email inbox intelligently and professionally.
You have access to the following context from their mailbox:

<context>
{context_str if context_str else "No relevant context found."}
</context>

Be concise, helpful, and professional. If context is provided, reference it specifically."""

    chat_messages = [{"role": "user", "content": query}]

    async def stream():
        try:
            response_text = await llama_chat(
                messages=chat_messages,
                system_prompt=system_prompt,
                max_tokens=1024,
                metadata={
                    "user_id": current_user.id,
                    "related_entity_type": "chat",
                    "related_entity_id": None,
                },
            )
            # Emit in word-sized chunks to simulate streaming UX
            words = response_text.split(" ")
            chunk_size = 5
            for i in range(0, len(words), chunk_size):
                chunk = " ".join(words[i:i+chunk_size])
                if i + chunk_size < len(words):
                    chunk += " "
                safe = chunk.replace("\n", "\\n")
                yield f"data: {safe}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            if isinstance(e, InsufficientCreditsError):
                yield "data: Error: Insufficient credits.\n\n"
                return
            logger.error(f"Chat stream failed: {e}")
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
