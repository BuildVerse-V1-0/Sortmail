"""
Google OAuth Integration
------------------------
Handles Google OAuth 2.0 flow for Gmail access.
"""

from typing import Optional
from pydantic import BaseModel

from app.config import settings


class GoogleTokens(BaseModel):
    """Tokens received from Google OAuth."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int
    token_type: str = "Bearer"


class GoogleUserInfo(BaseModel):
    """User info from Google."""
    id: str
    email: str
    name: str
    picture: Optional[str] = None


# OAuth configuration
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# Scopes needed for Gmail access
GOOGLE_SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


def get_google_auth_url(state: str = "") -> str:
    """Generate Google OAuth authorization URL."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def exchange_code_for_tokens(code: str) -> GoogleTokens:
    """Exchange authorization code for tokens."""
    # TODO: Implement actual token exchange
    # Use httpx to POST to GOOGLE_TOKEN_URL
    raise NotImplementedError("Implement Google token exchange")


async def get_user_info(access_token: str) -> GoogleUserInfo:
    """Get user info from Google."""
    # TODO: Implement actual user info fetch
    raise NotImplementedError("Implement Google user info fetch")


async def refresh_access_token(refresh_token: str) -> GoogleTokens:
    """Refresh an expired access token."""
    # TODO: Implement token refresh
    raise NotImplementedError("Implement Google token refresh")
