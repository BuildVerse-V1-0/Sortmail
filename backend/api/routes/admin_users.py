"""
API Routes - Admin Users
------------------------
Admin-only endpoints for user management.
Requires is_superuser = True.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, desc
from pydantic import BaseModel
from datetime import datetime

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User, UserStatus
from models.credits import UserCredits
from core.credits.credit_service import CreditService, TransactionType

router = APIRouter()


# --- Guard ---

async def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


# --- DTOs ---

class AdminUserOut(BaseModel):
    id: str
    email: str
    name: Optional[str]
    provider: str
    status: str
    is_superuser: bool
    credits_balance: int
    plan: str
    created_at: datetime
    last_login_at: Optional[datetime]


class SuspendRequest(BaseModel):
    reason: Optional[str] = "Admin action"


class CreditAdjustRequest(BaseModel):
    user_id: str         # str (not UUID) — matches User.id column type
    amount: int          # positive to add, negative to deduct
    reason: str


# --- Endpoints ---

@router.get("/users", response_model=List[AdminUserOut])
async def list_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = None,
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """List all users with their credit info."""
    stmt = select(User, UserCredits).outerjoin(
        UserCredits, UserCredits.user_id == User.id
    ).order_by(desc(User.created_at)).limit(limit).offset(offset)

    if search:
        stmt = stmt.where(User.email.ilike(f"%{search}%"))

    result = await db.execute(stmt)
    rows = result.all()

    return [
        AdminUserOut(
            id=u.id,
            email=u.email,
            name=u.name,
            provider=u.provider.value if u.provider else "google",
            status=u.status.value if u.status else "active",
            is_superuser=u.is_superuser or False,
            credits_balance=c.credits_balance if c else 0,
            plan=c.plan.value if c and c.plan else "free",
            created_at=u.created_at,
            last_login_at=u.last_login_at,
        )
        for u, c in rows
    ]


@router.get("/users/{user_id}", response_model=AdminUserOut)
async def get_user(
    user_id: str,
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific user's details."""
    stmt = (
        select(User, UserCredits)
        .outerjoin(UserCredits, UserCredits.user_id == User.id)
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    u, c = row
    return AdminUserOut(
        id=u.id,
        email=u.email,
        name=u.name,
        provider=u.provider.value if u.provider else "google",
        status=u.status.value if u.status else "active",
        is_superuser=u.is_superuser or False,
        credits_balance=c.credits_balance if c else 0,
        plan=c.plan.value if c and c.plan else "free",
        created_at=u.created_at,
        last_login_at=u.last_login_at,
    )


@router.patch("/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    body: SuspendRequest,
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Suspend a user account."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot suspend yourself")
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(status=UserStatus.SUSPENDED)
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    await db.commit()
    return {"suspended": True, "user_id": user_id}


@router.patch("/users/{user_id}/unsuspend")
async def unsuspend_user(
    user_id: str,
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Reactivate a suspended user."""
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(status=UserStatus.ACTIVE)
    )
    result = await db.execute(stmt)
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    await db.commit()
    return {"unsuspended": True, "user_id": user_id}


@router.patch("/users/{user_id}/toggle-admin")
async def toggle_superuser(
    user_id: str,
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Toggle superuser status for a user."""
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot change your own superuser status")
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_superuser = not user.is_superuser
    await db.commit()
    return {"user_id": user_id, "is_superuser": user.is_superuser}


@router.post("/credits/adjust")
async def adjust_credits(
    body: CreditAdjustRequest,
    admin: User = Depends(require_superuser),
    db: AsyncSession = Depends(get_db),
):
    """Manually add or deduct credits from a user (admin)."""
    # Verify user exists
    stmt = select(User.id).where(User.id == body.user_id)
    if not (await db.execute(stmt)).scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")
        
    try:
        new_balance = await CreditService.add_credits(
            db,
            body.user_id,
            body.amount,
            TransactionType.ADMIN_ADJUSTMENT,
            metadata={"reason": body.reason, "admin_id": admin.id},
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    return {"success": True, "new_balance": new_balance, "user_id": body.user_id}
