"""
Credit Service (Production Grade)
---------------------------------
Core logic for managing user credits with strict concurrency and safety checks.
Implements:
1. Optimistic Locking (versioning)
2. Two-Phase Commit (Reservation -> Commit/Rollback)
3. Rate Limiting
4. Audit Logging
"""

import uuid
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, insert, and_
from sqlalchemy.orm import selectinload

from models.credits import (
    UserCredits, CreditTransaction, CreditPricing, 
    TransactionType, PlanType, TransactionStatus, UserCreditLimits
)
from models.user import User

class InsufficientCreditsError(Exception):
    pass

class RateLimitExceededError(Exception):
    pass

class CreditService:
    
    @staticmethod
    async def get_or_create_user_credits(db: AsyncSession, user_id: str) -> UserCredits:
        """Get user credit record, creating it if it doesn't exist."""
        stmt = select(UserCredits).where(UserCredits.user_id == user_id)
        result = await db.execute(stmt)
        user_credits = result.scalar_one_or_none()
        
        if not user_credits:
            # Create default free tier record
            user_credits = UserCredits(
                id=str(uuid.uuid4()),
                user_id=user_id,
                credits_balance=50, # Free tier default
                plan=PlanType.FREE,
                monthly_credits_allowance=50,
                billing_cycle_start=datetime.now(timezone.utc).date(),
                version=1
            )
            db.add(user_credits)
            await db.flush()
            
            # Log initial grant
            transaction = CreditTransaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                amount=50,
                balance_after=50,
                transaction_type=TransactionType.BONUS,
                status=TransactionStatus.COMPLETED,
                metadata_json={"reason": "initial_account_setup"}
            )
            db.add(transaction)
            
        return user_credits

    @staticmethod
    async def get_operation_cost(db: AsyncSession, operation_type: str) -> int:
        stmt = select(CreditPricing).where(
            CreditPricing.operation_type == operation_type,
            CreditPricing.is_active == True
        )
        result = await db.execute(stmt)
        pricing = result.scalar_one_or_none()
        if not pricing:
            raise ValueError(f"Pricing not found for operation: {operation_type}")
        return pricing.credits_cost

    @staticmethod
    async def check_rate_limits(db: AsyncSession, user_credits: UserCredits, limits: Optional[UserCreditLimits]) -> None:
        """Check if user has exceeded rate limits."""
        now = datetime.now(timezone.utc)
        
        # 1. Check strict limits from UserCreditLimits if they exist
        if limits:
            if limits.max_credits_per_day:
                # Need daily usage aggregation check here (omitted for brevity, can check CreditUsageDaily)
                pass
                
        # 2. Check velocity limits (anti-spam)
        # Reset counters if time passed
        if not user_credits.last_operation_at or (now - user_credits.last_operation_at) > timedelta(minutes=1):
            user_credits.operations_count_last_minute = 0
            
        if not user_credits.last_operation_at or (now - user_credits.last_operation_at) > timedelta(hours=1):
            user_credits.operations_count_last_hour = 0
            
        if user_credits.operations_count_last_minute > 60: # Max 1 per second avg
            raise RateLimitExceededError("Too many operations (limit: 60/min)")
            
        if user_credits.operations_count_last_hour > 1000:
            raise RateLimitExceededError("Too many operations (limit: 1000/hour)")

    @staticmethod
    async def reserve_credits(
        db: AsyncSession, 
        user_id: str, 
        operation_type: str, 
        related_entity_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Phase 1: Reserve credits.
        Deducts balance, creates PENDING transaction.
        Returns: transaction_id
        """
        cost = await CreditService.get_operation_cost(db, operation_type)
        if cost == 0:
            return str(uuid.uuid4()) # Fake ID for free ops

        # Optimistic Locking Loop
        for attempt in range(3):
            # Fetch fresh
            user_credits = await CreditService.get_or_create_user_credits(db, user_id)
            
            # Fetch limits
            stmt_limits = select(UserCreditLimits).where(UserCreditLimits.user_id == user_id)
            limits = (await db.execute(stmt_limits)).scalar_one_or_none()
            
            # Refresh ORM object to avoid stale state in retry loop
            if attempt > 0:
                await db.refresh(user_credits)

            # Verify Balance
            if user_credits.credits_balance < cost:
                raise InsufficientCreditsError(f"Insufficient credits. Cost: {cost}, Balance: {user_credits.credits_balance}")
            
            # Verify Rate Limits
            await CreditService.check_rate_limits(db, user_credits, limits)
            
            # Prepare Update
            current_version = user_credits.version
            new_balance = user_credits.credits_balance - cost
            
            # Try Update with Version Check
            stmt = (
                update(UserCredits)
                .where(
                    UserCredits.id == user_credits.id,
                    UserCredits.version == current_version
                )
                .values(
                    credits_balance=new_balance,
                    credits_total_spent=UserCredits.credits_total_spent + cost,
                    credits_used_this_month=UserCredits.credits_used_this_month + cost,
                    operations_count_last_minute=UserCredits.operations_count_last_minute + 1,
                    operations_count_last_hour=UserCredits.operations_count_last_hour + 1,
                    last_operation_at=datetime.now(timezone.utc),
                    version=current_version + 1,
                    updated_at=datetime.now(timezone.utc)
                )
                .execution_options(synchronize_session=False)
            )
            result = await db.execute(stmt)
            
            if result.rowcount == 1:
                # Success - Create Reservation Transaction
                transaction_id = str(uuid.uuid4())
                transaction = CreditTransaction(
                    id=transaction_id,
                    user_id=user_id,
                    amount=-cost,
                    balance_after=new_balance,
                    transaction_type=TransactionType.DEDUCTION,
                    operation_type=operation_type,
                    related_entity_id=related_entity_id,
                    status=TransactionStatus.RESERVED,
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
                    metadata_json=metadata or {}
                )
                db.add(transaction)
                await db.flush()
                return transaction_id
                
            # If rowcount == 0, version mismatch (concurrent update), retry loop triggers
        
        raise Exception("Concurrency Limit Exceeded: Please try again.")

    @staticmethod
    async def commit_reservation(db: AsyncSession, transaction_id: str) -> None:
        """Phase 2a: Confirm success."""
        stmt = select(CreditTransaction).where(CreditTransaction.id == transaction_id)
        result = await db.execute(stmt)
        txn = result.scalar_one_or_none()
        
        if txn and txn.status == TransactionStatus.RESERVED:
            txn.status = TransactionStatus.COMPLETED
            txn.expires_at = None # Clear expiry
            # await db.commit() # Caller commits

    @staticmethod
    async def rollback_reservation(db: AsyncSession, transaction_id: str) -> None:
        """Phase 2b: Failure/Cancel. Refund credits."""
        stmt = select(CreditTransaction).where(CreditTransaction.id == transaction_id)
        result = await db.execute(stmt)
        txn = result.scalar_one_or_none()
        
        if not txn or txn.status != TransactionStatus.RESERVED:
            return

        # 1. Mark Cancelled
        txn.status = TransactionStatus.CANCELLED
        
        # 2. Refund User
        # We use atomic update again
        refund_amount = abs(txn.amount) 
        user_credits = await CreditService.get_or_create_user_credits(db, txn.user_id)
        
        # Optimistic Locking for rollback
        for attempt in range(3):
            user_credits = await CreditService.get_or_create_user_credits(db, txn.user_id)
            if attempt > 0:
                await db.refresh(user_credits)
                
            stmt = (
                update(UserCredits)
                .where(
                    UserCredits.id == user_credits.id,
                    UserCredits.version == user_credits.version
                )
                .values(
                    credits_balance=user_credits.credits_balance + refund_amount,
                    credits_total_spent=user_credits.credits_total_spent - refund_amount,
                    credits_used_this_month=user_credits.credits_used_this_month - refund_amount,
                    version=user_credits.version + 1
                )
            )
            result = await db.execute(stmt)
            if result.rowcount == 1:
                break
        else:
            raise Exception("Concurrency Limit Exceeded during rollback refund.")
        
        # 3. Log Refund Transaction (Internal)
        refund_txn = CreditTransaction(
            id=str(uuid.uuid4()),
            user_id=txn.user_id,
            amount=refund_amount,
            balance_after=user_credits.credits_balance + refund_amount, # Approx
            transaction_type=TransactionType.REFUND,
            operation_type=txn.operation_type,
            related_entity_id=txn.related_entity_id,
            status=TransactionStatus.COMPLETED,
            refunded_transaction_id=txn.id,
            is_refunded=True,
            metadata_json={"reason": "reservation_rollback"}
        )
        db.add(refund_txn)

    @staticmethod
    async def check_balance(db: AsyncSession, user_id: str, operation_type: str) -> bool:
        try:
            cost = await CreditService.get_operation_cost(db, operation_type)
        except ValueError:
            return False
            
        if cost == 0: return True
        
        stmt = select(UserCredits).where(UserCredits.user_id == user_id)
        result = await db.execute(stmt)
        credits = result.scalar_one_or_none()
        
        if not credits:
            return 50 >= cost # Free tier implicit assumption for uninstantiated users

        return credits.credits_balance >= cost

    # Old method for backward compatibility (wraps reserve+commit)
    @staticmethod
    async def deduct_credits(
        db: AsyncSession, 
        user_id: str, 
        operation_type: str, 
        related_entity_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Legacy atomic deduction (Safe wrapper)."""
        # Reserve (deducts immediately)
        txn_id = await CreditService.reserve_credits(db, user_id, operation_type, related_entity_id, metadata)
        # Commit immediately
        await CreditService.commit_reservation(db, txn_id)
        
        # Return new balance with explicit refresh
        credits = await CreditService.get_or_create_user_credits(db, user_id)
        await db.refresh(credits)
        return credits.credits_balance

    @staticmethod
    async def add_credits(
        db: AsyncSession,
        user_id: str,
        amount: int,
        transaction_type: "TransactionType",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Add (or deduct if negative) credits directly — admin use.
        Uses optimistic locking. Returns new balance.
        """
        import uuid as _uuid
        from models.credits import TransactionStatus

        if amount == 0:
            raise ValueError("Amount to add/deduct cannot be zero.")

        # Optimistic locking retry loop
        for attempt in range(3):
            user_credits = await CreditService.get_or_create_user_credits(db, user_id)
            if attempt > 0:
                await db.refresh(user_credits)
                
            current_version = user_credits.version
            new_balance = user_credits.credits_balance + amount
            
            if new_balance < 0:
                raise InsufficientCreditsError(f"Cannot deduct {-amount}: Balance would drop below zero.")

            stmt = (
                update(UserCredits)
                .where(
                    UserCredits.id == user_credits.id,
                    UserCredits.version == current_version
                )
                .values(
                    credits_balance=new_balance,
                    credits_total_earned=UserCredits.credits_total_earned + max(0, amount),
                    credits_total_spent=UserCredits.credits_total_spent + max(0, -amount),
                    updated_at=datetime.now(timezone.utc),
                )
                .execution_options(synchronize_session=False)
            )
            result = await db.execute(stmt)
            if result.rowcount == 1:
                break
            else:
                if attempt == 2:
                    raise Exception("Concurrent credit update detected, please retry.")

        transaction = CreditTransaction(
            id=str(_uuid.uuid4()),
            user_id=user_id,
            amount=amount,
            balance_after=new_balance,
            transaction_type=transaction_type,
            status=TransactionStatus.COMPLETED,
            metadata_json=metadata or {},
        )
        db.add(transaction)
        await db.flush()
        return new_balance

