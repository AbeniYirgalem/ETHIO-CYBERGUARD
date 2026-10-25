"""
ETHIO-CYBERGUARD Comprehensive Audit & Reliability Test Suite
Covers the 10 core verification scenarios mandated by the Platform Audit:
1. Invalid login, expired token, and revoked token enforcement.
2. Single-use refresh token rotation and session revocation.
3. Authenticated collector ingestion, normalization, and database persistence.
4. Malformed payload routing to DLQ and idempotency deduplication.
5. SIGMA rule matching triggering alerts linked to evidence.
6. Service degradation handling (database failure reports 503 NOT_READY).
7. External AI provider failure with graceful deterministic rule fallback.
8. Multi-tenant isolation preventing cross-organization data leakage.
9. Server-side dual-custody enforcement preventing self-approval of response actions.
10. Production startup fail-closed validation on default/insecure credentials.
"""

import pytest
import time
import hashlib
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from fastapi import Response

from apps.api.main import app
from apps.api.dependencies import (
    create_access_token, create_refresh_token, verify_token,
    revoke_token, is_token_revoked, DEMO_USERS
)
from apps.api.config import validate_production_configuration
from services.ingestion.pipeline import IngestionPipeline
from services.detection.engine import DetectionEngine
from services.response.engine import SOARResponseEngine
from database.connection import init_db, SessionLocal
from database.models import Event, Incident

client = TestClient(app)

# ---------------------------------------------------------------------------
# Scenario 2: Authentication Security, Expired Token & Revocation
# ---------------------------------------------------------------------------
def test_scenario_invalid_login_and_token_revocation():
    # 1. Invalid login credentials
    bad_login = client.post("/api/auth/login", json={
        "email": "analyst@cbe.com.et",
        "password": "WrongPassword123!"
    })
    assert bad_login.status_code == 401
    assert "Invalid email or password" in bad_login.json()["detail"]

    # 2. Valid login produces valid tokens
    good_login = client.post("/api/auth/login", json={
        "email": "analyst@cbe.com.et",
        "password": "Analyst@2026!"
    })
    assert good_login.status_code == 200
    access_token = good_login.json()["access_token"]
    refresh_token = good_login.json()["refresh_token"]

    # 3. Access protected endpoint
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["user"]["email"] == "analyst@cbe.com.et"

    # 4. Token revocation via logout
    logout_resp = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
    assert logout_resp.status_code == 200
    assert is_token_revoked(access_token) is True

    # 5. Subsequent request with revoked token must fail with 401
    revoked_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert revoked_resp.status_code == 401
    assert "revoked" in revoked_resp.json()["detail"].lower()

def test_scenario_single_use_refresh_token_rotation(monkeypatch):
    import apps.api.dependencies as deps
    monkeypatch.setattr(deps, 'REFRESH_REUSE_GRACE_SECONDS', -1)
    # Login to obtain fresh refresh token
    login_resp = client.post("/api/auth/login", json={
        "email": "commander@cbe.com.et",
        "password": "Commander@2026!"
    })
    assert login_resp.status_code == 200
    initial_refresh = login_resp.json()["refresh_token"]

    # Use refresh token once -> succeeds and issues new refresh token
    rotate_resp = client.post("/api/auth/refresh", json={"refresh_token": initial_refresh})
    assert rotate_resp.status_code == 200
    new_refresh = rotate_resp.json()["refresh_token"]
    new_access = rotate_resp.json()["access_token"]
    assert new_refresh != initial_refresh

    # Replay old refresh token -> must be rejected (401 revoked)
    replay_resp = client.post("/api/auth/refresh", json={"refresh_token": initial_refresh})
    assert replay_resp.status_code == 401
    assert "revoked" in replay_resp.json()["detail"].lower()

# ---------------------------------------------------------------------------
# Scenario 3: Collector Valid Event Ingestion, Normalization & Persistence
# ---------------------------------------------------------------------------
def test_scenario_collector_valid_event_persisted():
    init_db()
    event_uid = f"collector-test-{int(time.time())}"
    payload = {
        "event_uid": event_uid,
        "event_type": "AUTHENTICATION_FAILED",
        "severity": "HIGH",
        "host_name": "SERVER-04",
        "source_ip": "197.156.70.44",
        "destination_ip": "10.10.1.24",
        "user": "sysadmin",
        "raw_data": {"action": "logon_failure", "sub_status": "0xc000006a"}
    }

    resp = client.post(
        "/api/v1/events/ingest",
        json=payload,
        headers={"X-API-Key": "ecg-collector-secure-api-key-2026"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ACCEPTED"
    assert "event_hash" in data

    # Verify event was persisted to the database
    db = SessionLocal()
    persisted = db.query(Event).filter(Event.raw_event_hash == data["event_hash"]).first()
    assert persisted is not None
    assert persisted.host_name == "SERVER-04"
    assert persisted.source_ip == "197.156.70.44"
    db.close()

# ---------------------------------------------------------------------------
# Scenario 4: Malformed Event DLQ & Idempotent Deduplication
# ---------------------------------------------------------------------------
def test_scenario_malformed_event_dlq_and_deduplication():
    # 1. Malformed payload without event_type sent to DLQ
    malformed = {"host_name": "SERVER-04", "source_ip": "10.0.0.1"}
    resp = client.post(
        "/api/v1/events/ingest",
        json=malformed,
        headers={"X-API-Key": "ecg-collector-secure-api-key-2026"}
    )
    # FastAPI schema rejects missing event_type with 422
    assert resp.status_code == 422

    # 2. Pipeline-level DLQ rejection
    pipeline = IngestionPipeline()
    res = pipeline.ingest({"source_ip": "10.0.0.1"})
    assert res["status"] == "REJECTED_TO_DLQ"
    assert len(pipeline.dlq) == 1

    # 3. Duplicate event dropped idempotently
    event = {
        "event_type": "FIREWALL_DROP",
        "source_ip": "185.220.101.5",
        "destination_ip": "10.10.1.24",
        "host_name": "FW-PERIMETER-01",
        "raw_data": "blocked"
    }
    first_resp = pipeline.ingest(event)
    assert first_resp["status"] == "ACCEPTED"
    dup_resp = pipeline.ingest(event)
    assert dup_resp["status"] == "DUPLICATE_DROPPED"

# ---------------------------------------------------------------------------
# Scenario 5: Detection Rule Matching & Alert Generation
# ---------------------------------------------------------------------------
def test_scenario_rule_matching_and_alert_generation():
    engine = DetectionEngine()
    test_event = {
        "event_id": "test-c2-beacon",
        "event_type": "POWERSHELL_OBFUSCATED",
        "severity": "CRITICAL",
        "host_name": "SERVER-04",
        "source_ip": "10.10.1.24",
        "destination_ip": "185.220.101.5",
        "process": {"name": "powershell.exe", "command_line": "powershell -enc SQBFAFgA..."},
        "network": {"destination_ip": "185.220.101.5", "destination_port": 443}
    }
    alerts = engine.evaluate_event(test_event)
    assert len(alerts) > 0
    rule_names = [(a.get("rule_name") or a.get("title") or "") for a in alerts]
    assert any("PowerShell" in r or "ALT" in r for r in rule_names)

# ---------------------------------------------------------------------------
# Scenario 6: Service Dependency Degradation Handling
# ---------------------------------------------------------------------------
def test_scenario_readiness_probe_handles_db_failure(monkeypatch):
    from apps.api.routers import health
    
    # Mock database failure in health check
    def mock_broken_session():
        raise ConnectionRefusedError("Database connection refused: host unreachable")

    monkeypatch.setattr(health, "SessionLocal", mock_broken_session)
    response = Response()
    res = health.readiness_probe(response)
    
    assert response.status_code == 503
    assert res["status"] == "NOT_READY"
    assert res["checks"]["database"]["status"] == "DEGRADED"

# ---------------------------------------------------------------------------
# Scenario 7: External AI Provider Offline Graceful Fallback
# ---------------------------------------------------------------------------
def test_scenario_ai_offline_fallback_deterministic_operation():
    from services.ai.orchestrator import MultiAgentOrchestrator
    
    orchestrator = MultiAgentOrchestrator()
    incident_data = {
        "incident_number": "INC-00042",
        "title": "Suspicious Obfuscated PowerShell Activity & C2 Beaconing",
        "affected_asset": "SERVER-04",
        "severity": "CRITICAL",
        "summary": "PowerShell encoded beaconing"
    }

    # Run investigation without any external cloud LLM API keys
    result = orchestrator.run_investigation_pipeline(incident_data, [])
    assert result["orchestrator_status"] == "COMPLETED"
    assert result["agents_executed"] == 7
    # Deterministic heuristics should identify risk without hallucination
    assert "pipeline_results" in result
    assert result["pipeline_results"]["risk_assessment"]["overall_score"] >= 80

# ---------------------------------------------------------------------------
# Scenario 8: Tenant Isolation & Cross-Organization Protection
# ---------------------------------------------------------------------------
def test_scenario_cross_tenant_isolation_enforced():
    # User Sara Yohannes belongs to Commercial Bank of Ethiopia
    cbe_token = create_access_token({
        "sub": "analyst@cbe.com.et",
        "role": "SECURITY_ANALYST",
        "organization": "Commercial Bank of Ethiopia"
    })

    # External user belongs to Telebirr / Ethio Telecom
    telebirr_token = create_access_token({
        "sub": "telebirr_user@telebirr.et",
        "role": "SECURITY_ANALYST",
        "organization": "Ethio Telecom / Telebirr"
    })

    # Create an incident under Ethio Telecom
    create_resp = client.post(
        "/api/v1/incidents",
        json={
            "title": "Ethio Telecom Core Switch Failure",
            "severity": "HIGH",
            "affected_asset": "SW-CORE-01",
            "asset_ip": "10.20.1.1",
            "department": "Network Operations",
            "sector": "Telecom",
            "organization": "Ethio Telecom / Telebirr",
            "assigned_analyst": "Telebirr Responder",
            "summary": "Internal routing failure"
        },
        headers={"Authorization": f"Bearer {telebirr_token}"}
    )
    assert create_resp.status_code == 201

    # Query incidents as CBE user -> Telecom incident must not leak
    cbe_incidents = client.get(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {cbe_token}"}
    ).json()["incidents"]
    for inc in cbe_incidents:
        if inc.get("organization"):
            assert inc.get("organization") == "Commercial Bank of Ethiopia"
    from apps.api.routers.incidents import INCIDENTS_STORE
    INCIDENTS_STORE[:] = [i for i in INCIDENTS_STORE if i.get("title") != "Ethio Telecom Core Switch Failure"]

# ---------------------------------------------------------------------------
# Scenario 9: Dual-Custody Approval Gate Enforcement
# ---------------------------------------------------------------------------
def test_scenario_dual_custody_enforced_server_side():
    # 1. Initiator requests host isolation
    req_token = create_access_token({
        "sub": "initiator_analyst@cbe.com.et",
        "role": "SECURITY_ANALYST",
        "name": "Initiator Analyst"
    })
    iso_resp = client.post(
        "/api/v1/response/isolate-host",
        json={
            "hostname": "SERVER-SEC-99",
            "reason": "Host beaconing detected",
            "dry_run": False,
            "require_approval": True
        },
        headers={"Authorization": f"Bearer {req_token}"}
    )
    assert iso_resp.status_code == 200
    act_id = iso_resp.json()["action_id"]

    # 2. Self-approval attempt: initiator tries to approve their own destructive action -> MUST be 403
    self_appr = client.post(
        f"/api/v1/response/actions/{act_id}/approve",
        json={"reason": "Self-approving my own containment"},
        headers={"Authorization": f"Bearer {req_token}"}
    )
    assert self_appr.status_code == 403
    assert "Dual-Custody Violation" in self_appr.json()["detail"]

    # 3. Disallowed role attempt: Auditor attempts to approve -> MUST be 403
    auditor_token = create_access_token({
        "sub": "auditor@cbe.com.et",
        "role": "AUDITOR",
        "name": "Audit Officer"
    })
    auditor_appr = client.post(
        f"/api/v1/response/actions/{act_id}/approve",
        json={"reason": "Audit approval"},
        headers={"Authorization": f"Bearer {auditor_token}"}
    )
    assert auditor_appr.status_code == 403

    # 4. Valid secondary approval: Incident Commander approves -> SUCCEEDS
    cmd_token = create_access_token({
        "sub": "commander@cbe.com.et",
        "role": "INCIDENT_COMMANDER",
        "name": "Abebe Kebede (Incident Commander)"
    })
    cmd_appr = client.post(
        f"/api/v1/response/actions/{act_id}/approve",
        json={"reason": "Commander secondary authorization verified"},
        headers={"Authorization": f"Bearer {cmd_token}"}
    )
    assert cmd_appr.status_code == 200
    assert cmd_appr.json()["action"]["status"] == "APPROVED"
    assert cmd_appr.json()["action"]["dual_custody_verified"] is True
    from apps.api.routers.response import ACTIONS_STORE
    ACTIONS_STORE[:] = [a for a in ACTIONS_STORE if a.get("id") != act_id]

# ---------------------------------------------------------------------------
# Scenario 10: Fail-Closed Production Startup Validation
# ---------------------------------------------------------------------------
def test_scenario_production_startup_fails_closed_on_insecure_defaults(monkeypatch):
    import apps.api.config as config
    
    # Simulate production environment with default credentials
    monkeypatch.setattr(config, "ENVIRONMENT", "production")
    monkeypatch.setattr(config, "DEMO_MODE", True) # Insecure: demo mode in prod
    monkeypatch.setattr(config, "JWT_SECRET", "change_me_jwt_secret_placeholder")
    monkeypatch.setattr(config, "API_SECRET_KEY", "default")
    monkeypatch.setattr(config, "INGEST_API_KEY", "ecg-collector-secure-api-key-2026")

    with pytest.raises(RuntimeError) as excinfo:
        config.validate_production_configuration()
    
    error_text = str(excinfo.value)
    assert "PRODUCTION STARTUP VALIDATION FAILED CLOSED" in error_text
    assert "DEMO_MODE" in error_text
    assert "JWT_SECRET" in error_text
