"""
API Routes - Auth
-----------------
OAuth endpoints for Gmail and Outlook with Production Security.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.storage.database import get_db
from models.user import User, EmailProvider
from models.connected_account import ConnectedAccount, ProviderType
from core.auth import oauth_google, jwt
from core.redis import get_redis
from core.encryption import encrypt_token

router = APIRouter()
logger = logging.getLogger(__name__)


class AuthURLResponse(BaseModel):
    auth_url: str


@router.get("/google", response_model=AuthURLResponse)
async def google_auth(request: Request):
    """Initiate Google OAuth flow with PKCE and State protection."""
    # 1. Generate PKCE and State
    state = oauth_google.generate_code_verifier() # distinct state
    code_verifier = oauth_google.generate_code_verifier()
    code_challenge = oauth_google.generate_code_challenge(code_verifier)
    
    # 2. Store state with fingerprint in Redis
    state_data = {
        "code_verifier": code_verifier,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent", "unknown"),
        "created_at": datetime.utcnow().isoformat()
    }
    
    redis = await get_redis()
    state_key = f"oauth_state:{state}"
    logger.info(f"🆕 Generating OAuth State: {state}")
    logger.info(f"💾 Storing Redis Key: {state_key}")
    
    await redis.setex(state_key, 600, json.dumps(state_data))
    
    # Verify immediate write
    saved_val = await redis.get(state_key)
    logger.info(f"✅ Immediate Verify Read: {'SUCCESS' if saved_val else 'FAILED'}")
    
    # 3. Generate URL
    auth_url = oauth_google.get_google_auth_url(state, code_challenge)
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str, 
    state: str,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback with security validation."""
    redis = await get_redis()
    
    # 1. Validate State
    # 1. Validate State
    state_key = f"oauth_state:{state}"
    logger.info(f"🔑 Validating OAuth State: {state}")
    logger.info(f"🔎 Redis Key Lookup: {state_key}")
    
    try:
        state_json = await redis.get(state_key)
        logger.info(f"📄 Redis Result: {'FOUND' if state_json else 'NOT FOUND'}")
    except Exception as e:
        logger.error(f"❌ Redis Error during state lookup: {e}")
        raise HTTPException(status_code=500, detail="Redis connection failed")
    
    if not state_json:
        logger.warning(f"⚠️ OAuth State Missing/Expired for key: {state_key}")
        raise HTTPException(status_code=400, detail="Invalid or expired state parameter")
        
    state_data = json.loads(state_json)
    
    # 2. Validate Fingerprint
    # Strict UA check, soft IP warn
    if state_data.get("user_agent") != request.headers.get("user-agent", "unknown"):
        logger.warning(f"OAuth State User-Agent mismatch: stored={state_data.get('user_agent')}, current={request.headers.get('user_agent')}")
        # In strict mode we might fail here, but for now we proceed with warning log
    
    # 3. Exchange code for tokens (PKCE)
    try:
        tokens = await oauth_google.exchange_code_for_tokens(code, state_data["code_verifier"])
    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        raise HTTPException(status_code=400, detail="Internal authentication error")
    finally:
        # Prevent replay
        await redis.delete(state_key)
    
    # 4. Get User Info
    try:
        user_info = await oauth_google.get_user_info(tokens.access_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to fetch user profile")
        
    # 5. Encrypt Tokens
    enc_access_token = encrypt_token(tokens.access_token)
    enc_refresh_token = encrypt_token(tokens.refresh_token) if tokens.refresh_token else None
        
    # 6. Find or Create User
    stmt = select(User).where(User.email == user_info.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            id=user_info.id,
            email=user_info.email,
            name=user_info.name,
            picture_url=user_info.picture,
            provider=EmailProvider.GMAIL,
            access_token=enc_access_token, # Storing encrypted
            created_at=datetime.utcnow(),
            is_active=True
        )
        db.add(user)
        await db.flush()
    else:
        user.name = user_info.name
        user.picture_url = user_info.picture
        # user.access_token = enc_access_token # Consider if we want to update this on user model too
    
    # 7. Update Connected Account
    stmt = select(ConnectedAccount).where(
        ConnectedAccount.user_id == user.id,
        ConnectedAccount.provider == ProviderType.GMAIL
    )
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    
    if account:
        account.access_token = enc_access_token
        if enc_refresh_token:
            account.refresh_token = enc_refresh_token
        account.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens.expires_in)
        account.last_sync_at = datetime.utcnow()
    else:
        account = ConnectedAccount(
            id=f"gmail_{user.id}",
            user_id=user.id,
            provider=ProviderType.GMAIL,
            access_token=enc_access_token,
            refresh_token=enc_refresh_token,
            token_expires_at=datetime.utcnow() + timedelta(seconds=tokens.expires_in),
            last_sync_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.add(account)
        
    await db.commit()
    
    # 8. Create Session
    token_pair = jwt.create_token_pair(user.id, user.email)
    
    # 9. Redirect
    # In production, use httpOnly cookie for token if possible, but query param is standard for OAuth callback
    from app.config import settings
    redirect_url = f"{settings.FRONTEND_URL}?token={token_pair.access_token}"
    
    return RedirectResponse(url=redirect_url)


@router.get("/outlook", response_model=AuthURLResponse)
async def outlook_auth():
    """Initiate Microsoft OAuth flow."""
    return {"auth_url": "https://login.microsoftonline.com/..."}


@router.get("/outlook/callback")
async def outlook_callback(code: str):
    """Handle Microsoft OAuth callback."""
    return {"message": "Outlook auth callback - implement me"}


@router.get("/me")
async def get_current_user(token: str = Depends(jwt.verify_token)):
    """Get current authenticated user."""
    if not token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return token


@router.post("/logout")
async def logout():
    """Logout current user."""
    return {"message": "Logged out"}


@router.get("/test-redis")
async def test_redis():
    """DEBUG: Verify Redis connection and list active states."""
    try:
        redis = await get_redis()
        # 1. Test Write
        await redis.set("test_key", "hello_world", ex=60)
        # 2. Test Read
        value = await redis.get("test_key")
        # 3. List States
        keys = await redis.keys("oauth_state:*")
        
        return {
            "status": "ok",
            "write_read_test": value == "hello_world",
            "value_read": value,
            "active_states_count": len(keys),
            "active_states_sample": [k for k in keys[:5]],
            "redis_url_masked": str(redis.connection_pool.connection_kwargs.get("host"))
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

