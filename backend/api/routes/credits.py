"""
API Routes - Credits
--------------------
User-facing credit balance and transaction history endpoints.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel

from core.storage.database import get_db
from api.dependencies import get_current_user
from models.user import User
from models.credits import UserCredits, CreditTransaction
from core.credits.credit_service import CreditService

router = APIRouter()


class CreditBalanceResponse(BaseModel):
    balance: int
    plan: str
    monthly_allowance: int
    used_this_month: int
    resets_on: Optional[str]  # ISO date string


class TransactionOut(BaseModel):
    id: str
    amount: int
    balance_after: int
    transaction_type: str
    operation_type: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/me", response_model=CreditBalanceResponse)
async def get_my_credits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's credit balance and plan info."""
    credits = await CreditService.get_or_create_user_credits(db, current_user.id)
    await db.commit()

    # Calculate reset date (billing_cycle_start + 1 month)
    from dateutil.relativedelta import relativedelta
    resets_on = None
    if credits.billing_cycle_start:
        reset_date = credits.billing_cycle_start + relativedelta(months=1)
        resets_on = reset_date.isoformat()

    return CreditBalanceResponse(
        balance=credits.credits_balance,
        plan=credits.plan.value if credits.plan else "free",
        monthly_allowance=credits.monthly_credits_allowance,
        used_this_month=credits.credits_used_this_month,
        resets_on=resets_on,
    )


@router.get("/me/transactions", response_model=List[TransactionOut])
async def get_my_transactions(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    type_filter: Optional[str] = Query(default=None, alias="type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the current user's credit transaction history."""
    stmt = (
        select(CreditTransaction)
        .where(CreditTransaction.user_id == current_user.id)
        .order_by(desc(CreditTransaction.created_at))
        .limit(limit)
        .offset(offset)
    )
    if type_filter:
        stmt = stmt.where(CreditTransaction.transaction_type == type_filter)

    result = await db.execute(stmt)
    transactions = result.scalars().all()
    return transactions
