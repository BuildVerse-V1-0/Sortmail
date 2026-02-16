"""
Auth Schemas
------------
Request/response models for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class TokenResponse(BaseModel):
    """OAuth token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User info response."""
    id: str
    email: EmailStr
    name: Optional[str] = None
    picture_url: Optional[str] = None
    provider: str


class LoginRequest(BaseModel):
    """OAuth callback request."""
    code: str
    state: Optional[str] = None
