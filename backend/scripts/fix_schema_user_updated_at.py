
import asyncio
import os
import asyncpg
from urllib.parse import urlparse

# Get DATABASE_URL from env or user input
DATABASE_URL = os.getenv("DATABASE_URL")

async def fix_schema():
    print("🚀 Starting Schema Fix: Adding 'updated_at' to 'users' table")
    
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL environment variable not found.")
        return

    # Parse URL for asyncpg (handling postgres:// vs postgresql://)
    db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    print(f"🔌 Connecting to DB: {db_url.split('@')[-1]}") # Mask password

    try:
        conn = await asyncpg.connect(db_url)
        print("✅ Connected to Database")

        # 1. Check if column exists
        check_sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users' AND column_name='updated_at';
        """
        row = await conn.fetchrow(check_sql)
        
        if row:
            print("✅ Column 'updated_at' already exists. No action needed.")
        else:
            print("⚠️ Column 'updated_at' is MISSING. Adding it now...")
            alter_sql = """
            ALTER TABLE users 
            ADD COLUMN updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() AT TIME ZONE 'utc');
            """
            await conn.execute(alter_sql)
            print("✅ Successfully added 'updated_at' column to 'users' table.")

        await conn.close()
        print("🎉 Schema Fix Complete!")

    except Exception as e:
        print(f"❌ Error during migration: {e}")

if __name__ == "__main__":
    asyncio.run(fix_schema())
