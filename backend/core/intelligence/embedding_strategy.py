"""
Thread Embedding Strategy
-------------------------
Filters threads to determine if they are worth vectorizing into ChromaDB.
Prevents automated newsletters, generic alerts, and short "ok thanks" emails from 
polluting the semantic vector space.
"""

import logging
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from core.storage.vector_store import vector_store
from core.rag.embeddings import generate_embedding
from models.thread import Thread

logger = logging.getLogger(__name__)

async def embed_thread_if_valuable(thread: Thread, user_id: str, messages_text: str, db: AsyncSession) -> bool:
    """
    Evaluates a thread's intelligence metadata and vectors it into ChromaDB if it passes heuristics.
    Returns True if embedded, False if skipped.
    """
    
    # 1. Junk Filter Heuristics
    if not _is_valuable_for_rag(thread, messages_text):
        logger.debug(f"Thread {thread.id} deemed low-value for RAG. Skipping vectorization.")
        return False
        
    try:
        # 2. Build the semantic document
        # We embed the AI summary and key metadata rather than raw email chains 
        # to maximize search precision.
        document = f"""Subject: {thread.subject}
Intent: {thread.intent}

Summary:
{thread.summary}

Participants: {', '.join(thread.participants or [])}
"""

        # 3. Generate Embedding
        embedding = await generate_embedding(document)
        
        # 4. Insert into Vector DB
        await vector_store.add(
            id=f"thread_{thread.id}",
            document=document,
            embedding=embedding,
            metadata={
                "user_id": user_id,
                "source_type": "thread",
                "source_id": thread.id,
                "subject": thread.subject or "",
                "intent": thread.intent or "unknown",
                "urgency_score": thread.urgency_score or 0
            }
        )
        
        # 5. Mark thread as embedded in Postgres Tracker
        thread.rag_embedded_at = datetime.now(timezone.utc)
        await db.commit()
        
        logger.info(f"✅ Embedded thread {thread.id} into ChromaDB")
        return True
        
    except Exception as e:
        logger.error(f"Failed to embed thread {thread.id}: {e}")
        return False


def _is_valuable_for_rag(thread: Thread, text: str) -> bool:
    """
    Determines if a thread should be stored in long-term vector memory.
    """
    # 1. Reject if no intelligence was generated
    if not thread.summary:
        return False
        
    # 2. Reject automated newsletters/alerts explicitly classified by Gemini
    ignorable_intents = ["newsletter", "automated_alert", "spam", "promotional", "system_notification"]
    if thread.intent and thread.intent.lower() in ignorable_intents:
        return False
        
    # 3. Reject extreme low urgency unless it has heavy text volume
    urgency = thread.urgency_score or 0
    text_length = len(text.strip())
    
    if urgency < 20 and text_length < 500:
        return False
        
    # 4. Reject pure "ok thanks" short threads
    if text_length < 50:
        return False
        
    # By default, keep it in memory
    return True
