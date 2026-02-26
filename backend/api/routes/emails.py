"""
API Routes - Emails
-------------------
Email sync and management endpoints.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta, timezone

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User
from models.connected_account import ConnectedAccount
from core.ingestion import IngestionService

router = APIRouter(redirect_slashes=False)

STALE_AFTER_MINUTES = 5  # Trigger background sync if last sync was > 5 min ago


@router.post("/sync")
async def sync_emails(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger incremental email sync in the background.
    Returns immediately — sync runs without blocking the response.
    Uses Gmail history API so only NEW emails since last sync are fetched.
    """
    from core.ingestion.sync_service import background_sync_user_emails
    
    background_tasks.add_task(background_sync_user_emails, current_user.id)
    return {"message": "Sync started in background", "status": "syncing"}


@router.get("/sync/status")
async def sync_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Return real sync state from DB.
    Frontend uses 'needs_sync' to decide if a background sync should be triggered.
    """
    stmt = select(ConnectedAccount).where(
        ConnectedAccount.user_id == current_user.id,
        ConnectedAccount.deleted_at == None  # noqa: E711
    )
    result = await db.execute(stmt)
    account = result.scalars().first()

    if not account:
        return {
            "has_account": False,
            "status": "no_account",
            "last_sync_at": None,
            "needs_sync": False,
        }

    last_sync = account.last_sync_at
    if last_sync and last_sync.tzinfo is None:
        last_sync = last_sync.replace(tzinfo=timezone.utc)

    stale_cutoff = datetime.now(timezone.utc) - timedelta(minutes=STALE_AFTER_MINUTES)
    needs_sync = (last_sync is None) or (last_sync < stale_cutoff)

    return {
        "has_account": True,
        "provider": account.provider.value,
        "provider_email": account.provider_email,
        "status": account.sync_status.value if account.sync_status else "idle",
        "last_sync_at": last_sync.isoformat() + "Z" if last_sync else None,
        "initial_sync_done": account.initial_sync_done,
        "needs_sync": needs_sync,           # Key flag for frontend
        "stale_after_minutes": STALE_AFTER_MINUTES,
    }
