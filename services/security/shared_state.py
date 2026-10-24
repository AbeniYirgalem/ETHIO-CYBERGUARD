"""Shared (cross-process) security state: rate-limit counters and token revocation flags.

Why: with more than one API worker, a logout or a refresh-token replay handled by worker A must
be seen by worker B at once, and the login rate limit must count attempts across all workers.
Redis is the shared place for that.

Backends (``SHARED_STATE_BACKEND``):
* ``auto`` (default): Redis when DEMO_MODE=false, ``REDIS_URL`` is set and the ``redis`` package
  is installed; otherwise in-process memory.
* ``redis``: always try Redis. ``memory``: never use Redis.

Safety rules:
* Redis trouble never takes the API down. A failing call is logged once and answered from the
  process-local fallback, so the API behaves exactly like a single worker until Redis returns.
* Only a few simple commands are used (INCR, EXPIRE, TTL, SET NX EX, GET, EXISTS), so the same code
  runs against Redis and against the in-memory client used in demo mode and tests.
* Rate limiting is a fixed window (atomic INCR). A client can briefly send up to twice the limit
  across a window boundary; that is acceptable for login throttling.
"""

import logging
import os
import threading
import time
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger("ecg.shared_state")

KEY_PREFIX = "ecg:"


class MemoryClient:
    """The tiny subset of the Redis API used here, kept in process memory with expiry."""

    def __init__(self, clock: Callable[[], float] = time.monotonic):
        self._clock = clock
        self._data: Dict[str, Tuple[str, Optional[float]]] = {}
        self._lock = threading.Lock()

    def _live(self, key: str) -> Optional[Tuple[str, Optional[float]]]:
        item = self._data.get(key)
        if item is None:
            return None
        if item[1] is not None and item[1] <= self._clock():
            del self._data[key]
            return None
        return item

    def incr(self, key: str) -> int:
        with self._lock:
            item = self._live(key)
            value = int(item[0]) + 1 if item else 1
            self._data[key] = (str(value), item[1] if item else None)
            return value

    def expire(self, key: str, seconds: int) -> bool:
        with self._lock:
            item = self._live(key)
            if item is None:
                return False
            self._data[key] = (item[0], self._clock() + seconds)
            return True

    def ttl(self, key: str) -> int:
        with self._lock:
            item = self._live(key)
            if item is None:
                return -2
            if item[1] is None:
                return -1
            return max(0, int(item[1] - self._clock() + 0.999))

    def set(self, key: str, value: Any, ex: Optional[int] = None, nx: bool = False) -> Optional[bool]:
        with self._lock:
            if nx and self._live(key) is not None:
                return None
            self._data[key] = (str(value), self._clock() + ex if ex else None)
            return True

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            item = self._live(key)
            return item[0] if item else None

    def exists(self, key: str) -> int:
        with self._lock:
            return 1 if self._live(key) is not None else 0


class SharedState:
    def __init__(self, client: Any, distributed: bool, fallback: Optional[MemoryClient] = None, name: str = "memory"):
        self.client = client
        self.distributed = distributed
        self.name = name
        self._fallback = fallback or MemoryClient()
        self._warned = False
        self._down_until = 0.0   # circuit breaker: skip the failing backend for a short while
        self._retry_after = 15.0

    # -- internal ----------------------------------------------------------------------------
    def _run(self, op: str, *args, **kwargs):
        if self.distributed and time.monotonic() < self._down_until:
            return getattr(self._fallback, op)(*args, **kwargs)
        try:
            return getattr(self.client, op)(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 - Redis problems must never crash a request
            if self.distributed:
                # Do not make every request wait for a timeout while Redis is down.
                self._down_until = time.monotonic() + self._retry_after
            if not self._warned:
                logger.warning("Shared state backend '%s' failed (%s); using process-local fallback.", self.name, exc)
                self._warned = True
            return getattr(self._fallback, op)(*args, **kwargs)

    # -- rate limiting -----------------------------------------------------------------------
    def rate_check(self, key: str, limit: int, window: int = 60) -> Tuple[bool, int]:
        """Count one attempt. Returns (allowed, retry_after_seconds)."""
        full = f"{KEY_PREFIX}rl:{key}"
        count = int(self._run("incr", full))
        if count == 1:
            self._run("expire", full, window)
        if count <= limit:
            return True, 0
        remaining = int(self._run("ttl", full))
        if remaining < 0:  # key lost its expiry (crash between INCR and EXPIRE): heal it
            self._run("expire", full, window)
            remaining = window
        return False, max(1, remaining)

    # -- flags (revoked token ids, revoked session families) ---------------------------------
    def set_flag(self, name: str, ttl_seconds: int) -> None:
        self._run("set", f"{KEY_PREFIX}flag:{name}", "1", ex=max(1, int(ttl_seconds)))

    def has_flag(self, name: str) -> bool:
        return bool(self._run("exists", f"{KEY_PREFIX}flag:{name}"))

    # -- one-time marks (used refresh tokens) ------------------------------------------------
    def set_once(self, name: str, value: str, ttl_seconds: int) -> bool:
        """Store value only if absent. True = this caller was first."""
        result = self._run("set", f"{KEY_PREFIX}once:{name}", value, ex=max(1, int(ttl_seconds)), nx=True)
        return bool(result)

    def get_once(self, name: str) -> Optional[str]:
        value = self._run("get", f"{KEY_PREFIX}once:{name}")
        if isinstance(value, bytes):
            value = value.decode("utf-8", "replace")
        return value


_state: Optional[SharedState] = None
_state_lock = threading.Lock()


def _build_state() -> SharedState:
    backend = os.getenv("SHARED_STATE_BACKEND", "auto").strip().lower()
    demo = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
    url = os.getenv("REDIS_URL", "")
    want_redis = backend == "redis" or (backend == "auto" and not demo and bool(url))
    if want_redis:
        try:
            import redis  # type: ignore

            client = redis.Redis.from_url(
                url or "redis://localhost:6379/0",
                decode_responses=True,
                socket_connect_timeout=1.5,
                socket_timeout=1.5,
            )
            try:
                client.ping()
                logger.info("Shared state: Redis")
            except Exception as exc:  # noqa: BLE001
                # Keep the Redis client anyway: each call falls back locally and recovers by itself
                # when Redis comes back, without restarting the API.
                logger.warning("Redis not reachable yet (%s); using process-local fallback until it is.", exc)
            return SharedState(client, distributed=True, name="redis")
        except ImportError:
            logger.warning("The 'redis' package is not installed; shared state is process-local.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis could not be configured (%s); shared state is process-local.", exc)
    return SharedState(MemoryClient(), distributed=False, name="memory")


def get_shared_state() -> SharedState:
    global _state
    if _state is None:
        with _state_lock:
            if _state is None:
                _state = _build_state()
    return _state


def set_shared_state(state: Optional[SharedState]) -> None:
    """Replace the shared state (tests, or None to rebuild from the environment)."""
    global _state
    with _state_lock:
        _state = state
