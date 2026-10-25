"""
Test Suite for ETHIO-CYBERGUARD Production Enhancements
Verifies Health & Prometheus metrics, Connectors, Background Jobs,
Authentication lockout & refresh, Incident Lifecycle, and Safe SOAR response.
"""

import pytest
pytest.importorskip("httpx")

from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_system_mode_and_demo_banner():
    resp = client.get("/api/system/mode")
    assert resp.status_code == 200
    data = resp.json()
    assert "demo_mode" in data
    assert "banner" in data

def test_health_live_and_ready():
    # Liveness probe
    live_resp = client.get("/health/live")
    assert live_resp.status_code == 200
    assert live_resp.json()["status"] == "UP"

    # Readiness probe
    ready_resp = client.get("/health/ready")
    assert ready_resp.status_code == 200
    ready_data = ready_resp.json()
    assert ready_data["status"] == "READY"
    assert "database" in ready_data["checks"]
    assert "connectors" in ready_data["checks"]

def test_prometheus_metrics():
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "ecg_uptime_seconds" in resp.text
    assert "ecg_detection_rules_loaded 148" in resp.text
    assert "ecg_events_per_second_capacity" in resp.text

def test_connectors_list_and_test():
    # List connectors
    list_resp = client.get("/api/connectors")
    assert list_resp.status_code == 200
    connectors = list_resp.json()["connectors"]
    assert len(connectors) >= 4

    # Test individual connector health
    test_resp = client.post("/api/connectors/conn-fw-01/test")
    assert test_resp.status_code == 200
    assert test_resp.json()["status"] == "SUCCESS"

def test_background_jobs_workflow():
    # Enqueue a background task
    create_resp = client.post("/api/v1/jobs", json={
        "job_type": "report_generation",
        "payload": {"format": "pdf"}
    })
    assert create_resp.status_code == 202
    job_id = create_resp.json()["job_id"]
    assert job_id.startswith("job-")

    # Fetch status
    status_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert status_resp.status_code == 200
    assert status_resp.json()["job_id"] == job_id

def test_auth_refresh_and_reset(monkeypatch):
    from apps.api.routers import auth as auth_router

    delivered = []
    monkeypatch.setattr(auth_router, "_deliver_reset_token", lambda email, token: delivered.append((email, token)))

    def request_token():
        resp = client.post("/api/auth/password-reset", json={"email": "analyst@cbe.com.et"})
        assert resp.status_code == 200
        assert "reset_token_simulated" not in resp.json()  # never returned to the caller
        return delivered[-1][1]

    # Login to get refresh token
    login_resp = client.post("/api/auth/login", json={
        "email": "analyst@cbe.com.et",
        "password": "Analyst@2026!"
    })
    tokens = login_resp.json()
    assert "refresh_token" in tokens

    # Refresh
    refresh_resp = client.post("/api/auth/refresh", json={
        "refresh_token": tokens["refresh_token"]
    })
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.json()

    # Password reset request + confirm (token captured from the out-of-band channel)
    confirm_resp = client.post("/api/auth/password-reset/confirm", json={
        "reset_token": request_token(),
        "new_password": "NewSecurePassword@2026!"
    })
    assert confirm_resp.status_code == 200

    # Reset back to original password for other tests
    client.post("/api/auth/password-reset/confirm", json={
        "reset_token": request_token(),
        "new_password": "Analyst@2026!"
    })

def test_account_lockout_after_failures():
    # Attempt 5 invalid logins
    for _ in range(5):
        client.post("/api/auth/login", json={
            "email": "lockout_test@cbe.com.et",
            "password": "WrongPassword123!"
        })
    # 6th attempt should be locked
    locked_resp = client.post("/api/auth/login", json={
        "email": "lockout_test@cbe.com.et",
        "password": "WrongPassword123!"
    })
    assert locked_resp.status_code == 423
    assert "Account locked" in locked_resp.json()["detail"]

def test_incident_lifecycle_and_timeline():
    # Transition status
    trans_resp = client.post("/api/incidents/INC-00042/transition", json={
        "new_status": "CONTAINED",
        "reason": "Host quarantined via EDR channel"
    })
    assert trans_resp.status_code == 200
    assert trans_resp.json()["new_status"] == "CONTAINED"

    # Add comment
    comment_resp = client.post("/api/incidents/INC-00042/comments", json={
        "content": "Containment verified across enterprise perimeter."
    })
    assert comment_resp.status_code == 201

    # Add task
    task_resp = client.post("/api/incidents/INC-00042/tasks", json={
        "title": "Complete post-incident analysis"
    })
    assert task_resp.status_code == 201

    # Fetch timeline
    timeline_resp = client.get("/api/incidents/INC-00042/timeline")
    assert timeline_resp.status_code == 200
    timeline = timeline_resp.json()
    assert len(timeline["history"]) >= 1
    assert len(timeline["comments"]) >= 1

def test_safe_soar_dry_run_and_rollback(responder_headers, commander_headers):
    # Dry-run action
    dry_resp = client.post("/api/response/isolate-host", json={
        "hostname": "SERVER-TEST-09",
        "reason": "Simulated containment test",
        "dry_run": True
    }, headers=commander_headers)
    assert dry_resp.status_code == 200
    assert dry_resp.json()["dry_run"] is True
    assert dry_resp.json()["status"] == "SIMULATED"
    dry_action_id = dry_resp.json()["action_id"]

    # Dry-run (simulated) actions can never be approved
    dry_appr = client.post(f"/api/response/actions/{dry_action_id}/approve", json={
        "reason": "Should be refused"
    }, headers=commander_headers)
    assert dry_appr.status_code == 409

    # Live action: queued for approval, then approved
    live_resp = client.post("/api/response/isolate-host", json={
        "hostname": "SERVER-TEST-10",
        "reason": "Confirmed lateral movement",
        "dry_run": False
    }, headers=responder_headers)
    assert live_resp.status_code == 200
    action_id = live_resp.json()["action_id"]

    appr_resp = client.post(f"/api/response/actions/{action_id}/approve", json={
        "reason": "Confirmed threat containment"
    }, headers=commander_headers)
    assert appr_resp.status_code == 200
    assert appr_resp.json()["action"]["status"] == "APPROVED"

    # Rollback action
    roll_resp = client.post(f"/api/response/actions/{action_id}/rollback", json={
        "reason": "Containment period elapsed, returning host to normal operations"
    }, headers=commander_headers)
    assert roll_resp.status_code == 200
    assert roll_resp.json()["action"]["status"] == "ROLLED_BACK"

def test_stix_2_1_export():
    stix_resp = client.get("/api/threat-intelligence/stix")
    assert stix_resp.status_code == 200
    bundle = stix_resp.json()
    assert bundle["type"] == "bundle"
    assert len(bundle["objects"]) >= 2
    types = [obj["type"] for obj in bundle["objects"]]
    assert "identity" in types
    assert "indicator" in types
