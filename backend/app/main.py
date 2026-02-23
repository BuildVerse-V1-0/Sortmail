"""
SortMail Backend - FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print(f"🚀 Starting SortMail API v{settings.VERSION}")
    print(f"📧 Environment: {settings.ENVIRONMENT}")
    from core.storage.database import init_db
    await init_db()
    yield
    # Shutdown
    print("👋 Shutting down SortMail API")


app = FastAPI(
    title="SortMail API",
    description="AI Intelligence Layer for Gmail & Outlook",
    version=settings.VERSION,
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
    SecurityHeadersMiddleware, 
    RateLimitMiddleware,
    RequestIDMiddleware
)

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
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
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
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from api.routes import (
    auth, emails, threads, tasks, drafts, reminders,
    dashboard, admin_credits, notifications, credits, accounts, admin_users, events
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
app.include_router(events.router, prefix="/api/events", tags=["events"])

