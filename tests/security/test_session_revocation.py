"""Logout, token revocation, session invalidation on password reset, and durable users."""

import uuid

from fastapi.testclient import TestClient

from apps.api import dependencies
from apps.api.dependencies import (
    DEMO_USERS, REVOKED_TOKENS_STORE, USERS_STORE, after_state_restore,
    create_access_token, is_token_revoked, restore_users, verify_token,
)
from apps.api.main import app
from apps.api.routers import auth as auth_router
from database import state_store

client = TestClient(app)
PASSWORD = "Session-Test-2026!"


def _create_user(admin_headers, role="SECURITY_ANALYST"):
    email = f"sess.{uuid.uuid4().hex[:8]}@cbe.com.et"
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Session Tester", "role": role},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    return email


def _login(email, password=PASSWORD):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_tokens_carry_unique_ids():
    first = create_access_token({"sub": "a@x.com"})
    second = create_access_token({"sub": "a@x.com"})
    assert verify_token(first)["jti"] != verify_token(second)["jti"]


def test_logout_revokes_access_token(admin_headers):
    tokens = _login(_create_user(admin_headers))
    assert client.get("/api/auth/me", headers=_bearer(tokens["access_token"])).status_code == 200

    out = client.post("/api/auth/logout", headers=_bearer(tokens["access_token"]))
    assert out.status_code == 200 and out.json()["revoked_tokens"] == 1

    after = client.get("/api/auth/me", headers=_bearer(tokens["access_token"]))
    assert after.status_code == 401
    assert "revoked" in after.json()["detail"].lower()


def test_logout_revokes_refresh_token_too(admin_headers):
    tokens = _login(_create_user(admin_headers))
    out = client.post(
        "/api/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
        headers=_bearer(tokens["access_token"]),
    )
    assert out.json()["revoked_tokens"] == 2
    refresh = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refresh.status_code == 401


def test_logout_is_idempotent_and_never_fails():
    assert client.post("/api/auth/logout").status_code == 200
    assert client.post("/api/auth/logout", headers=_bearer("garbage.token.value")).status_code == 200
    assert client.post("/api/auth/logout", json={"refresh_token": "nope"}).status_code == 200


def test_revoked_token_cannot_be_used_twice_in_logout(admin_headers):
    tokens = _login(_create_user(admin_headers))
    first = client.post("/api/auth/logout", headers=_bearer(tokens["access_token"]))
    second = client.post("/api/auth/logout", headers=_bearer(tokens["access_token"]))
    assert first.json()["revoked_tokens"] == 1
    assert second.status_code == 200 and second.json()["revoked_tokens"] == 0


def test_password_reset_retires_existing_sessions(admin_headers, monkeypatch):
    delivered = []
    monkeypatch.setattr(auth_router, "_deliver_reset_token", lambda e, t: delivered.append((e, t)))
    email = _create_user(admin_headers)
    old = _login(email)
    assert client.get("/api/auth/me", headers=_bearer(old["access_token"])).status_code == 200

    client.post("/api/auth/password-reset", json={"email": email})
    done = client.post(
        "/api/auth/password-reset/confirm",
        json={"reset_token": delivered[-1][1], "new_password": "Brand-New-Pass-2027!"},
    )
    assert done.status_code == 200

    assert client.get("/api/auth/me", headers=_bearer(old["access_token"])).status_code == 401
    assert client.post("/api/auth/refresh", json={"refresh_token": old["refresh_token"]}).status_code == 401

    fresh = _login(email, "Brand-New-Pass-2027!")
    assert client.get("/api/auth/me", headers=_bearer(fresh["access_token"])).status_code == 200


def test_revocation_survives_restart(admin_headers):
    tokens = _login(_create_user(admin_headers))
    jti = verify_token(tokens["access_token"])["jti"]
    client.post("/api/auth/logout", headers=_bearer(tokens["access_token"]))

    REVOKED_TOKENS_STORE.clear()
    dependencies._revoked_jtis.clear()
    assert not is_token_revoked({"jti": jti})

    state_store.restore_all()
    after_state_restore()
    assert is_token_revoked({"jti": jti})
    assert client.get("/api/auth/me", headers=_bearer(tokens["access_token"])).status_code == 401


def test_created_user_survives_restart_and_can_log_in(admin_headers):
    email = _create_user(admin_headers, role="AUDITOR")
    DEMO_USERS.pop(email)
    USERS_STORE.clear()

    state_store.restore_all()
    after_state_restore()

    assert email in DEMO_USERS and DEMO_USERS[email]["role"] == "AUDITOR"
    assert _login(email)["user"]["role"] == "AUDITOR"


def test_password_change_survives_restart(admin_headers, monkeypatch):
    delivered = []
    monkeypatch.setattr(auth_router, "_deliver_reset_token", lambda e, t: delivered.append((e, t)))
    email = _create_user(admin_headers)
    client.post("/api/auth/password-reset", json={"email": email})
    client.post("/api/auth/password-reset/confirm",
                json={"reset_token": delivered[-1][1], "new_password": "Persisted-Pass-2028!"})

    DEMO_USERS.pop(email)
    USERS_STORE.clear()
    state_store.restore_all()
    after_state_restore()

    assert client.post("/api/auth/login", json={"email": email, "password": PASSWORD}).status_code == 401
    assert _login(email, "Persisted-Pass-2028!")["user"]["email"] == email
    # token_version survived too, so a pre-reset token is still dead after the restart
    assert DEMO_USERS[email]["token_version"] == 1


def test_default_accounts_are_never_resurrected_in_production():
    saved = list(USERS_STORE)
    try:
        USERS_STORE[:] = [
            {"id": "usr_cbe_admin_01", "email": "admin@cbe.com.et", "role": "SUPER_ADMIN", "password_hash": "x$y"},
            {"id": "usr_bootstrap_admin", "email": "root@cbe.com.et", "role": "SUPER_ADMIN", "password_hash": "x$y"},
            {"id": "usr_real_001", "email": "real@cbe.com.et", "role": "AUDITOR", "password_hash": "x$y"},
        ]
        production_directory = {}
        assert restore_users(production_directory, demo_mode=False) == 1
        assert list(production_directory) == ["real@cbe.com.et"]

        demo_directory = {}
        assert restore_users(demo_directory, demo_mode=True) == 2  # bootstrap admin still excluded
        assert "root@cbe.com.et" not in demo_directory
    finally:
        USERS_STORE[:] = saved


def test_unknown_subject_is_rejected_in_production(monkeypatch):
    token = create_access_token({"sub": "ghost@nowhere.example", "role": "SUPER_ADMIN"})
    assert client.get("/api/auth/me", headers=_bearer(token)).status_code == 200  # demo sandbox fallback
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    assert client.get("/api/auth/me", headers=_bearer(token)).status_code == 401
