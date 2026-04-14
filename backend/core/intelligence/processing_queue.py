"""
Intelligence Processing Queue
-----------------------------
Asynchronous Redis-backed queue to process incoming email threads through Gemini 
without hitting rate limits or blocking the webhook sync process.
"""

import asyncio
import logging
from typing import List
from core.redis import get_redis

from core.intelligence.pipeline import process_thread_intelligence
from core.intelligence.attachment_intel import analyze_attachment
from core.storage.database import async_session
from core.app_metrics import record_metric
from sqlalchemy.future import select
from models.thread import Thread

logger = logging.getLogger("ai_worker")

class IntelligenceQueue:
    """Queue threads for AI processing using Redis Sorted Sets."""
    
    def __init__(self, redis_url: str):
        self.redis = None
        self.queue_key = "intel:pending"

    async def _get_redis(self):
        if self.redis is None:
            self.redis = await get_redis()
        return self.redis
        
    async def enqueue(self, thread_id: str, priority: int = 50):
        """Add thread to processing queue (higher score = processed sooner)"""
        redis = await self._get_redis()
        await redis.zadd(
            self.queue_key,
            {thread_id: priority}
        )
        record_metric("queue_enqueue")
        logger.debug(f"[Queue] Enqueued thread {thread_id} with priority {priority}")
    
    async def dequeue_batch(self, batch_size: int = 10) -> List[str]:
        """Atomically pop the highest priority items from the queue."""
        redis = await self._get_redis()
        items = await redis.zpopmax(self.queue_key, batch_size)
        if not items:
            return []

        thread_ids = [item[0] for item in items]
        record_metric("queue_dequeue_items", len(thread_ids))
        return thread_ids
    
    async def size(self) -> int:
        """Get pending queue length"""
        redis = await self._get_redis()
        return await redis.zcard(self.queue_key)
    
    async def remove(self, thread_id: str) -> bool:
        """Remove a thread from the processing queue after completion."""
        redis = await self._get_redis()
        removed = await redis.zrem(self.queue_key, thread_id)
        if removed > 0:
            record_metric("queue_item_removed")
            logger.debug(f"[Queue] Removed thread {thread_id} from queue")
            return True
        return False


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
            record_metric("queue_thread_processed")
            logger.info(f"✅ [Worker] Successfully processed AI intel for {thread.id}")
            await db.commit()
        except Exception as e:
            record_metric("queue_thread_failed")
            logger.error(f"❌ [Worker] Failed to process {thread.id}: {e}")
            await db.rollback()

async def generate_intelligence_for_attachment(attachment_id: str):
    """Run full intelligence pipeline for an attachment in the background."""
    async with async_session() as db:
        try:
            await analyze_attachment(attachment_id, db)
            record_metric("queue_attachment_processed")
        except Exception as e:
            record_metric("queue_attachment_failed")
            logger.error(f"❌ [Worker] Failed to process attachment {attachment_id}: {e}")

async def intelligence_worker(redis_url: str):
    """Continuous polling loop to process queued items (threads or attachments)."""
    queue = IntelligenceQueue(redis_url)
    logger.info(f"🚀 Started AI Background Worker connected to {redis_url}")
    idle_sleep_seconds = 5
    max_idle_sleep_seconds = 30
    
    while True:
        try:
            item_ids = await queue.dequeue_batch(batch_size=5)
            
            if not item_ids:
                await asyncio.sleep(idle_sleep_seconds)
                idle_sleep_seconds = min(idle_sleep_seconds * 2, max_idle_sleep_seconds)
                continue
            idle_sleep_seconds = 1
            
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
            record_metric("queue_worker_loop_error")
            logger.error(f"[Worker] Internal loop error: {e}")
            await asyncio.sleep(idle_sleep_seconds)
            idle_sleep_seconds = min(idle_sleep_seconds * 2, max_idle_sleep_seconds)

# Singleton helper
queue_instance = None
def get_queue(redis_url: str) -> IntelligenceQueue:
    global queue_instance
    if not queue_instance:
         queue_instance = IntelligenceQueue(redis_url)
    return queue_instance
