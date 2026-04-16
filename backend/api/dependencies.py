"""
API Dependencies
----------------
Common dependencies like authentication and database sessions.
"""

import logging
from threading import Lock
from time import monotonic
from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from core.storage.database import get_db
from core.auth import jwt
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False) 

_AUTH_ATTEMPT_LOG_INTERVAL_SECONDS = 15.0
_auth_log_lock = Lock()
_auth_log_last_flush = monotonic()
_auth_log_counts = {
    "total": 0,
    "header": 0,
    "cookie": 0,
    "both": 0,
    "neither": 0,
}


def _record_auth_attempt(has_header: bool, has_cookie: bool, logger: logging.Logger) -> None:
    """Log auth attempt volume as a periodic summary instead of every request."""
    global _auth_log_last_flush

    now = monotonic()
    with _auth_log_lock:
        _auth_log_counts["total"] += 1
        if has_header:
            _auth_log_counts["header"] += 1
        if has_cookie:
            _auth_log_counts["cookie"] += 1
        if has_header and has_cookie:
            _auth_log_counts["both"] += 1
        if not has_header and not has_cookie:
            _auth_log_counts["neither"] += 1

        elapsed = now - _auth_log_last_flush
        if elapsed < _AUTH_ATTEMPT_LOG_INTERVAL_SECONDS:
            return

        snapshot = dict(_auth_log_counts)
        for key in _auth_log_counts:
            _auth_log_counts[key] = 0
        _auth_log_last_flush = now

    # Build a fully formatted message to avoid placeholder mismatch if downstream
    # sanitizers rewrite sensitive tokens in log text.
    logger.debug(
        "Auth attempt summary "
        f"({elapsed:.1f}s): "
        f"total={snapshot['total']} "
        f"header={snapshot['header']} "
        f"ck={snapshot['cookie']} "
        f"both={snapshot['both']} "
        f"neither={snapshot['neither']}"
    )

async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    access_token: Optional[str] = Cookie(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Validate token and return current user.
    Prioritizes Bearer Header, falls back to 'access_token' Cookie.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 1. Try Bearer Header (Best for API Clients)
    # 2. Try Cookie (Best for Browser/Frontend)
    logger = logging.getLogger(__name__)
    has_header = token is not None
    has_cookie = access_token is not None
    _record_auth_attempt(has_header, has_cookie, logger)
    
    token_to_validate = token or access_token
    
    if not token_to_validate:
        logger.debug("No token or cookie found. Raising 401.")
        raise credentials_exception
    
    try:
        token_data = jwt.verify_token(token_to_validate)
        if token_data is None:
            raise credentials_exception
        user_id = token_data.user_id
    except Exception:
        raise credentials_exception
        
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
        
    return user
