"""Refresh-token rotation: single-use refresh tokens, reuse detection, session families."""

import uuid

from fastapi.testclient import TestClient

from apps.api import dependencies
from apps.api.dependencies import (
    REFRESH_USED_STORE, REVOKED_FAMILIES_STORE, consume_refresh_token,
    create_refresh_token, verify_token,
)
from apps.api.main import app

client = TestClient(app)
PASSWORD = "Rotation-Test-2026!"


def _create_user(admin_headers):
    email = f"rot.{uuid.uuid4().hex[:8]}@cbe.com.et"
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": PASSWORD, "full_name": "Rotation Tester", "role": "SECURITY_ANALYST"},
        headers=admin_headers,
    )
    assert resp.status_code == 201, resp.text
    return email


def _login(email):
    resp = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 200, resp.text
    return resp.json()


def _refresh(token):
    return client.post("/api/auth/refresh", json={"refresh_token": token})


def _bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_login_tokens_share_a_session_family(admin_headers):
    tokens = _login(_create_user(admin_headers))
    access = verify_token(tokens["access_token"])
    refresh = verify_token(tokens["refresh_token"], expected_type="refresh")
    assert access["fid"] and access["fid"] == refresh["fid"]


def test_each_login_gets_its_own_family(admin_headers):
    email = _create_user(admin_headers)
    first, second = _login(email), _login(email)
    assert verify_token(first["access_token"])["fid"] != verify_token(second["access_token"])["fid"]


def test_refresh_issues_new_pair_in_same_family(admin_headers):
    tokens = _login(_create_user(admin_headers))
    resp = _refresh(tokens["refresh_token"])
    assert resp.status_code == 200
    new = resp.json()
    assert new["refresh_token"] != tokens["refresh_token"]
    old_fid = verify_token(tokens["refresh_token"], expected_type="refresh")["fid"]
    assert verify_token(new["refresh_token"], expected_type="refresh")["fid"] == old_fid
    assert client.get("/api/auth/me", headers=_bearer(new["access_token"])).status_code == 200


def test_old_token_inside_grace_window_still_works(admin_headers, monkeypatch):
    monkeypatch.setattr(dependencies, "REFRESH_REUSE_GRACE_SECONDS", 10)
    # Two browser tabs refresh at the same moment: the second must not log the user out.
    tokens = _login(_create_user(admin_headers))
    assert _refresh(tokens["refresh_token"]).status_code == 200
    assert _refresh(tokens["refresh_token"]).status_code == 200


def test_reuse_after_grace_revokes_the_whole_session(admin_headers, monkeypatch):
    email = _create_user(admin_headers)
    victim, other_device = _login(email), _login(email)

    rotated = _refresh(victim["refresh_token"])
    assert rotated.status_code == 200
    newest = rotated.json()

    monkeypatch.setattr(dependencies, "REFRESH_REUSE_GRACE_SECONDS", -1)
    replay = _refresh(victim["refresh_token"])
    assert replay.status_code == 401
    assert "reuse" in replay.json()["detail"].lower()

    # The legitimate newest tokens of that session are dead as well ...
    assert _refresh(newest["refresh_token"]).status_code == 401
    assert client.get("/api/auth/me", headers=_bearer(newest["access_token"])).status_code == 401
    assert client.get("/api/auth/me", headers=_bearer(victim["access_token"])).status_code == 401
    # ... but a separate login of the same user is untouched.
    assert client.get("/api/auth/me", headers=_bearer(other_device["access_token"])).status_code == 200
    assert _refresh(other_device["refresh_token"]).status_code == 200


def test_logout_ends_the_whole_family(admin_headers):
    tokens = _login(_create_user(admin_headers))
    newest = _refresh(tokens["refresh_token"]).json()

    out = client.post("/api/auth/logout", headers=_bearer(newest["access_token"]))
    assert out.status_code == 200
    assert _refresh(newest["refresh_token"]).status_code == 401


def test_logout_keeps_counting_only_revoked_tokens(admin_headers):
    tokens = _login(_create_user(admin_headers))
    out = client.post(
        "/api/auth/logout",
        headers=_bearer(tokens["access_token"]),
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert out.json()["revoked_tokens"] == 2


def test_token_issued_before_rotation_existed_still_refreshes(admin_headers):
    email = _create_user(admin_headers)
    legacy = create_refresh_token({"sub": email, "tv": 0})  # no "fid" claim
    resp = _refresh(legacy)
    assert resp.status_code == 200
    assert verify_token(resp.json()["refresh_token"], expected_type="refresh")["fid"]


def test_consume_refresh_token_states():
    payload = {"jti": uuid.uuid4().hex, "fid": uuid.uuid4().hex, "exp": 4_102_444_800}  # year 2100
    assert consume_refresh_token(payload, now=1000.0) == "ok"
    assert consume_refresh_token(payload, now=1000.0 + dependencies.REFRESH_REUSE_GRACE_SECONDS) == "grace"
    assert consume_refresh_token(payload, now=1000.0 + dependencies.REFRESH_REUSE_GRACE_SECONDS + 5) == "reuse"
    assert any(e["fid"] == payload["fid"] for e in REVOKED_FAMILIES_STORE)


def test_rotation_state_is_kept_and_expired_entries_are_dropped():
    live = {"jti": uuid.uuid4().hex, "fid": "f-live", "exp": 4_102_444_800}
    consume_refresh_token(live)
    assert any(e["jti"] == live["jti"] for e in REFRESH_USED_STORE)

    REFRESH_USED_STORE.append({"jti": "old-one", "fid": "f-old", "used_at": 1.0, "exp": 2.0})
    REVOKED_FAMILIES_STORE.append({"fid": "f-old", "exp": 2.0})
    dependencies.after_state_restore()
    assert not any(e["jti"] == "old-one" for e in REFRESH_USED_STORE)
    assert not any(e["fid"] == "f-old" for e in REVOKED_FAMILIES_STORE)
    assert any(e["jti"] == live["jti"] for e in REFRESH_USED_STORE)
