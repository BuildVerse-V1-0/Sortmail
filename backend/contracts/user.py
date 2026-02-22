"""
User DTO Contracts
------------------
API-facing DTOs for user data.
Normalizes the User model for frontend consumption.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class UserDTO(BaseModel):
    """
    User representation returned to the client.
    
    Maps/normalizes the SQLAlchemy User model:
    - picture_url → picture
    - status enum → is_active bool
    - Injects credits balance and plan from UserCredits table
    """
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None   # from User.picture_url
    provider: str
    is_active: bool                  # True if status == "active"
    is_superuser: bool
    credits: int = 0                 # from UserCredits.credits_balance
    plan: str = "free"               # from UserCredits.plan
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UpdateProfileRequest(BaseModel):
    """Request body for PATCH /api/users/me"""
    name: Optional[str] = None
    timezone: Optional[str] = None
    locale: Optional[str] = None
