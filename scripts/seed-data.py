# Seed Data Script
# Run this to populate the database with test data

"""
Seed database with test data for development.
"""

import asyncio
from datetime import datetime, timedelta
import uuid

# from core.storage import async_session, init_db
# from models import User, Thread, Task


async def seed_database():
    """Seed the database with test data."""
    print("🌱 Seeding database...")
    
    # await init_db()
    
    # async with async_session() as session:
    #     # Create test user
    #     user = User(
    #         id=f"user-{uuid.uuid4().hex[:8]}",
    #         email="test@example.com",
    #         name="Test User",
    #         provider="gmail",
    #     )
    #     session.add(user)
    #     
    #     # Create test threads
    #     # ...
    #     
    #     await session.commit()
    
    print("✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
