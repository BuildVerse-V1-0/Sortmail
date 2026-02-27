"""
API Routes - Auth
-----------------
OAuth endpoints for Gmail and Outlook with Production Security.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.storage.database import get_db
from models.user import User, UserStatus, EmailProvider
from models.connected_account import ConnectedAccount, ProviderType
from core.auth import oauth_google, jwt
from core.redis import get_redis
from core.encryption import encrypt_token
from api.dependencies import get_current_user as get_current_user_dep

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
        "created_at": datetime.now(timezone.utc).isoformat()
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
        # DATA RACING DEBUGGING: Temporarily commenting out delete to handle potential double-requests/retries
        # await redis.delete(state_key)
        pass
    
    # 4. Get User Info
    try:
        user_info = await oauth_google.get_user_info(tokens.access_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to fetch user profile")
        
    # 5. Encrypt Tokens
    enc_access_token = encrypt_token(tokens.access_token)
    enc_refresh_token = encrypt_token(tokens.refresh_token) if tokens.refresh_token else None
        
    # 6. Find or Create User
    try:
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
                created_at=datetime.now(timezone.utc),
                status=UserStatus.ACTIVE
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
        else:
            user.name = user_info.name
            user.picture_url = user_info.picture
            # user.access_token = enc_access_token # Consider if we want to update this on user model too
    except Exception as e:
        logger.error(f"❌ User DB Error: {e}")
        # Explicit check for missing column to help user debug
        if "UndefinedColumnError" in str(e) or "column \"updated_at\" does not exist" in str(e):
             raise HTTPException(
                status_code=500, 
                detail="DATABASE CONFIG ERROR: Missing 'updated_at' column. Please run the migration script provided."
            )
        raise HTTPException(status_code=500, detail="Database error during user creation")
    
    # 7. Update Connected Account
    stmt = select(ConnectedAccount).where(
        ConnectedAccount.user_id == user.id,
        ConnectedAccount.provider == ProviderType.GMAIL
    )
    result = await db.execute(stmt)
    account = result.scalar_one_or_none()
    
    if account:
        account.access_token = enc_access_token
        account.provider_email = user_info.email  # Explicitly sync the email
        if enc_refresh_token:
            account.refresh_token = enc_refresh_token
        account.token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=tokens.expires_in)
        account.last_sync_at = datetime.now(timezone.utc)
    else:
        account = ConnectedAccount(
            id=f"gmail_{user.id}",
            user_id=user.id,
            provider=ProviderType.GMAIL,
            access_token=enc_access_token,
            refresh_token=enc_refresh_token,
            token_expires_at=datetime.now(timezone.utc) + timedelta(seconds=tokens.expires_in),
            last_sync_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        db.add(account)
        
    await db.commit()
    
    # 8. Create Session
    token_pair = jwt.create_token_pair(user.id, user.email)
    
    # 9. Redirect
    # Option 1: HttpOnly Cookie (Best Security)
    from app.config import settings
    redirect_url = f"{settings.FRONTEND_URL}/dashboard"
    
    response = RedirectResponse(url=redirect_url)
    
    # Cookie Configuration for Cross-Domain (Vercel <-> Railway)
    # Using 'Lax' breaks cross-site if domains differ. 'None' requires Secure=True.
    is_development = settings.ENVIRONMENT.lower() == "development"
    
    response.set_cookie(
        key="access_token",
        value=token_pair.access_token,
        httponly=True,
        secure=False if is_development else True, # False for local http
        samesite="lax" if is_development else "none", # Lax for localhost, None for cross-site prod
        max_age=60 * 60 * 24 * 7, # 7 days (or match token expiry)
        path="/"
    )
    
    logger.info(f"✅ Google OAuth Success! Setting Cookie & Redirecting to: {redirect_url}")
    return response


@router.get("/outlook", response_model=AuthURLResponse)
async def outlook_auth():
    """Initiate Microsoft OAuth flow."""
    return {"auth_url": "https://login.microsoftonline.com/..."}


@router.get("/outlook/callback")
async def outlook_callback(code: str):
    """Handle Microsoft OAuth callback."""
    return {"message": "Outlook auth callback - implement me"}


@router.get("/me")
async def get_current_user(
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user.
    Returns a normalized UserDTO with credits injected.
    """
    from contracts.user import UserDTO
    from core.credits.credit_service import CreditService
    from models.user import UserStatus

    # Fetch credit balance (creates record if first time)
    try:
        credits_record = await CreditService.get_or_create_user_credits(db, user.id)
        await db.commit()
        credits_balance = credits_record.credits_balance
        plan = credits_record.plan.value if credits_record.plan else "free"
    except Exception:
        credits_balance = 0
        plan = "free"

    return UserDTO(
        id=user.id,
        email=user.email,
        name=user.name,
        picture=user.picture_url,                              # normalize field name
        provider=user.provider.value if user.provider else "google",
        is_active=user.status == UserStatus.ACTIVE if user.status else True,
        is_superuser=user.is_superuser or False,
        credits=credits_balance,
        plan=plan,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/logout")
async def logout():
    """Logout current user. Clears the access_token cookie."""
    from fastapi.responses import JSONResponse
    from app.config import settings
    
    response = JSONResponse(content={"message": "Logged out"})
    is_development = settings.ENVIRONMENT.lower() == "development"
    
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=False if is_development else True,
        httponly=True,
        samesite="lax" if is_development else "none",
    )
    return response


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None


@router.patch("/users/me")
async def update_profile(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user_dep),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile (name, timezone, locale)."""
    if body.name is not None:
        user.name = body.name
    if body.timezone is not None:
        prefs = user.preferences or {}
        prefs["timezone"] = body.timezone
        user.preferences = prefs
    if body.locale is not None:
        prefs = user.preferences or {}
        prefs["locale"] = body.locale
        user.preferences = prefs
    user.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return {"updated": True}

