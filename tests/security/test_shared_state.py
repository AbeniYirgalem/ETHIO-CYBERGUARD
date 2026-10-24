"""Shared (multi-worker) security state: rate limits, revocation flags, refresh-token marks.

Two "workers" are simulated by giving two SharedState objects the same client, which is exactly
how two API processes share one Redis. No real Redis is needed.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from apps.api import config, dependencies
from apps.api.main import app
from apps.api.security_middleware import auth_limiter
from services.security.shared_state import MemoryClient, SharedState, get_shared_state, set_shared_state


@pytest.fixture(autouse=True)
def _reset_shared_state():
    yield
    set_shared_state(None)


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def _two_workers():
    clock = Clock()
    redis_like = MemoryClient(clock)
    return SharedState(redis_like, distributed=True, name="fake"), SharedState(redis_like, distributed=True, name="fake"), clock


# ---------- the primitives ----------

def test_rate_limit_counts_across_workers_and_recovers():
    a, b, clock = _two_workers()
    assert a.rate_check("ip", 3, 60) == (True, 0)
    assert b.rate_check("ip", 3, 60) == (True, 0)
    assert a.rate_check("ip", 3, 60) == (True, 0)
    allowed, retry_after = b.rate_check("ip", 3, 60)   # the 4th attempt lands on the other worker
    assert allowed is False and 1 <= retry_after <= 60
    clock.now += 61
    assert a.rate_check("ip", 3, 60)[0] is True


def test_rate_limit_keeps_keys_separate():
    a, _b, _ = _two_workers()
    assert a.rate_check("one", 1, 60)[0] is True
    assert a.rate_check("two", 1, 60)[0] is True
    assert a.rate_check("one", 1, 60)[0] is False


def test_flags_are_shared_and_expire():
    a, b, clock = _two_workers()
    assert b.has_flag("jti:abc") is False
    a.set_flag("jti:abc", 30)
    assert b.has_flag("jti:abc") is True
    clock.now += 31
    assert b.has_flag("jti:abc") is False


def test_set_once_has_exactly_one_winner():
    a, b, _ = _two_workers()
    assert a.set_once("used:x", "100.0", 60) is True
    assert b.set_once("used:x", "200.0", 60) is False
    assert b.get_once("used:x") == "100.0"


class _BrokenClient:
    calls = 0

    def __getattr__(self, name):
        def fail(*args, **kwargs):
            _BrokenClient.calls += 1
            raise ConnectionError("redis is down")
        return fail


def test_redis_outage_falls_back_locally_and_stops_retrying_for_a_while():
    _BrokenClient.calls = 0
    state = SharedState(_BrokenClient(), distributed=True, name="broken")
    assert state.rate_check("ip", 2, 60)[0] is True      # still answers, from the local fallback
    assert state.rate_check("ip", 2, 60)[0] is True
    assert state.rate_check("ip", 2, 60)[0] is False     # the local limit still works
    first = _BrokenClient.calls
    state.set_flag("jti:z", 30)
    assert state.has_flag("jti:z") is True
    assert _BrokenClient.calls == first                   # circuit open: no more slow calls


def test_demo_mode_uses_memory_not_redis(monkeypatch):
    monkeypatch.setenv("SHARED_STATE_BACKEND", "auto")
    monkeypatch.setenv("DEMO_MODE", "true")
    set_shared_state(None)
    assert get_shared_state().distributed is False


def test_memory_backend_can_be_forced(monkeypatch):
    monkeypatch.setenv("SHARED_STATE_BACKEND", "memory")
    monkeypatch.setenv("DEMO_MODE", "false")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    set_shared_state(None)
    assert get_shared_state().distributed is False


# ---------- the login rate limit through the real app ----------

def test_login_limit_is_shared_between_workers(monkeypatch):
    client = TestClient(app)
    a, b, _ = _two_workers()
    monkeypatch.setattr(config, "AUTH_RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(config, "AUTH_RATE_LIMIT_PER_MINUTE", 2)
    auth_limiter.reset()

    def attempt():
        return client.post("/api/auth/login", json={"email": f"s{uuid.uuid4().hex[:6]}@example.com", "password": "x"})

    set_shared_state(a)
    assert attempt().status_code == 401
    set_shared_state(b)                      # the next request is served by the other worker
    assert attempt().status_code == 401
    blocked = attempt()
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) >= 1


# ---------- revocation and refresh rotation across workers ----------

def _forget_local_revocations():
    """Make this process look like a different worker that never saw the revocation."""
    dependencies.REVOKED_TOKENS_STORE.clear()
    dependencies.REVOKED_FAMILIES_STORE.clear()
    dependencies.REFRESH_USED_STORE.clear()
    dependencies._prune_revoked()
    dependencies._prune_rotation()


def test_logout_on_one_worker_is_enforced_on_another():
    a, b, _ = _two_workers()
    set_shared_state(a)
    token = dependencies.create_access_token({"sub": "who@example.com", "fid": "fam-1"})
    payload = dependencies.verify_token(token)
    assert dependencies.revoke_token_payload(payload) is True

    _forget_local_revocations()
    set_shared_state(b)
    assert dependencies.is_token_revoked(payload) is True
    with pytest.raises(Exception) as err:
        dependencies.verify_token(token)
    assert "revoked" in str(getattr(err.value, "detail", err.value)).lower()


def test_revoked_family_is_enforced_on_another_worker():
    a, b, _ = _two_workers()
    set_shared_state(a)
    token = dependencies.create_access_token({"sub": "who@example.com", "fid": uuid.uuid4().hex})
    payload = dependencies.verify_token(token)
    assert dependencies.revoke_family(payload) is True

    _forget_local_revocations()
    set_shared_state(b)
    assert dependencies.is_family_revoked(payload) is True


def test_refresh_token_replayed_on_another_worker_is_detected():
    a, b, _ = _two_workers()
    payload = {"jti": uuid.uuid4().hex, "fid": uuid.uuid4().hex, "exp": 4_102_444_800}

    set_shared_state(a)
    assert dependencies.consume_refresh_token(payload, now=5000.0) == "ok"

    _forget_local_revocations()               # worker B has no local memory of the first use
    set_shared_state(b)
    grace = dependencies.REFRESH_REUSE_GRACE_SECONDS
    assert dependencies.consume_refresh_token(payload, now=5000.0 + grace) == "grace"
    assert dependencies.consume_refresh_token(payload, now=5000.0 + grace + 30) == "reuse"
    assert dependencies.is_family_revoked(payload) is True


def test_saved_revocations_are_republished_to_a_fresh_redis():
    a, b, _ = _two_workers()
    set_shared_state(a)
    token = dependencies.create_access_token({"sub": "who@example.com"})
    payload = dependencies.verify_token(token)
    dependencies.revoke_token_payload(payload)

    fresh_redis = SharedState(MemoryClient(), distributed=True, name="fresh")   # Redis was flushed
    set_shared_state(fresh_redis)
    dependencies._sync_revocations_to_shared()
    _forget_local_revocations()
    assert fresh_redis.has_flag(f"jti:{payload['jti']}") is True
