"""Persistence: incidents, SOAR actions and the audit log survive an API restart."""

import json

from fastapi.testclient import TestClient
from sqlalchemy import update

from apps.api import dependencies
from apps.api.main import app
from apps.api.routers import response as response_module
from apps.api.routers.incidents import INCIDENTS_STORE
from apps.api.routers.response import ACTIONS_STORE, AUDIT_LOG_STORE, verify_audit_chain
from database import state_store

client = TestClient(app)


def _simulate_restart():
    """Wipe the in-memory stores, then restore them exactly as API startup does."""
    INCIDENTS_STORE.clear()
    ACTIONS_STORE.clear()
    AUDIT_LOG_STORE.clear()
    return state_store.restore_all()


def test_save_and_load_roundtrip_and_overwrite():
    state_store.save("roundtrip_test", [{"id": "1", "name": "አዲስ አበባ"}])
    assert state_store.load("roundtrip_test") == [{"id": "1", "name": "አዲስ አበባ"}]
    state_store.save("roundtrip_test", [{"id": "2"}])
    assert state_store.load("roundtrip_test") == [{"id": "2"}]


def test_restore_all_loads_into_same_list_object_and_seeds_when_empty():
    seed = [{"id": "seed-1"}]
    state_store.register("restore_test", seed)
    first = state_store.restore_all()
    assert first["restore_test"] == "seeded"
    assert state_store.load("restore_test") == [{"id": "seed-1"}]

    seed_ref = seed
    state_store.save("restore_test", [{"id": "saved-A"}, {"id": "saved-B"}])
    second = state_store.restore_all()
    assert second["restore_test"] == "restored"
    assert seed is seed_ref and seed == [{"id": "saved-A"}, {"id": "saved-B"}]


def test_corrupt_saved_state_is_ignored_not_fatal():
    state_store.save("corrupt_test", [{"id": "ok"}])
    with state_store.engine.begin() as conn:
        conn.execute(
            update(state_store.state_documents)
            .where(state_store.state_documents.c.name == "corrupt_test")
            .values(data="{not valid json")
        )
    assert state_store.load("corrupt_test") is None


def test_incident_created_via_api_survives_restart(commander_headers):
    resp = client.post(
        "/api/incidents",
        json={
            "title": "Persistence check incident",
            "severity": "HIGH",
            "affected_asset": "SERVER-77",
            "summary": "created to verify durable storage",
        },
        headers=commander_headers,
    )
    assert resp.status_code == 201, resp.text
    number = resp.json().get("incident_number") or resp.json()["incident"]["incident_number"]

    outcome = _simulate_restart()
    assert outcome["incidents"] == "restored"
    assert any(i["incident_number"] == number for i in INCIDENTS_STORE)

    fetched = client.get(f"/api/incidents/{number}", headers=commander_headers)
    assert fetched.status_code == 200


def test_soar_action_and_audit_chain_survive_restart(responder_headers, commander_headers):
    resp = client.post(
        "/api/response/block-ip",
        json={"ip_address": "203.0.113.77", "reason": "persistence test", "dry_run": False},
        headers=responder_headers,
    )
    assert resp.status_code == 200
    action_id = resp.json()["action_id"]
    approve = client.post(
        f"/api/response/actions/{action_id}/approve",
        json={"reason": "second approver confirms"},
        headers=commander_headers,
    )
    assert approve.status_code == 200

    audit_before = len(AUDIT_LOG_STORE)
    outcome = _simulate_restart()
    assert outcome["response_actions"] == "restored" and outcome["audit_log"] == "restored"

    restored = next(a for a in ACTIONS_STORE if a["id"] == action_id)
    assert restored["status"] == "APPROVED"
    assert len(AUDIT_LOG_STORE) == audit_before

    verify = client.get("/api/v1/response/audit-log/verify", headers=commander_headers)
    assert verify.status_code == 200
    assert verify.json()["valid"] is True

    # New audit entries after the restart must keep chaining correctly.
    client.post(
        "/api/response/block-ip",
        json={"ip_address": "203.0.113.78", "reason": "post-restart entry", "dry_run": False},
        headers=responder_headers,
    )
    assert client.get("/api/v1/response/audit-log/verify", headers=commander_headers).json()["valid"] is True


def test_verify_audit_chain_detects_tampering():
    genesis = {"id": "AUD-001", "operator": "system", "action": "A", "target": "t", "result": "OK",
               "timestamp": "t0", "prev_hash": "0" * 64, "integrity_hash": "g" * 64}
    import hashlib
    h = hashlib.sha256(f"{genesis['integrity_hash']}|alice|APPROVE|x|SUCCESS|t1".encode()).hexdigest()
    second = {"id": "AUD-002", "operator": "alice", "action": "APPROVE", "target": "x", "result": "SUCCESS",
              "timestamp": "t1", "prev_hash": genesis["integrity_hash"], "integrity_hash": h}
    assert verify_audit_chain([second, genesis])["valid"] is True

    tampered = dict(second, result="FAILURE")
    report = verify_audit_chain([tampered, genesis])
    assert report["valid"] is False and report["broken_entries"] == ["AUD-002"]


def test_demo_seed_actions_are_rearmed_after_restart(monkeypatch):
    monkeypatch.setattr(response_module, "DEMO_MODE", True)
    for action in ACTIONS_STORE:
        if action["id"] == "ACT-001" and not action.get("reviewed_by"):
            action["status"] = "EXPIRED"
            action["expires_at"] = "2020-01-01T00:00:00+00:00"
    response_module._rearm_demo_seed_actions()
    act = next(a for a in ACTIONS_STORE if a["id"] == "ACT-001")
    if not act.get("reviewed_by"):
        assert act["status"] == "PENDING_APPROVAL"


def test_incident_by_id_v1_requires_login_in_production_mode(monkeypatch, commander_headers):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    assert client.get("/api/v1/incidents/INC-00042").status_code == 401
    assert client.get("/api/v1/incidents/INC-00042", headers=commander_headers).status_code == 200
