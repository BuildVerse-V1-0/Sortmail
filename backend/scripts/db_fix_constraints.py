import asyncio
from sqlalchemy import text
from app.config import settings
from core.storage.database import engine

async def check_schema():
    print("Executing SQLAlchemy direct ALTERS on Supabase...")
    async with engine.begin() as conn:
        try:
            await conn.execute(text('ALTER TABLE emails ALTER COLUMN from_address DROP NOT NULL;'))
            print("Successfully dropped NOT NULL constraint on emails.from_address")
        except Exception as e:
            print(f"Error modifying emails.from_address: {e}")
            
        try:
            await conn.execute(text('ALTER TABLE emails ALTER COLUMN to_addresses DROP NOT NULL;'))
            print("Successfully dropped NOT NULL constraint on emails.to_addresses")
        except Exception as e:
            print(f"Error modifying emails.to_addresses: {e}")

asyncio.run(check_schema())
