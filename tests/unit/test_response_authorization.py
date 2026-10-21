"""Authorization tests for SOAR response endpoints."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.dependencies import get_current_user
from apps.api.routers.response import router


def make_client(role: str) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: {
        "id": "test-user",
        "email": "test@example.com",
        "name": "Test User",
        "role": role,
    }
    return TestClient(app)


def test_analyst_cannot_request_host_isolation():
    client = make_client("SECURITY_ANALYST")
    response = client.post(
        "/api/response/isolate-host",
        json={"hostname": "host-01", "reason": "test", "dry_run": True},
    )
    assert response.status_code == 403


def test_responder_can_request_host_isolation_in_dry_run():
    client = make_client("INCIDENT_RESPONDER")
    response = client.post(
        "/api/response/isolate-host",
        json={"hostname": "host-01", "reason": "test", "dry_run": True},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "SIMULATED"


def test_analyst_cannot_disable_account():
    client = make_client("SECURITY_ANALYST")
    response = client.post(
        "/api/response/disable-account",
        json={"username": "testuser", "reason": "test", "dry_run": True},
    )
    assert response.status_code == 403


def test_read_only_user_can_read_audit_log_but_cannot_approve_actions():
    client = make_client("READ_ONLY")
    audit_response = client.get("/api/response/audit-log")
    approve_response = client.post(
        "/api/response/actions/ACT-001/approve",
        json={"reason": "test approval"},
    )
    assert audit_response.status_code == 200
    assert approve_response.status_code == 403


def test_analyst_cannot_approve_actions():
    client = make_client("SECURITY_ANALYST")
    response = client.post(
        "/api/response/actions/ACT-001/approve",
        json={"reason": "test approval"},
    )
    assert response.status_code == 403
