"""
Rate Limiting Middleware
------------------------
Simple rate limiting for API protection.
"""

from typing import Optional
from fastapi import Request, HTTPException
from datetime import datetime, timezone
import asyncio


# Simple in-memory rate limiter (use Redis in production)
_request_counts: dict = {}


async def rate_limit_middleware(request: Request, calls_per_minute: int = 60):
    """
    Simple rate limiting.
    
    In production, use Redis-based rate limiting.
    """
    client_ip = request.client.host
    current_minute = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H-%M")
    key = f"{client_ip}:{current_minute}"
    
    # Increment counter
    _request_counts[key] = _request_counts.get(key, 0) + 1
    
    if _request_counts[key] > calls_per_minute:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later.",
        )
    
    # Clean old entries (basic cleanup)
    keys_to_remove = [
        k for k in _request_counts.keys()
        if k.split(":")[1] != current_minute
    ]
    for k in keys_to_remove:
        del _request_counts[k]
