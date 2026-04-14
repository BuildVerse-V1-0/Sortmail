"""
SortMail Backend - FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from api.dependencies import get_current_user
from models.user import User

from app.config import settings
from core.logging.sanitizer import setup_secure_logging
import logging

# Configure secure logging with sanitization
setup_secure_logging(
    environment=settings.ENVIRONMENT,
    debug=settings.DEBUG
)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info(f"Starting SortMail API v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    from core.storage.database import init_db
    from core.storage.vector_store import vector_store
    await init_db()
    
    # Initialize ChromaDB
    try:
        ok = await vector_store.initialize()
        if ok:
            logger.info("ChromaDB initialized successfully")
        else:
            logger.warning("ChromaDB initialization failed — proceeding without vector search")
    except Exception as e:
        logger.error(f"ChromaDB initialization error: {e}")
        logger.warning("Proceeding without vector search")
    
    # Start Background AI Worker when explicitly enabled for this process.
    worker_enabled = os.getenv("AI_WORKER_ENABLED", "true").strip().lower() in {"1", "true", "yes", "on"}
    if worker_enabled and hasattr(settings, "REDIS_URL") and settings.REDIS_URL:
        from core.intelligence.processing_queue import intelligence_worker
        import asyncio
        app.state.ai_worker_task = asyncio.create_task(intelligence_worker(settings.REDIS_URL))
    elif not worker_enabled:
        logger.info("AI_WORKER_ENABLED is false. Skipping AI Background Worker startup.")
    else:
        logger.warning("REDIS_URL not configured. AI Background Worker will not start.")
        
    yield
    # Shutdown
    logger.info("Shutting down SortMail API")
    try:
        from core.redis import RedisClient
        await RedisClient.close()
    except Exception as e:
        logger.warning(f"Redis shutdown cleanup failed: {e}")


app = FastAPI(
    title="SortMail API",
    description="AI Intelligence Layer for Gmail & Outlook",
    version=settings.VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan,
)

# Trust Railway's X-Forwarded-Proto header so FastAPI generates https:// redirect URLs
# (Without this, 307 trailing-slash redirects use http:// because Railway terminates SSL)
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# CORS
# Enhanced CORS to support Vercel deployments
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [o.strip() for o in origins.split(",")]

# Local Development Support
if settings.ENVIRONMENT.lower() == "development":
    if "http://localhost:3000" not in origins:
        origins.append("http://localhost:3000")
    if "http://127.0.0.1:3000" not in origins:
        origins.append("http://127.0.0.1:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://sortmail.*\.vercel\.app", # Allow all Vercel previews
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Security Middleware
from api.middleware.security import (
    OriginServiceGateMiddleware,
    SecurityHeadersMiddleware, 
    RateLimitMiddleware,
    RequestIDMiddleware,
    SanitizedAccessLogMiddleware,
)

app.add_middleware(SanitizedAccessLogMiddleware)
app.add_middleware(OriginServiceGateMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestIDMiddleware)


# Global exception handler — ensures CORS headers are present even on 500 crashes.
# Without this, CORSMiddleware doesn't run on unhandled exceptions and the browser
# reports "CORS blocked" instead of the real error.
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "")
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Production: Hide internal errors; Development: Show details
    if settings.ENVIRONMENT.lower() == "production":
        error_detail = "Internal server error"
    else:
        error_detail = str(exc)
    
    return JSONResponse(
        status_code=500,
        content={"detail": error_detail},
        headers={
            "Access-Control-Allow-Origin": origin or "*",
            "Access-Control-Allow-Credentials": "true",
        },
    )



@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "SortMail API",
        "version": settings.VERSION,
        "status": "running",
    }


@app.get("/health")
async def health():
    """Comprehensive health check for monitoring and alerting."""
    checks = {
        "api": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "vector_store": "unknown",
        "ai_worker": "unknown",
    }
    redis_metrics = None

    # Database health
    try:
        from core.storage.database import async_session

        async with async_session() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as exc:
        checks["database"] = f"unhealthy: {str(exc)}"

    # Redis health
    try:
        from core.redis import get_redis
        from core.redis_metrics import get_redis_metrics_snapshot

        redis = await get_redis()
        await redis.ping()
        checks["redis"] = "healthy"
        redis_metrics = get_redis_metrics_snapshot()
    except Exception as exc:
        checks["redis"] = f"unhealthy: {str(exc)}"

    # Vector store health
    try:
        from core.storage.vector_store import vector_store

        checks["vector_store"] = "healthy" if vector_store._collection is not None else "not_initialized"
    except Exception as exc:
        checks["vector_store"] = f"unhealthy: {str(exc)}"

    # AI worker health
    worker_task = getattr(app.state, "ai_worker_task", None)
    if worker_task is None:
        checks["ai_worker"] = "not_running"
    elif worker_task.done():
        checks["ai_worker"] = "stopped"
    else:
        checks["ai_worker"] = "healthy"

    service_states = [value for key, value in checks.items() if key != "api"]
    degraded_states = ("unhealthy", "stopped")
    overall_status = "degraded" if any(state.startswith(degraded_states) for state in service_states) else "healthy"

    return {
        "status": overall_status,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": checks,
        "redis_metrics": redis_metrics,
    }


@app.get("/health/simple")
async def simple_health():
    """Lightweight probe endpoint for uptime checks."""
    return {"status": "ok", "version": settings.VERSION}


# Import and include routers
from api.routes import (
    auth, emails, threads, tasks, drafts, reminders,
    dashboard, admin_credits, notifications, credits, accounts, admin_users, admin_metrics, events, webhooks,
    proxy, ai, attachments, contacts, tags, settings as app_settings, search, bin
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(threads.router, prefix="/api/threads", tags=["threads"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(drafts.router, prefix="/api/drafts", tags=["drafts"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["reminders"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(admin_credits.router, prefix="/api/admin/credits", tags=["admin"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(credits.router, prefix="/api/credits", tags=["credits"])
app.include_router(accounts.router, prefix="/api/connected-accounts", tags=["accounts"])
app.include_router(admin_users.router, prefix="/api/admin", tags=["admin"])
app.include_router(admin_metrics.router, prefix="/api/admin/metrics", tags=["admin"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(attachments.router, prefix="/api/attachments", tags=["attachments"])
app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(bin.router, prefix="/api/bin", tags=["bin"])
app.include_router(proxy.router, prefix="/api", tags=["proxy"])
app.include_router(app_settings.router, prefix="/api/settings", tags=["settings"])


def _docs_access_enabled() -> bool:
    if settings.ENVIRONMENT.lower() == "production" and settings.DISABLE_API_DOCS_IN_PRODUCTION:
        return False
    return settings.DEBUG or settings.ENVIRONMENT.lower() != "production"


async def _require_docs_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


if _docs_access_enabled():
    @app.get("/docs", include_in_schema=False)
    async def secure_docs(_: User = Depends(_require_docs_superuser)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title=f"{app.title} - Docs")


    @app.get("/openapi.json", include_in_schema=False)
    async def secure_openapi(_: User = Depends(_require_docs_superuser)):
        return JSONResponse(
            get_openapi(
                title=app.title,
                version=app.version,
                description=app.description,
                routes=app.routes,
            )
        )

from pydantic import BaseModel
from typing import Optional
from core.storage.vector_store import get_chroma_collection

class RequestBody(BaseModel):
    ids: list[str]
    documents: list[str]
    metadatas: list[dict]

@app.post("/api/documents/")
async def add_documents(
    request: RequestBody,
    current_user: User = Depends(get_current_user),  # enforce auth
    col=Depends(get_chroma_collection)
):
    # Enforce user_id in every metadata dict so documents can never
    # cross user boundaries when queried with the user_id where-filter.
    for meta in request.metadatas:
        meta["user_id"] = current_user.id

    try:
        col.add(
            ids=request.ids,
            documents=request.documents,
            metadatas=request.metadatas
        )
        return {"message": "Documents added successfully", "ids": request.ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
