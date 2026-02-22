"""
API Routes - Connected Accounts
---------------------------------
User's connected email provider accounts (Gmail, Outlook).
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel
from datetime import datetime

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User
from models.connected_account import ConnectedAccount, AccountStatus

router = APIRouter()


class ConnectedAccountOut(BaseModel):
    id: str
    email: str
    provider: str
    status: str
    sync_status: Optional[str]
    last_sync_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ConnectedAccountOut])
async def list_connected_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all connected email accounts for the current user."""
    stmt = select(ConnectedAccount).where(
        ConnectedAccount.user_id == current_user.id,
        ConnectedAccount.status != AccountStatus.DISCONNECTED,
    )
    result = await db.execute(stmt)
    accounts = result.scalars().all()
    return [
        ConnectedAccountOut(
            id=a.id,
            email=a.provider_email,
            provider=a.provider.value,
            status=a.status.value,
            sync_status=a.sync_status.value if a.sync_status else None,
            last_sync_at=a.last_sync_at,
            created_at=a.created_at,
        )
        for a in accounts
    ]


@router.post("/{account_id}/sync")
async def trigger_sync(
    account_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Trigger a manual email sync for a connected account."""
    stmt = select(ConnectedAccount).where(
        ConnectedAccount.id == account_id,
        ConnectedAccount.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Queue sync (reuse existing email sync logic)
    from core.ingestion.ingestion_service import IngestionService
    async def run_sync():
        from core.storage.database import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            service = IngestionService(session)
            await service.sync_user_emails(current_user.id)

    background_tasks.add_task(run_sync)
    return {"status": "sync_queued", "account_id": account_id}


@router.post("/{account_id}/disconnect")
async def disconnect_account(
    account_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Disconnect a connected email account (stops sync)."""
    stmt = (
        update(ConnectedAccount)
        .where(
            ConnectedAccount.id == account_id,
            ConnectedAccount.user_id == current_user.id,
        )
        .values(status=AccountStatus.DISCONNECTED)
    )
    await db.execute(stmt)
    await db.commit()
    return {"disconnected": True, "account_id": account_id}
