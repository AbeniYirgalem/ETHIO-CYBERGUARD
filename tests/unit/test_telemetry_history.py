"""Hourly telemetry history, persistence of counters, and the richer dashboard payload."""

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routers.incidents import INCIDENTS_STORE
from services.telemetry.stats import TelemetryStats, TIMELINE_HOURS

client = TestClient(app)

T0 = 1_800_000_000.0 - (1_800_000_000.0 % 3600)  # start of an hour (UTC)


def _stats(now, **kw):
    return TelemetryStats(clock=lambda: now[0], **kw)


def test_timeline_has_24_hourly_buckets_with_empty_hours():
    now = [T0 + 120]
    stats = _stats(now)
    stats.record_event("CRITICAL", [{"title": "x"}, {"title": "y"}])
    stats.record_event("INFO")
    rows = stats.snapshot()["timeline"]
    assert len(rows) == TIMELINE_HOURS
    assert rows[-1] == {"hour": rows[-1]["hour"], "events": 2, "critical": 1, "alerts": 2}
    assert all(r["events"] == 0 for r in rows[:-1])
    assert rows[-1]["hour"].endswith(":00:00Z")


def test_events_land_in_the_hour_they_arrived():
    now = [T0 + 10]
    stats = _stats(now)
    stats.record_event("LOW")
    now[0] += 3 * 3600
    stats.record_event("LOW")
    stats.record_event("LOW")
    rows = stats.timeline()
    assert [r["events"] for r in rows[-4:]] == [1, 0, 0, 2]


def test_old_hours_roll_out_of_the_window():
    now = [T0]
    stats = _stats(now)
    stats.record_event("HIGH")
    now[0] += 25 * 3600
    assert sum(r["events"] for r in stats.timeline()) == 0


def test_persist_is_throttled_and_flush_writes_the_rest():
    now = [T0]
    saved = []
    stats = _stats(now, persist=saved.append, persist_interval=5.0)
    stats.record_event("INFO")           # first write is immediate
    stats.record_event("INFO")           # within 5 s: held back
    assert len(saved) == 1 and saved[0]["events_today"] == 1
    now[0] += 6
    stats.record_event("INFO")
    assert len(saved) == 2 and saved[1]["events_today"] == 3
    stats.record_event("INFO")
    stats.flush()
    assert saved[-1]["events_today"] == 4
    stats.flush()                        # nothing new: no extra write
    assert len(saved) == 3


def test_state_survives_a_restart_on_the_same_day():
    now = [T0 + 60]
    saved = []
    first = _stats(now, persist=saved.append)
    first.record_event("CRITICAL", [{"title": "PowerShell", "severity": "CRITICAL"}])
    first.flush()

    second = _stats(now)
    assert second.load_state(saved[-1]) is True
    snap = second.snapshot()
    assert snap["events_processed_today"] == 1
    assert snap["by_severity"]["CRITICAL"] == 1
    assert snap["top_alerts"][0]["name"] == "PowerShell"
    assert snap["timeline"][-1]["events"] == 1


def test_next_day_keeps_history_but_resets_daily_counters():
    now = [T0]
    saved = []
    first = _stats(now, persist=saved.append)
    first.record_event("HIGH")
    first.flush()

    now[0] += 24 * 3600 + 60
    second = _stats(now)
    second.load_state(saved[-1])
    snap = second.snapshot()
    assert snap["events_processed_today"] == 0
    assert sum(r["events"] for r in snap["timeline"]) == 0  # 25 h old: outside the 24 h view
    assert second._hourly  # still held (within 48 h) for later queries


def test_corrupt_saved_state_is_ignored():
    stats = _stats([T0])
    assert stats.load_state("not a dict") is False
    assert stats.load_state({"hourly": {"bad": 1, "2026-10-24T10": {"events": "x"}}, "day": "nope"}) is True
    assert stats.snapshot()["events_processed_today"] == 0


def test_a_failing_persist_never_breaks_ingestion():
    def boom(_doc):
        raise RuntimeError("db down")

    stats = _stats([T0], persist=boom)
    stats.record_event("INFO")           # must not raise
    assert stats.snapshot()["events_processed_today"] == 1


# ---------- dashboard payload ----------

def test_dashboard_returns_timeline_and_sector_severity_detail(commander_headers):
    res = client.get("/api/dashboard/stats", headers=commander_headers)
    assert res.status_code == 200
    body = res.json()
    assert len(body["timeline"]) == TIMELINE_HOURS
    assert {"hour", "events", "critical", "alerts"} <= set(body["timeline"][0])
    for sector, profile in body["sector_profiles"].items():
        assert {"active_alerts", "critical", "high", "max_severity"} <= set(profile), sector
    from services.security.tenancy import scope
    expected = sum(1 for i in scope({"organization": "Commercial Bank of Ethiopia"}, INCIDENTS_STORE) if str(i.get("status", "")).upper() != "CLOSED")
    assert sum(p["active_alerts"] for p in body["sector_profiles"].values()) == expected
