"""
ETHIO-CYBERGUARD HTTP hardening middleware.

1. Security response headers on every response.
2. Per-IP sliding-window rate limit on credential endpoints (login, refresh,
   password reset). This stops password spraying across many accounts, which the
   per-account lockout in the login route cannot see.

Settings are read at request time from apps.api.config so tests can change them.
"""

import threading
import time
from collections import deque
from typing import Callable, Deque, Dict, Tuple

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from . import config

# Credential endpoints that get the per-IP limit (POST only).
_LIMITED_PATHS = frozenset(
    {
        "/api/auth/login",
        "/api/v1/auth/login",
        "/api/auth/refresh",
        "/api/v1/auth/refresh",
        "/api/auth/password-reset",
        "/api/v1/auth/password-reset",
        "/api/auth/password-reset/confirm",
        "/api/v1/auth/password-reset/confirm",
    }
)

# Swagger UI / ReDoc load scripts from a CDN, so a strict CSP would break them.
_DOC_PATHS = ("/docs", "/redoc")

_MAX_TRACKED_KEYS = 10_000


class SlidingWindowLimiter:
    """Allow at most `limit` events per `window` seconds for each key."""

    def __init__(self, limit: int, window: float = 60.0, clock: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.window = window
        self._clock = clock
        self._hits: Dict[str, Deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str) -> Tuple[bool, int]:
        """Record an attempt. Returns (allowed, retry_after_seconds)."""
        now = self._clock()
        cutoff = now - self.window
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.limit:
                retry_after = max(1, int(hits[0] + self.window - now) + 1)
                return False, retry_after
            hits.append(now)
            if len(self._hits) > _MAX_TRACKED_KEYS:
                self._prune(cutoff)
            return True, 0

    def _prune(self, cutoff: float) -> None:
        for key in [k for k, v in self._hits.items() if not v or v[-1] <= cutoff]:
            del self._hits[key]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


auth_limiter = SlidingWindowLimiter(limit=config.AUTH_RATE_LIMIT_PER_MINUTE)


def _limiter_enabled() -> bool:
    if config.AUTH_RATE_LIMIT_ENABLED is not None:
        return config.AUTH_RATE_LIMIT_ENABLED
    return not config.DEMO_MODE  # on by default in production, off in local demos


def _hsts_enabled() -> bool:
    if config.ENABLE_HSTS is not None:
        return config.ENABLE_HSTS
    return not config.DEMO_MODE


def client_ip(request: Request) -> str:
    """Client address. X-Forwarded-For is trusted only behind a known proxy
    (TRUST_PROXY=true), and then only its LAST entry, which the proxy appended;
    earlier entries can be forged by the client."""
    if config.TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for", "")
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if parts:
            return parts[-1]
    return request.client.host if request.client else "unknown"


def _apply_headers(request: Request, response) -> None:
    headers = response.headers
    headers.setdefault("X-Content-Type-Options", "nosniff")
    headers.setdefault("X-Frame-Options", "DENY")
    headers.setdefault("Referrer-Policy", "no-referrer")
    headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    path = request.url.path
    if not path.startswith(_DOC_PATHS):
        headers.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
    if path.startswith(("/api/auth/", "/api/v1/auth/")):
        headers["Cache-Control"] = "no-store"
    if _hsts_enabled():
        headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")


async def security_middleware(request: Request, call_next):
    if request.method == "POST" and request.url.path in _LIMITED_PATHS and _limiter_enabled():
        allowed, retry_after = auth_limiter.check(client_ip(request))
        if not allowed:
            blocked = JSONResponse(
                status_code=429,
                content={"detail": "Too many attempts. Please wait and try again."},
                headers={"Retry-After": str(retry_after)},
            )
            _apply_headers(request, blocked)
            return blocked
    response = await call_next(request)
    _apply_headers(request, response)
    return response


def install_security_middleware(app: FastAPI) -> None:
    app.middleware("http")(security_middleware)
