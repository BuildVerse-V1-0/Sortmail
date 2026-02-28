import asyncio
import os
import sys

# Add parent dir to sys.path so we can import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.storage.database import async_session_factory
from sqlalchemy import text

async def add_columns():
    async with async_session_factory() as db:
        try:
            await db.execute(text("ALTER TABLE attachments ADD COLUMN intel_json JSONB;"))
            await db.commit()
            print("✅ Added intel_json to attachments")
        except Exception as e:
            print(f"⚠️ Could not add intel_json: {e}")
            await db.rollback()
            
        try:
            await db.execute(text("ALTER TABLE threads ADD COLUMN rag_embedded_at TIMESTAMP WITH TIME ZONE;"))
            await db.commit()
            print("✅ Added rag_embedded_at to threads")
        except Exception as e:
            print(f"⚠️ Could not add rag_embedded_at: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(add_columns())
