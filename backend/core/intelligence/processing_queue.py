"""
Intelligence Processing Queue
-----------------------------
Asynchronous Redis-backed queue to process incoming email threads through Gemini 
without hitting rate limits or blocking the webhook sync process.
"""

import json
import asyncio
import logging
import redis.asyncio as aioredis
from typing import List

from core.intelligence.pipeline import process_thread_intelligence
from core.intelligence.attachment_intel import analyze_attachment
from core.storage.database import async_session
from sqlalchemy.future import select
from models.thread import Thread
from models.attachment import Attachment

logger = logging.getLogger("ai_worker")

class IntelligenceQueue:
    """Queue threads for AI processing using Redis Sorted Sets."""
    
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.queue_key = "intel:pending"
        
    async def enqueue(self, thread_id: str, priority: int = 50):
        """Add thread to processing queue (higher score = processed sooner)"""
        await self.redis.zadd(
            self.queue_key,
            {thread_id: priority}
        )
        logger.debug(f"[Queue] Enqueued thread {thread_id} with priority {priority}")
    
    async def dequeue_batch(self, batch_size: int = 10) -> List[str]:
        """Pop the highest priority threads from the queue"""
        # Get highest scores first (-inf to +inf, ZREVRANGE)
        thread_ids = await self.redis.zrevrange(
            self.queue_key, 0, batch_size - 1
        )
        if thread_ids:
            # Remove from pending so other workers don't grab them
            await self.redis.zrem(self.queue_key, *thread_ids)
        return thread_ids
    
    async def size(self) -> int:
        """Get pending queue length"""
        return await self.redis.zcard(self.queue_key)


async def generate_intelligence_for_thread(thread_id: str):
    """Run full intelligence pipeline for the thread in the background."""
    async with async_session() as db:
        stmt = select(Thread).where(Thread.id == thread_id)
        result = await db.execute(stmt)
        thread = result.scalars().first()
        
        if not thread:
            logger.warning(f"[Worker] Thread {thread_id} not found in DB.")
            return

        try:
            await process_thread_intelligence(thread.id, thread.user_id, db)
            logger.info(f"✅ [Worker] Successfully processed AI intel for {thread.id}")
            await db.commit()
        except Exception as e:
            logger.error(f"❌ [Worker] Failed to process {thread.id}: {e}")
            await db.rollback()

async def generate_intelligence_for_attachment(attachment_id: str):
    """Run full intelligence pipeline for an attachment in the background."""
    async with async_session() as db:
        try:
            await analyze_attachment(attachment_id, db)
        except Exception as e:
            logger.error(f"❌ [Worker] Failed to process attachment {attachment_id}: {e}")

async def intelligence_worker(redis_url: str):
    """Continuous polling loop to process queued items (threads or attachments)."""
    queue = IntelligenceQueue(redis_url)
    logger.info(f"🚀 Started AI Background Worker connected to {redis_url}")
    
    while True:
        try:
            item_ids = await queue.dequeue_batch(batch_size=5)
            
            if not item_ids:
                await asyncio.sleep(5)  # Wait for work and backoff gracefully
                continue
            
            # Process batch concurrently
            tasks = []
            for item in item_ids:
                if item.startswith("att:"):
                    tasks.append(generate_intelligence_for_attachment(item.replace("att:", "")))
                else:
                    # thread fallback for older queued items
                    thread_id = item.replace("thread:", "") if item.startswith("thread:") else item
                    tasks.append(generate_intelligence_for_thread(thread_id))
                    
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"[Worker] Internal loop error: {e}")
            await asyncio.sleep(5)

# Singleton helper
queue_instance = None
def get_queue(redis_url: str) -> IntelligenceQueue:
    global queue_instance
    if not queue_instance:
         queue_instance = IntelligenceQueue(redis_url)
    return queue_instance
