import asyncio
import sys
import os
from datetime import datetime, timezone

# Set strict env vars for connection AND mock vars for Settings validation
# MUST BE DONE BEFORE IMPORTS from app or models
os.environ.setdefault("DATABASE_URL", "postgresql://postgres.lsqeeoysmyonkiaphvhz:SortmailRounak%406789@aws-1-ap-south-1.pooler.supabase.com:5432/postgres")
os.environ.setdefault("FRONTEND_URL", "http://localhost:3000")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
os.environ.setdefault("MICROSOFT_REDIRECT_URI", "http://localhost:8000/auth/microsoft/callback")
os.environ.setdefault("JWT_SECRET", "mock_secret_for_testing_only")

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from models.user import User, UserStatus, AccountType
from models.thread import Thread
from models.email import Email

database_url = os.environ.get("DATABASE_URL").replace("postgresql://", "postgresql+asyncpg://") if "postgresql://" in os.environ.get("DATABASE_URL") else os.environ.get("DATABASE_URL")
engine = create_async_engine(
    database_url,
    echo=False,
    connect_args={"prepared_statement_cache_size": 0, "statement_cache_size": 0}
)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def verify_core_access():
    print("🧪 Verifying Core Email Access (Before AI)...")
    async with AsyncSessionLocal() as db:
        try:
            # 1. Get or Create Test User
            result = await db.execute(select(User).where(User.email == "test_core@example.com"))
            user = result.scalars().first()
            if not user:
                print("Creating test user...")
                user = User(
                    id="test_user_core_v1",
                    email="test_core@example.com",
                    full_name="Core Tester",
                    status=UserStatus.ACTIVE,
                    account_type=AccountType.FREE
                )
                db.add(user)
                await db.commit()
                # Re-fetch
                result = await db.execute(select(User).where(User.email == "test_core@example.com"))
                user = result.scalars().first()

            print(f"User: {user.email} ({user.id})")

            # 2. Create Raw Thread (No AI Data)
            thread_id = f"thread_core_{int(datetime.now(timezone.utc).timestamp())}"
            print(f"Creating raw thread: {thread_id}")
            thread = Thread(
                id=thread_id,
                user_id=user.id,
                external_id="ext_123",
                subject="Hello World - No AI",
                participants=["sender@example.com", "me@example.com"],
                provider="gmail",
                last_email_at=datetime.now(timezone.utc),
                is_unread=1,
                # AI Fields explicitly None
                summary=None,
                intent=None,
                urgency_score=None
            )
            db.add(thread)
            
            # 3. Create Raw Email
            email = Email(
                id=f"email_core_{int(datetime.now(timezone.utc).timestamp())}",
                user_id=user.id,
                thread_id=thread_id,
                external_id="msg_123",
                sender="sender@example.com",
                recipients=[{"email": "me@example.com", "name": "Me"}],
                subject="Hello World - No AI",
                body_plain="This is a raw email body.",
                received_at=datetime.now(timezone.utc)
            )
            db.add(email)
            await db.commit()
            
            # 4. Simulate Dashboard Fetch
            print("Fetching threads for dashboard...")
            stmt = (
                select(Thread)
                .where(Thread.user_id == user.id)
                .order_by(desc(Thread.last_email_at))
                .limit(5)
            )
            result = await db.execute(stmt)
            recent_threads = result.scalars().all()
            
            print(f"Found {len(recent_threads)} threads.")
            for t in recent_threads:
                print(f"--- Thread: {t.id} ---")
                print(f"Subject: {t.subject}")
                print(f"Participants: {t.participants}")
                print(f"Summary (Safe Access): {t.summary or 'Pending analysis...'}")
                print(f"Intent (Safe Access): {t.intent or 'processing'}")
                print(f"Urgency (Safe Access): {t.urgency_score or 0}")
                
                if t.id == thread_id:
                    print("✅ VERIFIED: Newly created raw thread is visible and accessible without AI data.")
            
        except Exception as e:
            print(f"❌ Verification Failed: {e}")
            raise
        finally:
            # Cleanup (Optional, keeping for inspection)
            pass

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_core_access())
