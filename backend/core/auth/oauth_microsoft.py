"""
Microsoft OAuth Integration
---------------------------
Handles Microsoft OAuth 2.0 flow for Outlook access.
"""

from typing import Optional
from pydantic import BaseModel

from app.config import settings


class MicrosoftTokens(BaseModel):
    """Tokens received from Microsoft OAuth."""
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: int
    token_type: str = "Bearer"


class MicrosoftUserInfo(BaseModel):
    """User info from Microsoft."""
    id: str
    email: str
    display_name: str


# OAuth configuration
MICROSOFT_AUTH_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
MICROSOFT_TOKEN_URL = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

# Scopes needed for Outlook access
MICROSOFT_SCOPES = [
    "openid",
    "email",
    "profile",
    "offline_access",
    "Mail.Read",
    "Mail.Send",
]


def get_microsoft_auth_url(state: str = "") -> str:
    """Generate Microsoft OAuth authorization URL."""
    params = {
        "client_id": settings.MICROSOFT_CLIENT_ID,
        "redirect_uri": settings.MICROSOFT_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(MICROSOFT_SCOPES),
        "state": state,
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{MICROSOFT_AUTH_URL}?{query}"


async def exchange_code_for_tokens(code: str) -> MicrosoftTokens:
    """Exchange authorization code for tokens."""
    # TODO: Implement actual token exchange using MSAL
    raise NotImplementedError("Implement Microsoft token exchange")


async def get_user_info(access_token: str) -> MicrosoftUserInfo:
    """Get user info from Microsoft Graph."""
    # TODO: Implement actual user info fetch
    raise NotImplementedError("Implement Microsoft user info fetch")


async def refresh_access_token(refresh_token: str) -> MicrosoftTokens:
    """Refresh an expired access token."""
    # TODO: Implement token refresh
    raise NotImplementedError("Implement Microsoft token refresh")
