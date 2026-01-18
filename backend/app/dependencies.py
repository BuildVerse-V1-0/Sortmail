"""
Dependency Injection Setup
--------------------------
FastAPI dependencies for services

.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.storage import get_db
from api.middleware.auth import get_current_user, TokenData


# Type aliases for cleaner route signatures
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[TokenData, Depends(get_current_user)]
