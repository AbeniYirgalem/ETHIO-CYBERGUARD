"""Security headers and per-IP rate limiting on credential endpoints."""

import pytest
from fastapi.testclient import TestClient

from apps.api import config
from apps.api.main import app
from apps.api.security_middleware import SlidingWindowLimiter, auth_limiter

client = TestClient(app)


# ---------- limiter unit tests (fake clock) ----------

def test_limiter_blocks_after_limit_and_recovers():
    now = [1000.0]
    limiter = SlidingWindowLimiter(limit=3, window=60, clock=lambda: now[0])

    assert [limiter.check("ip")[0] for _ in range(3)] == [True, True, True]
    allowed, retry_after = limiter.check("ip")
    assert allowed is False
    assert 1 <= retry_after <= 61

    now[0] += 61
    assert limiter.check("ip")[0] is True


def test_limiter_keeps_separate_buckets_per_key():
    limiter = SlidingWindowLimiter(limit=1, window=60)
    assert limiter.check("a")[0] is True
    assert limiter.check("a")[0] is False
    assert limiter.check("b")[0] is True


# ---------- security headers ----------

def test_security_headers_present():
    resp = client.get("/api/v1/health")
    assert resp.headers["x-content-type-options"] == "nosniff"
    assert resp.headers["x-frame-options"] == "DENY"
    assert resp.headers["referrer-policy"] == "no-referrer"
    assert "frame-ancestors 'none'" in resp.headers["content-security-policy"]


def test_auth_responses_are_not_cached():
    resp = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "x"})
    assert resp.headers["cache-control"] == "no-store"


def test_api_docs_are_not_blocked_by_csp():
    resp = client.get("/docs")
    assert resp.status_code == 200
    assert "content-security-policy" not in resp.headers


def test_hsts_only_when_enabled(monkeypatch):
    assert "strict-transport-security" not in client.get("/api/v1/health").headers
    monkeypatch.setattr(config, "ENABLE_HSTS", True)
    assert "max-age=" in client.get("/api/v1/health").headers["strict-transport-security"]


# ---------- rate limiting through the app ----------

@pytest.fixture
def limited(monkeypatch):
    monkeypatch.setattr(config, "AUTH_RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(auth_limiter, "limit", 3)
    auth_limiter.reset()
    yield
    auth_limiter.reset()


def _bad_login(email: str):
    return client.post("/api/auth/login", json={"email": email, "password": "wrong-password"})


def test_login_is_limited_per_ip_across_accounts(limited):
    # Different emails each time: the per-account lockout never triggers,
    # but the per-IP limit still stops the spraying.
    assert [_bad_login(f"spray{i}@example.com").status_code for i in range(3)] == [401, 401, 401]
    blocked = _bad_login("spray4@example.com")
    assert blocked.status_code == 429
    assert int(blocked.headers["retry-after"]) >= 1
    assert blocked.headers["x-content-type-options"] == "nosniff"


def test_only_credential_posts_are_limited(limited):
    for _ in range(6):
        assert client.get("/api/v1/health").status_code == 200
    assert _bad_login("one@example.com").status_code == 401


def test_limit_off_by_default_in_demo_mode():
    auth_limiter.reset()
    for i in range(15):
        assert _bad_login(f"demo{i}@example.com").status_code == 401


def test_forwarded_for_ignored_unless_proxy_trusted(limited):
    for i in range(3):
        resp = client.post(
            "/api/auth/login",
            json={"email": f"fwd{i}@example.com", "password": "x"},
            headers={"X-Forwarded-For": f"203.0.113.{i}"},
        )
        assert resp.status_code == 401
    # A forged header must not give the caller a fresh bucket.
    resp = client.post(
        "/api/auth/login",
        json={"email": "fwd9@example.com", "password": "x"},
        headers={"X-Forwarded-For": "198.51.100.77"},
    )
    assert resp.status_code == 429


def test_forwarded_for_used_when_proxy_trusted(limited, monkeypatch):
    monkeypatch.setattr(config, "TRUST_PROXY", True)
    for i in range(3):
        resp = client.post(
            "/api/auth/login",
            json={"email": f"p{i}@example.com", "password": "x"},
            headers={"X-Forwarded-For": "10.0.0.1, 203.0.113.5"},
        )
        assert resp.status_code == 401
    same_ip = client.post(
        "/api/auth/login",
        json={"email": "p9@example.com", "password": "x"},
        headers={"X-Forwarded-For": "10.0.0.2, 203.0.113.5"},
    )
    assert same_ip.status_code == 429
    other_ip = client.post(
        "/api/auth/login",
        json={"email": "p10@example.com", "password": "x"},
        headers={"X-Forwarded-For": "10.0.0.1, 203.0.113.6"},
    )
    assert other_ip.status_code == 401
