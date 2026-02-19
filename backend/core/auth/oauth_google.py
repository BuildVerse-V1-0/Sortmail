"""
Google OAuth Integration
------------------------
Handles Google OAuth 2.0 flow for Gmail access.
"""

from typing import Optional
import httpx
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


import secrets
import hashlib
import base64

# ... imports ...

def generate_code_verifier() -> str:
    """Generate a random PKCE code verifier."""
    return secrets.token_urlsafe(64)

def generate_code_challenge(verifier: str) -> str:
    """Generate a SHA-256 code challenge from the verifier."""
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")

def get_google_auth_url(state: str, code_challenge: str) -> str:
    """Generate Google OAuth authorization URL with PKCE."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(GOOGLE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return f"{GOOGLE_AUTH_URL}?{query}"


async def exchange_code_for_tokens(code: str, code_verifier: str) -> GoogleTokens:
    """Exchange authorization code for tokens."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "code_verifier": code_verifier,
            },
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get tokens: {response.text}")
            
        data = response.json()
        return GoogleTokens(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            expires_in=data["expires_in"],
            token_type=data["token_type"],
        )


async def get_user_info(access_token: str) -> GoogleUserInfo:
    """Get user info from Google."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if response.status_code != 200:
            raise Exception(f"Failed to get user info: {response.text}")
            
        data = response.json()
        return GoogleUserInfo(
            id=data["id"],
            email=data["email"],
            name=data.get("name", ""),
            picture=data.get("picture"),
        )


async def refresh_access_token(refresh_token: str) -> GoogleTokens:
    """Refresh an expired access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        if response.status_code != 200:
            raise Exception(f"Failed to refresh token: {response.text}")
            
        data = response.json()
        return GoogleTokens(
            access_token=data["access_token"],
            # Google might not return a new refresh token, so we keep the old one if not provided
            refresh_token=data.get("refresh_token", refresh_token),
            expires_in=data["expires_in"],
            token_type=data["token_type"],
        )
