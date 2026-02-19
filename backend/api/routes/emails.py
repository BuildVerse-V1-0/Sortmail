"""
API Routes - Emails
-------------------
Email sync and management endpoints.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User
from core.ingestion import IngestionService

router = APIRouter()


@router.post("/sync")
async def sync_emails(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger email sync from provider.
    
    Fetches new emails since last sync.
    """
    service = IngestionService(db)
    
    # Run sync in background to avoid blocking response
    # For MVP, we might want to await it to see errors, 
    # but for production "ingestion bit by bit", background is better.
    # However, since we are "bit by bit testing", maybe query param to force sync?
    # Let's await it for now for immediate feedback to user, or use logic below.
    
    try:
        await service.sync_user_emails(current_user.id)
        return {"message": "Sync completed successfully", "status": "completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sync/status")
async def sync_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current sync status."""
    # TODO: Fetch from ConnectedAccount
    return {
        "status": "idle",
        "last_sync": "Never", # Placeholder
        "threads_synced": 0,
    }
