
import asyncio
import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Get Database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ DATABASE_URL env var not found.")
    sys.exit(1)

# Fix for asyncpg
if "postgresql://" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

async def add_superuser_column():
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        print("🔧 Checking for 'is_superuser' column in 'users' table...")
        
        # Check if column exists
        result = await conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name='is_superuser';"
        ))
        exists = result.scalar()
        
        if exists:
            print("✅ Column 'is_superuser' already exists.")
        else:
            print("⚠️ Column 'is_superuser' missing. Adding it now...")
            await conn.execute(text("ALTER TABLE users ADD COLUMN is_superuser BOOLEAN DEFAULT FALSE;"))
            print("✅ Column 'is_superuser' added successfully.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_superuser_column())
