"""
Per-organization isolation through the real API.

Two organizations share one server: the built-in demo bank (Commercial Bank of Ethiopia) and a
second tenant, "Awash Bank". Nothing created by one may be visible to, or changeable by, the
other. SUPER_ADMIN is the national administrator and sees everything.
"""

import json
import uuid
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

import apps.api.tenancy as collector_tenancy
from apps.api import dependencies
from apps.api.main import app
from apps.api.routers.incidents import INCIDENTS_STORE
from apps.api.routers.response import ACTIONS_STORE, AUDIT_LOG_STORE
from database import state_store
from services.security.passwords import hash_password
from services.telemetry.stats import telemetry_registry, telemetry_stats

client = TestClient(app)
AWASH = "org_awash_bank"
PASSWORD = "Awash-Secure-2026!"
INGEST = "/api/v1/events/ingest"


# ---------------- fixtures ----------------

@pytest.fixture
def clean_telemetry():
    telemetry_stats.reset()
    telemetry_registry.reset()
    yield
    telemetry_stats.reset()
    telemetry_registry.reset()


@pytest.fixture
def isolated_stores():
    """Whatever a test creates is removed again, in memory and in the saved copy."""
    incidents, actions, audit = list(INCIDENTS_STORE), list(ACTIONS_STORE), list(AUDIT_LOG_STORE)
    yield
    INCIDENTS_STORE[:] = incidents
    ACTIONS_STORE[:] = actions
    AUDIT_LOG_STORE[:] = audit
    state_store.save("incidents")
    state_store.save("response_actions")
    state_store.save("audit_log")


def _login(email: str):
    resp = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def awash(monkeypatch, isolated_stores, clean_telemetry):
    """Two signed-in Awash Bank users: a responder (requests actions) and a commander (approves)."""
    users = {
        "responder@awash.example": ("usr_awash_resp", "INCIDENT_RESPONDER"),
        "commander@awash.example": ("usr_awash_cmd", "INCIDENT_COMMANDER"),
    }
    for email, (user_id, role) in users.items():
        monkeypatch.setitem(dependencies.DEMO_USERS, email, {
            "id": user_id, "email": email, "name": f"Awash {role.title()}", "role": role,
            "department": "SOC", "organization": "Awash Bank", "password_hash": hash_password(PASSWORD),
        })
    return SimpleNamespace(resp=_login("responder@awash.example"), cmd=_login("commander@awash.example"))


def _open_incident(headers, sector="AwashSector"):
    resp = client.post("/api/incidents", json={
        "title": "Awash core banking outage", "severity": "CRITICAL", "sector": sector,
        "affected_asset": "AWASH-DB-01", "asset_ip": "10.50.0.5", "summary": "Database unreachable",
    }, headers=headers)
    assert resp.status_code == 201, resp.text
    return resp.json()["incident"]


def _event(**overrides):
    body = {
        "event_uid": f"tenant-{uuid.uuid4()}",
        "timestamp": "2026-10-24T10:00:00+00:00",
        "event_type": "process_execution",
        "severity": "HIGH",
        "user": "tester",
        "source": {"hostname": "TEST-HOST", "ip": "10.0.0.9"},
        "process": {"name": "cmd.exe", "command_line": "cmd /c whoami"},
    }
    body.update(overrides)
    return body


def _numbers(headers):
    return {i["incident_number"] for i in client.get("/api/incidents", headers=headers).json()["incidents"]}


# ---------------- incidents ----------------

def test_incident_lists_are_separate(awash, commander_headers, admin_headers):
    mine = _open_incident(awash.cmd)
    assert mine["org_id"] == AWASH

    awash_view = client.get("/api/incidents", headers=awash.cmd).json()
    assert awash_view["total"] == 1
    assert [i["incident_number"] for i in awash_view["incidents"]] == [mine["incident_number"]]

    cbe_numbers = _numbers(commander_headers)
    assert "INC-00042" in cbe_numbers
    assert mine["incident_number"] not in cbe_numbers

    national = _numbers(admin_headers)          # SUPER_ADMIN sees both organizations
    assert {"INC-00042", mine["incident_number"]} <= national


@pytest.mark.parametrize("method,path,body", [
    ("get", "/api/incidents/INC-00042", None),
    ("get", "/api/incidents/e0000000-0000-0000-0000-000000000001", None),
    ("get", "/api/incidents/INC-00042/comments", None),
    ("get", "/api/incidents/INC-00042/timeline", None),
    ("post", "/api/incidents/INC-00042/comments", {"content": "hello"}),
    ("post", "/api/incidents/INC-00042/tasks", {"title": "task"}),
    ("post", "/api/incidents/INC-00042/transition", {"new_status": "CLOSED"}),
    ("post", "/api/incidents/INC-00042/evidence", {"value": "x"}),
    ("patch", "/api/incidents/INC-00042", {"summary": "hijacked"}),
])
def test_other_organization_cannot_read_or_change_an_incident(awash, method, path, body):
    resp = client.request(method.upper(), path, json=body, headers=awash.cmd)
    assert resp.status_code == 404, resp.text


def test_own_organization_still_reaches_its_incident(commander_headers):
    assert client.get("/api/incidents/INC-00042", headers=commander_headers).status_code == 200
    summary = [i for i in INCIDENTS_STORE if i["incident_number"] == "INC-00042"][0]["summary"]
    assert summary != "hijacked"


# ---------------- SOAR actions and audit ----------------

def test_actions_are_separate_and_approval_stays_inside_the_organization(awash, commander_headers):
    queued = client.post("/api/response/block-ip", json={
        "ip_address": "203.0.113.7", "reason": "Awash blocklist", "incident_number": "INC-00099",
    }, headers=awash.resp)
    assert queued.status_code == 200, queued.text
    action_id = queued.json()["action_id"]
    assert queued.json()["action"]["org_id"] == AWASH

    # The other bank cannot see it, approve it, reject it or roll it back.
    cbe_ids = {a["id"] for a in client.get("/api/response/actions", headers=commander_headers).json()["actions"]}
    assert action_id not in cbe_ids and "ACT-001" in cbe_ids
    for verb in ("approve", "reject", "rollback"):
        resp = client.post(f"/api/response/actions/{action_id}/{verb}", json={"reason": "not mine"},
                           headers=commander_headers)
        assert resp.status_code == 404, f"{verb}: {resp.text}"

    # Awash cannot touch the demo bank's seeded actions either.
    awash_ids = {a["id"] for a in client.get("/api/response/actions", headers=awash.cmd).json()["actions"]}
    assert awash_ids == {action_id}
    assert client.post("/api/response/actions/ACT-001/approve", json={"reason": "no"},
                       headers=awash.cmd).status_code == 404

    # Inside Awash, dual custody still works: a different person approves.
    approved = client.post(f"/api/response/actions/{action_id}/approve", json={"reason": "Verified"},
                           headers=awash.cmd)
    assert approved.status_code == 200, approved.text
    assert approved.json()["action"]["status"] == "APPROVED"


def test_audit_log_and_its_verification_are_scoped(awash, commander_headers, admin_headers):
    client.post("/api/response/block-ip", json={"ip_address": "203.0.113.8", "reason": "Awash blocklist"},
                headers=awash.resp)

    awash_log = client.get("/api/response/audit-log", headers=awash.cmd).json()
    cbe_log = client.get("/api/response/audit-log", headers=commander_headers).json()
    national_log = client.get("/api/response/audit-log", headers=admin_headers).json()

    assert awash_log["total"] >= 1
    assert {e["org_id"] for e in awash_log["audit_logs"]} == {AWASH}
    assert AWASH not in {e.get("org_id") for e in cbe_log["audit_logs"]}
    assert national_log["total"] == awash_log["total"] + cbe_log["total"]

    for headers, log in ((awash.cmd, awash_log), (commander_headers, cbe_log)):
        check = client.get("/api/response/audit-log/verify", headers=headers).json()
        assert check["valid"] is True
        assert check["entries"] == log["total"]
        assert check["broken_entries"] == []


# ---------------- dashboard, reports, AI ----------------

def test_dashboard_numbers_are_per_organization(awash, commander_headers, admin_headers):
    before = client.get("/api/dashboard/stats", headers=commander_headers).json()
    _open_incident(awash.cmd, sector="AwashSector")

    mine = client.get("/api/dashboard/stats", headers=awash.cmd).json()
    assert mine["tenant"] == {"org_id": AWASH, "scope": "organization"}
    assert mine["metrics"]["active_incidents"] == 1
    assert mine["metrics"]["critical_alerts"] == 1
    assert mine["metrics"]["pending_approvals"] == 0
    assert set(mine["sector_profiles"]) == {"AwashSector"}

    cbe = client.get("/api/dashboard/stats", headers=commander_headers).json()
    assert cbe["metrics"]["active_incidents"] == before["metrics"]["active_incidents"]
    assert "AwashSector" not in cbe["sector_profiles"]

    national = client.get("/api/dashboard/stats", headers=admin_headers).json()
    assert national["tenant"]["scope"] == "national"
    assert national["metrics"]["active_incidents"] == before["metrics"]["active_incidents"] + 1
    assert "AwashSector" in national["sector_profiles"]


def test_reports_and_ai_do_not_leak_other_organizations(awash, commander_headers):
    assert client.get("/api/reports/incident/INC-00042", headers=commander_headers).status_code == 200
    assert client.get("/api/reports/incident/INC-00042", headers=awash.cmd).status_code == 404

    # An organization with no incidents gets "not found", never another bank's incident.
    body = {"query": "why is it critical?", "incident_number": "INC-00042"}
    assert client.post("/api/ai/chat", json=body, headers=awash.cmd).status_code == 404
    assert client.post("/api/ai/investigate", json={"incident_number": "INC-00042"},
                       headers=awash.cmd).status_code == 404

    _open_incident(awash.cmd)
    chat = client.post("/api/ai/chat", json=body, headers=awash.cmd)
    assert chat.status_code == 200, chat.text
    assert "Obfuscated PowerShell" not in json.dumps(chat.json())


def test_reports_require_login_in_production(monkeypatch):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    for path in ("/api/reports/incident/INC-00042", "/api/reports/executive", "/api/reports/compliance"):
        assert client.get(path).status_code == 401, path


def test_users_created_for_a_new_organization_start_with_an_empty_workspace(admin_headers):
    email = "new.analyst@telebirr.example"
    created = client.post("/api/auth/register", json={
        "email": email, "password": "Valid-Password-2026!", "full_name": "Telebirr Analyst",
        "organization": "Telebirr", "role": "INCIDENT_COMMANDER",
    }, headers=admin_headers)
    assert created.status_code == 201, created.text
    try:
        login = client.post("/api/auth/login", json={"email": email, "password": "Valid-Password-2026!"})
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        assert client.get("/api/incidents", headers=headers).json()["total"] == 0
        assert client.get("/api/response/actions", headers=headers).json()["total"] == 0
        assert client.get("/api/incidents/INC-00042", headers=headers).status_code == 404
    finally:
        dependencies.DEMO_USERS.pop(email, None)
        dependencies.persist_users()


# ---------------- event statistics and the live stream ----------------

def test_event_counts_and_duplicates_are_per_organization(awash, commander_headers, admin_headers):
    body = _event()
    first = client.post(INGEST, json=body, headers={"X-Org-ID": AWASH})
    assert first.json()["status"] == "ACCEPTED"
    # The very same event from another organization is not mistaken for a duplicate...
    assert client.post(INGEST, json=body).json()["status"] == "ACCEPTED"
    # ...but a replay inside one organization still is.
    assert client.post(INGEST, json=body, headers={"X-Org-ID": AWASH}).json()["status"] == "DUPLICATE_DROPPED"

    assert client.get("/api/dashboard/stats", headers=awash.cmd).json()["metrics"]["events_processed_today"] == 1
    assert client.get("/api/dashboard/stats", headers=commander_headers).json()["metrics"]["events_processed_today"] == 1
    assert client.get("/api/dashboard/stats", headers=admin_headers).json()["metrics"]["events_processed_today"] == 2


def test_live_stream_only_carries_the_organizations_own_events(awash, commander_headers, admin_headers):
    token = lambda headers: headers["Authorization"].split(" ", 1)[1]  # noqa: E731
    awash_event, cbe_event = _event(), _event()

    with client.websocket_connect(f"/ws/live-events?token={token(awash.cmd)}") as ws_awash, \
            client.websocket_connect(f"/ws/live-events?token={token(commander_headers)}") as ws_cbe, \
            client.websocket_connect(f"/ws/live-events?token={token(admin_headers)}") as ws_national:
        assert ws_awash.receive_json()["tenant_channel"] == f"tenant:{AWASH}"
        assert ws_cbe.receive_json()["tenant_channel"] == "tenant:org_cbe_01"
        assert ws_national.receive_json()["type"] == "CONNECTION_ESTABLISHED"

        assert client.post(INGEST, json=awash_event, headers={"X-Org-ID": AWASH}).status_code == 200
        assert client.post(INGEST, json=cbe_event).status_code == 200

        # Awash's event came first; had it leaked, the CBE console would receive it first.
        got_awash = ws_awash.receive_json()
        assert got_awash["event"]["event_id"] == awash_event["event_uid"]
        assert got_awash["org_id"] == AWASH
        assert got_awash["stats"]["events_processed_today"] == 1

        assert ws_cbe.receive_json()["event"]["event_id"] == cbe_event["event_uid"]

        # The national administrator sees both, in order.
        assert ws_national.receive_json()["event"]["event_id"] == awash_event["event_uid"]
        assert ws_national.receive_json()["event"]["event_id"] == cbe_event["event_uid"]


def test_collector_key_decides_the_organization(monkeypatch, clean_telemetry):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    monkeypatch.setattr(dependencies, "INGEST_API_KEY", "shared-collector-key-0002")
    monkeypatch.setattr(collector_tenancy, "INGEST_ORG_KEYS", {"awash-collector-key-0001": AWASH})

    assert client.post(INGEST, json=_event()).status_code == 401
    assert client.post(INGEST, json=_event(), headers={"X-API-Key": "wrong-key"}).status_code == 401

    # An organization key fixes the organization: an X-Org-ID header cannot redirect the events.
    sent = client.post(INGEST, json=_event(),
                       headers={"X-API-Key": "awash-collector-key-0001", "X-Org-ID": "org_cbe_01"})
    assert sent.status_code == 200, sent.text
    assert telemetry_registry.for_org(AWASH).snapshot()["events_processed_today"] == 1
    assert telemetry_registry.for_org("org_cbe_01").snapshot()["events_processed_today"] == 0

    # The shared key feeds the default organization.
    assert client.post(INGEST, json=_event(), headers={"X-API-Key": "shared-collector-key-0002"}).status_code == 200
    assert telemetry_registry.for_org("org_cbe_01").snapshot()["events_processed_today"] == 1
