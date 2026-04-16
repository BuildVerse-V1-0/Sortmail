"""
Security Middleware
-------------------
Implements critical security controls:
1. Rate Limiting (Redis-backed window)
2. Security Headers (HSTS, CSP, etc.)
3. Request ID (Traceability)
"""

import uuid
import logging
import os
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from core.redis import get_redis
from app.config import settings

logger = logging.getLogger("security")


class OriginServiceGateMiddleware(BaseHTTPMiddleware):
    """
    Blocks unknown cross-origin API calls and non-browser API calls without
    a trusted internal service token.
    """

    def __init__(self, app):
        super().__init__(app)
        self.allowed_origins = set(settings.CORS_ORIGINS or [])
        self.allow_exact_no_origin = {
            "/",
            "/health",
            "/health/simple",
        }
        self.allow_prefixes_no_origin = (
            "/api/webhooks/",
            "/api/events/",
            "/api/auth/google",
            "/api/auth/outlook",
            "/api/auth/google/callback",
            "/api/auth/outlook/callback",
            "/api/auth/microsoft/callback",
        )
        self.vercel_regex = r"https://sortmail.*\.vercel\.app"

    def _origin_allowed(self, origin: str) -> bool:
        if origin in self.allowed_origins:
            return True
        try:
            import re
            return bool(re.fullmatch(self.vercel_regex, origin))
        except Exception:
            return False

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        method = request.method.upper()

        if method == "OPTIONS" or not path.startswith("/api"):
            return await call_next(request)

        origin = request.headers.get("origin")
        if origin:
            if not self._origin_allowed(origin):
                return Response("Forbidden origin", status_code=403)
            return await call_next(request)

        if path in self.allow_exact_no_origin or any(path.startswith(p) for p in self.allow_prefixes_no_origin):
            return await call_next(request)

        token = settings.INTERNAL_SERVICE_TOKEN
        provided = request.headers.get("X-Internal-Service-Token", "")

        if settings.ENVIRONMENT.lower() == "production":
            if not token or provided != token:
                return Response("Forbidden", status_code=403)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # HSTS (1 year)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        
        # No Sniff
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Frame Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # CSP (Basic default, tighten as needed)
        # response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; connect-src 'self'"
        # Commented out CSP for now to avoid breaking existing dev flow, UNCOMMENT FOR PROD.
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple sliding window rate limiter using Redis.
    Limit: 100 requests / minute per IP.
    """
    RATE_LIMIT = 100
    WINDOW = 60

    def __init__(self, app):
        super().__init__(app)
        self.rate_limit_all_api = os.getenv("RATE_LIMIT_ALL_API", "false").strip().lower() in {"1", "true", "yes", "on"}
        self.protected_prefixes = (
            "/api/auth",
            "/api/webhooks",
            "/api/proxy",
        )
        self.redis_error_cooldown_seconds = float(os.getenv("RATE_LIMIT_REDIS_COOLDOWN_SECONDS", "5"))
        self._redis_unavailable_until = 0.0
        self._last_redis_warning_at = 0.0
        self.redis_warning_interval_seconds = float(os.getenv("RATE_LIMIT_REDIS_WARNING_INTERVAL_SECONDS", "15"))
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for static/health inputs if needed
        path = request.url.path
        if path in {"/health", "/health/simple"} or request.method == "OPTIONS":
            return await call_next(request)

        # Cost-control mode: only protect high-risk public endpoints with Redis-backed limiting.
        if not self.rate_limit_all_api and not any(path.startswith(prefix) for prefix in self.protected_prefixes):
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"rate_limit:{client_ip}"

        now = time.monotonic()
        if now < self._redis_unavailable_until:
            return await call_next(request)
        
        try:
            redis_client = await get_redis()
            # Set TTL only when key is first seen to avoid an extra EXPIRE on every request.
            count = await redis_client.incr(key)
            if count == 1:
                await redis_client.expire(key, self.WINDOW)
            
            if count > self.RATE_LIMIT:
                return Response(
                    "Rate limit exceeded", 
                    status_code=429,
                    headers={"Retry-After": str(self.WINDOW)}
                )
                
        except Exception as e:
            # Fail Open for Redis connection issues
            self._redis_unavailable_until = time.monotonic() + self.redis_error_cooldown_seconds
            if time.monotonic() - self._last_redis_warning_at >= self.redis_warning_interval_seconds:
                logger.warning(f"Rate Limit Redis Error: {e}")
                self._last_redis_warning_at = time.monotonic()
            pass
            
        # Call the actual route OUTSIDE the try-except so exceptions bubble up!
        response = await call_next(request)
        
        # Add Rate Limit Headers if we have the count
        if 'count' in locals():
            response.headers["X-RateLimit-Limit"] = str(self.RATE_LIMIT)
            response.headers["X-RateLimit-Remaining"] = str(max(0, self.RATE_LIMIT - count))
            
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class SanitizedAccessLogMiddleware(BaseHTTPMiddleware):
    """
    Middleware to suppress verbose access logging of sensitive headers.
    Prevents sensitive data from appearing in Railway logs.
    """
    
    # Headers that should never be logged
    SENSITIVE_HEADERS = {
        'authorization',
        'cookie',
        'x-api-key',
        'x-internal-service-token',
        'x-auth-token',
        'x-access-token',
        'x-csrf-token',
    }
    
    async def dispatch(self, request: Request, call_next):
        # Log request info (but not sensitive headers)
        # Skip logging for health checks
        if request.url.path not in {"/health", "/health/simple"}:
            # Create a sanitized headers dict for logging
            safe_headers = {
                k: "***REDACTED***" 
                for k in request.headers 
                if k.lower() in self.SENSITIVE_HEADERS
            }
            if safe_headers and settings.DEBUG:
                logger.debug(f"Request sanitized headers: {safe_headers}")
        
        response = await call_next(request)
        return response
