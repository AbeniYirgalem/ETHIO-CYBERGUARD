"""Live data pipeline: telemetry stats, real dashboard numbers, ingest -> stream broadcast."""

import uuid

import pytest
from fastapi.testclient import TestClient

from apps.api import dependencies
from apps.api.main import app
from apps.api.routers.incidents import INCIDENTS_STORE
from services.ingestion.pipeline import IngestionPipeline
from services.telemetry.stats import TelemetryStats, telemetry_stats
import apps.api.main as main_module

client = TestClient(app)


# ---------- TelemetryStats (fake clock) ----------

def test_stats_eps_window_and_today_counter():
    now = [1_800_000_000.0]
    stats = TelemetryStats(window_seconds=60, clock=lambda: now[0])
    for _ in range(30):
        stats.record_event("HIGH")
    snap = stats.snapshot()
    assert snap["events_per_second"] == 0.5
    assert snap["events_processed_today"] == 30
    assert snap["by_severity"]["HIGH"] == 30

    now[0] += 61  # window expires, daily total stays
    snap = stats.snapshot()
    assert snap["events_per_second"] == 0
    assert snap["events_processed_today"] == 30


def test_stats_daily_counter_resets_at_utc_midnight():
    now = [1_800_000_000.0]
    stats = TelemetryStats(clock=lambda: now[0])
    stats.record_event("INFO")
    now[0] += 86_400
    assert stats.snapshot()["events_processed_today"] == 0


def test_stats_top_alerts_sorted_by_count():
    stats = TelemetryStats()
    a = {"title": "PowerShell", "severity": "CRITICAL", "mitre_tactic": "Execution"}
    b = {"title": "Brute force", "severity": "HIGH"}
    stats.record_event("CRITICAL", [a])
    stats.record_event("HIGH", [b])
    stats.record_event("HIGH", [b])
    top = stats.snapshot()["top_alerts"]
    assert [t["name"] for t in top] == ["Brute force", "PowerShell"]
    assert top[0]["count"] == 2


# ---------- duplicate detection no longer swallows different events ----------

def test_pipeline_keeps_different_events_of_same_type():
    pipeline = IngestionPipeline()
    first = {"event_id": "e1", "event_type": "process_execution", "timestamp": "t1", "user": "a"}
    second = {"event_id": "e2", "event_type": "process_execution", "timestamp": "t2", "user": "a"}
    assert pipeline.ingest(first)["status"] == "ACCEPTED"
    assert pipeline.ingest(second)["status"] == "ACCEPTED"
    assert pipeline.ingest(first)["status"] == "DUPLICATE_DROPPED"


# ---------- dashboard numbers are real ----------

@pytest.fixture
def clean_stats():
    telemetry_stats.reset()
    yield
    telemetry_stats.reset()


def _event(**overrides):
    body = {
        "event_uid": f"test-{uuid.uuid4()}",
        "timestamp": "2026-10-24T10:00:00+00:00",
        "event_type": "process_execution",
        "severity": "HIGH",
        "user": "tester",
        "source": {"hostname": "TEST-HOST", "ip": "10.0.0.9"},
        "process": {"name": "cmd.exe", "command_line": "cmd /c whoami"},
    }
    body.update(overrides)
    return body


def test_dashboard_matches_incident_store(clean_stats):
    data = client.get("/api/dashboard/stats").json()
    active = [i for i in INCIDENTS_STORE if str(i["status"]).upper() != "CLOSED"]
    assert data["metrics"]["active_incidents"] == len(active)
    assert data["metrics"]["critical_alerts"] == sum(1 for i in active if i["severity"] == "CRITICAL")
    assert data["metrics"]["events_per_second"] == 0
    assert data["metrics"]["mean_time_to_respond_minutes"] is None


def test_ingested_event_shows_up_in_dashboard(clean_stats):
    resp = client.post("/api/v1/events/ingest", json=_event())
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "ACCEPTED"

    data = client.get("/api/dashboard/stats").json()
    assert data["metrics"]["events_processed_today"] == 1
    assert data["metrics"]["events_per_second"] > 0
    assert data["telemetry"]["by_severity"]["HIGH"] == 1


def test_duplicate_event_is_not_counted(clean_stats):
    body = _event()
    assert client.post("/api/v1/events/ingest", json=body).json()["status"] == "ACCEPTED"
    assert client.post("/api/v1/events/ingest", json=body).json()["status"] == "DUPLICATE_DROPPED"
    assert client.get("/api/dashboard/stats").json()["metrics"]["events_processed_today"] == 1


def test_dashboard_requires_login_in_production(monkeypatch):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    assert client.get("/api/dashboard/stats").status_code == 401
    assert client.get("/api/v1/stats/overview").status_code == 401


# ---------- ingest pushes to the live stream ----------

def test_ingest_broadcasts_event_without_raw_data(clean_stats, monkeypatch):
    sent = []

    async def fake_broadcast(message):
        sent.append(message)

    monkeypatch.setattr(main_module.ws_manager, "broadcast", fake_broadcast)

    body = _event(raw_data={"secret": "must-not-leave-the-server"})
    resp = client.post("/api/v1/events/ingest", json=body)
    assert resp.status_code == 200

    assert len(sent) == 1
    message = sent[0]
    assert message["type"] == "EVENT_INGESTED"
    assert message["event"]["event_id"] == body["event_uid"]
    assert message["event"]["source"]["hostname"] == "TEST-HOST"
    assert "raw_data" not in message["event"]
    assert message["stats"]["events_processed_today"] == 1

    # A duplicate is dropped silently and is not pushed again.
    client.post("/api/v1/events/ingest", json=body)
    assert len(sent) == 1


def test_ingest_requires_collector_key_in_production(monkeypatch):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)
    assert client.post("/api/v1/events/ingest", json=_event()).status_code == 401
