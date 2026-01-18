"""
API Routes - Emails
-------------------
Email sync and management endpoints.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List

router = APIRouter()


@router.post("/sync")
async def sync_emails():
    """
    Trigger email sync from provider.
    
    Fetches new emails since last sync.
    """
    # TODO: Implement email sync
    return {"message": "Sync started", "status": "pending"}


@router.get("/sync/status")
async def sync_status():
    """Get current sync status."""
    return {
        "status": "idle",
        "last_sync": None,
        "threads_synced": 0,
    }
