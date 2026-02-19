"""
SortMail Backend - FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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
from api.routes import auth, emails, threads, tasks, drafts, reminders, dashboard

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(emails.router, prefix="/api/emails", tags=["emails"])
app.include_router(threads.router, prefix="/api/threads", tags=["threads"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(drafts.router, prefix="/api/drafts", tags=["drafts"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["reminders"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
