"""Security tests: dual-custody approvals, demo-only guest access, production config checks."""

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api import dependencies
from apps.api.config import validate_production_config

client = TestClient(app)

STRONG_SECRET = "k9Zr2vQ8xLm4Tn7Bw3Yc6Hd1Fs5Jp0Ae-unique"


def _request_live_isolation(headers, hostname):
    resp = client.post(
        "/api/response/isolate-host",
        json={"hostname": hostname, "reason": "Dual-custody test", "dry_run": False},
        headers=headers,
    )
    assert resp.status_code == 200
    return resp.json()["action_id"]


def test_requester_cannot_approve_own_action(commander_headers):
    action_id = _request_live_isolation(commander_headers, "SELF-APPROVE-01")
    resp = client.post(
        f"/api/response/actions/{action_id}/approve",
        json={"reason": "Approving my own request"},
        headers=commander_headers,
    )
    assert resp.status_code == 403
    assert "Dual-custody" in resp.json()["detail"]


def test_different_user_can_approve_action(responder_headers, commander_headers):
    action_id = _request_live_isolation(responder_headers, "TWO-PERSON-01")
    resp = client.post(
        f"/api/response/actions/{action_id}/approve",
        json={"reason": "Second pair of eyes confirmed"},
        headers=commander_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["action"]["status"] == "APPROVED"


def test_responder_cannot_approve_actions(responder_headers, admin_headers):
    action_id = _request_live_isolation(admin_headers, "ROLE-CHECK-01")
    resp = client.post(
        f"/api/response/actions/{action_id}/approve",
        json={"reason": "Responders must not approve"},
        headers=responder_headers,
    )
    assert resp.status_code == 403


def test_guest_access_allowed_in_demo_mode(monkeypatch):
    monkeypatch.setattr(dependencies, "DEMO_MODE", True)
    resp = client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["user"]["role"] == "SECURITY_ANALYST"


def test_guest_access_blocked_in_production_mode(monkeypatch):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_production_mode_still_accepts_real_login(monkeypatch, commander_headers):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    resp = client.get("/api/auth/me", headers=commander_headers)
    assert resp.status_code == 200


def test_production_rejects_default_secrets():
    with pytest.raises(RuntimeError):
        validate_production_config(
            demo_mode=False,
            jwt_secret="ethio-cyberguard-production-hmac-sha256-key-9281923",
            ingest_key=STRONG_SECRET,
        )
    with pytest.raises(RuntimeError):
        validate_production_config(demo_mode=False, jwt_secret="short", ingest_key=STRONG_SECRET)
    with pytest.raises(RuntimeError):
        validate_production_config(demo_mode=False, jwt_secret=STRONG_SECRET, ingest_key="ecg-collector-secure-api-key-2026")


def test_production_accepts_strong_secrets_and_demo_skips_checks():
    validate_production_config(
        demo_mode=False, jwt_secret=STRONG_SECRET, ingest_key=STRONG_SECRET,
        bootstrap_email="root@cbe.com.et", bootstrap_password="Str0ng-Bootstrap-Pass!",
    )
    validate_production_config(demo_mode=True, jwt_secret="weak", ingest_key="weak")
