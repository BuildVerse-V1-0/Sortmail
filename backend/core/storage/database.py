"""
Database Connection
-------------------
SQLAlchemy async database setup.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings


from sqlalchemy.engine.url import make_url

import ssl

# Database Setup
original_url = settings.DATABASE_URL
if original_url and original_url.startswith("postgres://"):
    original_url = original_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif original_url and original_url.startswith("postgresql://"):
    original_url = original_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Debug Logging (Mask password)
try:
    u = make_url(original_url)
    print(f"🔌 Connecting to DB Host: {u.host}:{u.port} | DB: {u.database}")
except Exception as e:
    print(f"⚠️ Could not parse DB URL for logging: {e}")

# Use make_url to safely manipulate the URL
db_url_obj = make_url(original_url)

# SSL Context for Production (Railway/Supabase usually need this)
# SSL and Connection Arguments
connect_args = {}

# Check for Production / Railway / Supabase
is_production = (
    settings.ENVIRONMENT == "production" 
    or "railway" in settings.DATABASE_URL 
    or "railway" in (db_url_obj.host or "") 
    or "supabase" in (db_url_obj.host or "")
)

if is_production:
    print("🚀 Configuring database for PRODUCTION/CLOUD environment")
    
    # 1. SSL Context (Necessary for Supabase/Railway)
    # We use a custom context to avoid "certificate verify failed" or hostname mismatches
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx
    
    # 2. Check for Transaction Pooler (PgBouncer default port is 6543 on Supabase)
    # If using port 6543, we MUST disable prepared statements.
    # If using port 5432 (Direct), we can keep them enabled for better performance.
    if db_url_obj.port == 6543:
        print("🛠️  Detected PgBouncer (Port 6543). Disabling prepared statements.")
        connect_args["statement_cache_size"] = 0
    else:
        print(f"⚡ Detected Direct Connection (Port {db_url_obj.port}). Prepared statements enabled.")

    # 3. Strip 'sslmode' query param to avoid conflicts with our manual SSL context
    query_params = dict(db_url_obj.query)
    if "sslmode" in query_params:
        print("🧹 Removing 'sslmode' query parameter (handled manually)")
        del query_params["sslmode"]
    
    # Ensure no conflicting args in query if we set them in connect_args
    if "statement_cache_size" in query_params:
         del query_params["statement_cache_size"]

    db_url_obj = db_url_obj._replace(query=query_params)
    
else:
    print("💻 Configuring database for LOCAL environment")

print(f"⚙️  Final connect_args: keys={list(connect_args.keys())}")

# Create async engine
# Create async engine
engine = create_async_engine(
    db_url_obj,
    echo=settings.DEBUG,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True if not is_production else False, # Pre-ping might attempt prepared statements
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Alias for code that imports async_session_factory
async_session_factory = async_session

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncSession:
    """Dependency for getting database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
