"""
API Dependencies
----------------
Common dependencies like authentication and database sessions.
"""

from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from core.storage.database import get_db
from core.auth import jwt
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False) 

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
    token_to_validate = token or access_token
    
    if not token_to_validate:
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
