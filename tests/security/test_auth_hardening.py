"""Authentication hardening: passwords, registration, password reset, routes, WebSocket."""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from apps.api import dependencies
from apps.api.config import validate_production_config
from apps.api.dependencies import DEMO_USERS, _build_user_directory
from apps.api.main import app
from apps.api.routers import auth as auth_router
from services.security.passwords import (
    hash_password, needs_rehash, validate_password_policy, verify_password,
)

client = TestClient(app)
STRONG = "k9Zr2vQ8xLm4Tn7Bw3Yc6Hd1Fs5Jp0Ae-unique"


# ---------------- password hashing ----------------

def test_hash_is_salted_and_verifies():
    first, second = hash_password("Correct-Horse-9!"), hash_password("Correct-Horse-9!")
    assert first != second  # random salt per hash
    assert verify_password("Correct-Horse-9!", first)
    assert not verify_password("Correct-Horse-8!", first)


def test_verify_never_raises_on_garbage():
    for bad in (None, "", "nonsense", "pbkdf2_sha256$x$y$z", "pbkdf2_sha256$99999999999$QQ$QQ", "a" * 64):
        assert verify_password("anything", bad) is False


def test_legacy_fixed_salt_hash_still_verifies_and_is_flagged():
    import hashlib
    legacy = hashlib.pbkdf2_hmac("sha256", b"Old-Password-1!", b"ecg_salt_2026_ethiopia", 100000).hex()
    assert verify_password("Old-Password-1!", legacy)
    assert needs_rehash(legacy)


def test_password_policy():
    assert validate_password_policy("Str0ng-Enough-Pass!") == []
    assert validate_password_policy("short1A!")
    assert validate_password_policy("alllowercaseletters")
    assert validate_password_policy("")
    assert validate_password_policy("a" * 200)


def test_demo_users_use_salted_hashes():
    for user in DEMO_USERS.values():
        assert user["password_hash"].startswith("pbkdf2_sha256$")


# ---------------- registration ----------------

def _register(headers=None, **overrides):
    body = {"email": "new.user@cbe.com.et", "password": "Valid-Password-2026!", "full_name": "New User",
            "role": "SECURITY_ANALYST"}
    body.update(overrides)
    return client.post("/api/auth/register", json=body, headers=headers)


def test_anonymous_cannot_register_an_administrator(monkeypatch):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    resp = _register(email="evil@x.com", role="SUPER_ADMIN")
    assert resp.status_code == 401
    assert "evil@x.com" not in DEMO_USERS


def test_guest_and_non_admins_cannot_register(commander_headers):
    assert _register(email="g@x.com").status_code == 403  # guest is a low-privilege analyst
    assert "g@x.com" not in DEMO_USERS
    assert _register(headers=commander_headers, email="c@x.com").status_code == 403
    assert "c@x.com" not in DEMO_USERS


def test_admin_can_register_with_validation(admin_headers):
    ok = _register(headers=admin_headers, email="created.by.admin@cbe.com.et")
    assert ok.status_code == 201
    body = ok.json()
    assert "access_token" not in body and "password_hash" not in str(body)
    assert DEMO_USERS["created.by.admin@cbe.com.et"]["password_hash"].startswith("pbkdf2_sha256$")

    assert _register(headers=admin_headers, email="weak@x.com", password="weak").status_code == 422
    assert _register(headers=admin_headers, email="role@x.com", role="GOD_MODE").status_code == 422
    assert _register(headers=admin_headers, email="not-an-email").status_code == 422
    assert _register(headers=admin_headers, email="created.by.admin@cbe.com.et").status_code == 400


def test_newly_created_user_can_log_in(admin_headers):
    assert _register(headers=admin_headers, email="login.check@cbe.com.et").status_code == 201
    resp = client.post("/api/auth/login", json={"email": "login.check@cbe.com.et", "password": "Valid-Password-2026!"})
    assert resp.status_code == 200
    assert resp.json()["user"]["role"] == "SECURITY_ANALYST"


# ---------------- password reset ----------------

def test_reset_never_returns_token_and_is_account_blind(monkeypatch):
    delivered = []
    monkeypatch.setattr(auth_router, "_deliver_reset_token", lambda e, t: delivered.append((e, t)))
    known = client.post("/api/auth/password-reset", json={"email": "readonly@cbe.com.et"})
    unknown = client.post("/api/auth/password-reset", json={"email": "nobody@nowhere.example"})
    assert known.status_code == unknown.status_code == 200
    assert known.json() == unknown.json()  # identical answers: no account discovery
    assert len(delivered) == 1 and delivered[0][0] == "readonly@cbe.com.et"
    assert delivered[0][1] not in known.text


def test_reset_token_is_single_use_policy_checked_and_not_stored_in_clear(monkeypatch):
    delivered = []
    monkeypatch.setattr(auth_router, "_deliver_reset_token", lambda e, t: delivered.append((e, t)))
    client.post("/api/auth/password-reset", json={"email": "hunter@cbe.com.et"})
    token = delivered[-1][1]
    assert token not in auth_router.PASSWORD_RESET_TOKENS  # only a digest is kept

    weak = client.post("/api/auth/password-reset/confirm", json={"reset_token": token, "new_password": "weak"})
    assert weak.status_code == 422

    done = client.post("/api/auth/password-reset/confirm", json={"reset_token": token, "new_password": "Hunter@2026!"})
    assert done.status_code == 200
    replay = client.post("/api/auth/password-reset/confirm", json={"reset_token": token, "new_password": "Hunter@2026!"})
    assert replay.status_code == 400


def test_reset_with_forged_token_fails():
    resp = client.post("/api/auth/password-reset/confirm",
                       json={"reset_token": "rst_forged", "new_password": "Whatever-Pass-2026!"})
    assert resp.status_code == 400


# ---------------- production mode ----------------

def test_demo_accounts_do_not_exist_in_production_directory():
    prod = _build_user_directory(False, "root@cbe.com.et", "Str0ng-Bootstrap-Pass!")
    assert list(prod) == ["root@cbe.com.et"] and prod["root@cbe.com.et"]["role"] == "SUPER_ADMIN"
    assert _build_user_directory(False, "", "") == {}
    assert "admin@cbe.com.et" in _build_user_directory(True, "", "")


def test_production_requires_a_strong_bootstrap_admin():
    base = dict(demo_mode=False, jwt_secret=STRONG, ingest_key=STRONG)
    with pytest.raises(RuntimeError):
        validate_production_config(**base, bootstrap_email="", bootstrap_password="")
    with pytest.raises(RuntimeError):
        validate_production_config(**base, bootstrap_email="root@cbe.com.et", bootstrap_password="weak")
    validate_production_config(**base, bootstrap_email="root@cbe.com.et", bootstrap_password="Str0ng-Bootstrap-Pass!")


def test_demo_credentials_endpoint_hidden_in_production(monkeypatch):
    assert client.get("/api/auth/demo-credentials").status_code == 200
    monkeypatch.setattr(auth_router, "DEMO_MODE", False)
    assert client.get("/api/auth/demo-credentials").status_code == 404


def test_login_rejects_unknown_user_and_wrong_password():
    for email, pw in (("ghost@cbe.com.et", "Anything-Goes-1!"), ("analyst@cbe.com.et", "wrong-password-1A!")):
        resp = client.post("/api/auth/login", json={"email": email, "password": pw})
        assert resp.status_code == 401


# ---------------- previously unguarded routes ----------------

def test_notify_pipeline_and_benchmark_require_login(monkeypatch, admin_headers, commander_headers):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    notify = {"incident_id": "INC-00042", "severity": "HIGH", "channel": "webhook"}
    assert client.post("/api/v1/alerts/notify", json=notify).status_code == 401
    assert client.post("/api/v1/pipeline/execute-slice", json={}).status_code == 401
    assert client.get("/api/v1/benchmark/run?events=100").status_code == 401

    assert client.post("/api/v1/alerts/notify", json=notify, headers=commander_headers).status_code == 200
    assert client.get("/api/v1/benchmark/run?events=100", headers=commander_headers).status_code == 403  # admin only
    assert client.get("/api/v1/benchmark/run?events=100", headers=admin_headers).status_code == 200


def test_notify_and_benchmark_validate_input(admin_headers):
    bad_channel = {"incident_id": "INC-1", "channel": "http://169.254.169.254/"}
    assert client.post("/api/v1/alerts/notify", json=bad_channel, headers=admin_headers).status_code == 422
    assert client.post("/api/v1/alerts/notify", json={"incident_id": "x", "risk_score": 500},
                       headers=admin_headers).status_code == 422
    assert client.get("/api/v1/benchmark/run?events=99999999", headers=admin_headers).status_code == 422


# ---------------- websocket ----------------

def test_websocket_rejects_bad_token_always():
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/live-events?token=not-a-real-token"):
            pass


def test_websocket_requires_token_in_production(monkeypatch):
    import apps.api.main as main_module
    monkeypatch.setattr(main_module, "DEMO_MODE", False)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/live-events"):
            pass


def test_websocket_accepts_valid_token(commander_headers):
    token = commander_headers["Authorization"].split(" ", 1)[1]
    with client.websocket_connect(f"/ws/live-events?token={token}") as ws:
        assert ws.receive_json()["type"] == "CONNECTION_ESTABLISHED"
