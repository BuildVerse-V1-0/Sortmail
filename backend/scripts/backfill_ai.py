import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.storage.database import async_session as AsyncSessionLocal
from models.thread import Thread
from models.email import Email
from core.intelligence.gemini_engine import run_intelligence

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def backfill_threads():
    async with AsyncSessionLocal() as db:
        stmt = select(Thread).where(Thread.summary == None)
        result = await db.execute(stmt)
        threads = result.scalars().all()

        if not threads:
            logger.info("No threads need AI backfill.")
            return

        for thread in threads:
            logger.info(f"Backfilling intelligence for thread: {thread.id}")
            # Fetch emails for this thread
            msg_stmt = select(Email).where(Email.thread_id == thread.id).order_by(Email.received_at)
            msg_result = await db.execute(msg_stmt)
            emails = msg_result.scalars().all()

            messages = []
            for m in emails:
                messages.append({
                    "from": m.sender or "",
                    "date": str(m.received_at),
                    "body": m.body_plain or ""
                })

            participants = [p if isinstance(p, str) else p.get("email", "") for p in thread.participants] if thread.participants else []
            
            try:
                intel = await run_intelligence(
                    thread_id=thread.id,
                    subject=thread.subject or "",
                    participants=participants,
                    messages=messages
                )

                if intel:
                    thread.summary = intel.get("summary")
                    thread.intent = intel.get("intent")
                    thread.urgency_score = intel.get("urgency_score")
                    thread.main_ask = intel.get("main_ask")
                    # Store raw JSON in intel_json mapped column if it exists, or just attributes
                    # For sortmail, we just commit the attributes as modeled
                    # ensure we mark it as processed
                    await db.commit()
                    logger.info(f"Successfully processed AI intel for {thread.id}")
            except Exception as e:
                logger.error(f"Failed to process {thread.id}: {e}")

if __name__ == "__main__":
    asyncio.run(backfill_threads())
