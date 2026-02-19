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
connect_args = {}
if settings.ENVIRONMENT == "production" or "railway" in settings.DATABASE_URL or "railway" in (db_url_obj.host or ""):
    # Create a custom SSL context that ignores hostname verification if needed
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ctx
    
    # IMPORTANT: Remove 'sslmode' or other query params that might conflict with asyncpg
    # asyncpg does not support 'sslmode' in the query string when using connect_args['ssl']
    query_params = dict(db_url_obj.query)
    if "sslmode" in query_params:
        del query_params["sslmode"]
    
    # Reconstruct URL without conflicting params
    db_url_obj = db_url_obj._replace(query=query_params)

# Create async engine
engine = create_async_engine(
    db_url_obj,
    echo=settings.DEBUG,
    future=True,
    connect_args=connect_args,
    pool_pre_ping=True, # Verify connection before usage
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

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
