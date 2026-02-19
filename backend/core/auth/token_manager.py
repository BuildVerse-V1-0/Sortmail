"""
Token Manager
-------------
Handles secure lifecycle of OAuth tokens:
- Retrieval from DB
- Decryption
- Automatic Refresh with Redis Locks
- Persistence of new tokens
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.connected_account import ConnectedAccount, ProviderType
from core.auth import oauth_google
from core.encryption import encrypt_token, decrypt_token
from core.redis import get_redis
from core.storage.database import async_session_factory

logger = logging.getLogger(__name__)

class TokenRevokedError(Exception):
    pass

class TokenExpiredError(Exception):
    pass

async def get_valid_google_token(user_id: str) -> str:
    """
    Get a valid access token for a user's Google account.
    Handles refresh automatically with distributed locking.
    """
    async with async_session_factory() as db:
        stmt = select(ConnectedAccount).where(
            ConnectedAccount.user_id == user_id,
            ConnectedAccount.provider == ProviderType.GMAIL
        )
        result = await db.execute(stmt)
        account = result.scalar_one_or_none()
        
        if not account:
            raise ValueError(f"No connected Gmail account for user {user_id}")
            
        if account.status == "revoked":
            raise TokenRevokedError("Account access has been revoked by user")

        # Check expiration (refresh if < 5 mins remaining)
        now = datetime.utcnow()
        if account.token_expires_at and account.token_expires_at < now + timedelta(minutes=5):
            return await _refresh_google_token(db, account)
            
        # Token is valid, decrypt and return
        try:
            return decrypt_token(account.access_token)
        except Exception:
            logger.error(f"Failed to decrypt access token for user {user_id}")
            raise

async def _refresh_google_token(db: AsyncSession, account: ConnectedAccount) -> str:
    """
    Refresh Google token with Redis lock protection.
    """
    redis = await get_redis()
    lock_key = f"lock:refresh:{account.user_id}"
    
    # Try to acquire lock
    # nx=True (Only set if not exists), ex=30 (Expire in 30s)
    acquired = await redis.set(lock_key, "1", nx=True, ex=30)
    
    if not acquired:
        # Lock exists, wait for other process to refresh
        logger.info(f"Waiting for token refresh lock for user {account.user_id}")
        for _ in range(10): # Wait up to 2 seconds
            await asyncio.sleep(0.2)
            # Re-fetch account to see if updated
            await db.refresh(account)
            if account.token_expires_at > datetime.utcnow() + timedelta(minutes=1):
                return decrypt_token(account.access_token)
        
        # If we timeout waiting, assume other process failed and we should try (or just fail)
        # For robustness, we'll try one more time or just fail this request
        raise Exception("Timeout waiting for token refresh")

    # Lock acquired, proceed with refresh
    try:
        try:
            refresh_token = decrypt_token(account.refresh_token)
        except Exception:
            logger.error(f"Failed to decrypt refresh token for user {account.user_id}")
            raise TokenRevokedError("Invalid refresh token")

        try:
            new_tokens = await oauth_google.refresh_access_token(refresh_token)
        except Exception as e:
            logger.error(f"Google token refresh failed for user {account.user_id}: {e}")
            if "invalid_grant" in str(e) or "revoked" in str(e):
                account.status = "revoked"
                account.sync_status = "failed"
                account.sync_error = "Token revoked during refresh"
                await db.commit()
                raise TokenRevokedError("Token revoked")
            raise

        # Update DB
        account.access_token = encrypt_token(new_tokens.access_token)
        if new_tokens.refresh_token:
             # Google only returns refresh token if requested or limit exceeded, 
             # but sometimes they rotate it.
            account.refresh_token = encrypt_token(new_tokens.refresh_token)
            
        account.token_expires_at = datetime.utcnow() + timedelta(seconds=new_tokens.expires_in)
        await db.commit()
        
        return new_tokens.access_token
        
    finally:
        # Release lock
        await redis.delete(lock_key)
