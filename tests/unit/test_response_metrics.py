"""MTTD / MTTR are measured from incident history, never invented."""

from fastapi.testclient import TestClient

from apps.api.main import app
from services.telemetry.response_metrics import compute_response_metrics, parse_time


def _incident(first_seen, *history):
    return {
        "first_seen": first_seen,
        "history": [{"new_status": status, "timestamp": ts} for status, ts in history],
    }


def test_no_incidents_means_not_measured():
    result = compute_response_metrics([])
    assert result["mean_time_to_detect_minutes"] is None
    assert result["mean_time_to_respond_minutes"] is None
    assert result["mttd_samples"] == 0 and result["mttr_samples"] == 0


def test_mttd_is_time_until_first_action():
    inc = _incident(
        "2026-09-30 10:00:00+00:00",
        ("NEW", "2026-09-30T10:00:00Z"),
        ("TRIAGED", "2026-09-30T10:05:00Z"),
        ("INVESTIGATING", "2026-09-30T10:20:00Z"),
    )
    result = compute_response_metrics([inc])
    assert result["mean_time_to_detect_minutes"] == 5.0
    assert result["mean_time_to_respond_minutes"] is None  # never contained yet


def test_mttr_is_time_to_first_containment_or_close():
    inc = _incident(
        "2026-09-30T10:00:00Z",
        ("TRIAGED", "2026-09-30T10:10:00Z"),
        ("CONTAINED", "2026-09-30T10:40:00Z"),
        ("CLOSED", "2026-09-30T12:00:00Z"),
    )
    result = compute_response_metrics([inc])
    assert result["mean_time_to_respond_minutes"] == 40.0
    assert result["mttr_samples"] == 1


def test_average_over_several_incidents_skips_unfinished_ones():
    done_a = _incident("2026-09-30T10:00:00Z", ("TRIAGED", "2026-09-30T10:10:00Z"), ("CLOSED", "2026-09-30T10:30:00Z"))
    done_b = _incident("2026-09-30T11:00:00Z", ("TRIAGED", "2026-09-30T11:20:00Z"), ("CONTAINED", "2026-09-30T12:30:00Z"))
    waiting = _incident("2026-09-30T13:00:00Z", ("NEW", "2026-09-30T13:00:00Z"))
    result = compute_response_metrics([done_a, done_b, waiting])
    assert result["mean_time_to_detect_minutes"] == 15.0   # (10 + 20) / 2
    assert result["mean_time_to_respond_minutes"] == 60.0  # (30 + 90) / 2
    assert result["mttd_samples"] == 2 and result["mttr_samples"] == 2


def test_bad_data_is_ignored_not_crashing():
    bad = [
        {"first_seen": "not a date", "history": [{"new_status": "CLOSED", "timestamp": "2026-09-30T10:00:00Z"}]},
        {"first_seen": "2026-09-30T10:00:00Z", "history": "oops"},
        {"first_seen": "2026-09-30T10:00:00Z"},
        # Clock skew: the action is dated before the incident started
        _incident("2026-09-30T10:00:00Z", ("CLOSED", "2026-09-30T09:00:00Z")),
    ]
    result = compute_response_metrics(bad)
    assert result["mean_time_to_detect_minutes"] is None
    assert result["mean_time_to_respond_minutes"] is None


def test_parse_time_handles_store_formats():
    assert parse_time("2026-09-30 10:42:00+03:00").utcoffset().total_seconds() == 3 * 3600
    assert parse_time("2026-09-30T10:43:00Z").utcoffset().total_seconds() == 0
    assert parse_time("2026-09-30T10:43:00").tzinfo is not None
    assert parse_time(None) is None and parse_time("") is None


def test_dashboard_reports_measured_values(admin_headers):
    client = TestClient(app)
    body = client.get("/api/dashboard/stats", headers=admin_headers).json()
    metrics = body["metrics"]
    assert "mean_time_to_detect_minutes" in metrics and "mean_time_to_respond_minutes" in metrics
    for key in ("mean_time_to_detect_minutes", "mean_time_to_respond_minutes"):
        assert metrics[key] is None or metrics[key] >= 0
    assert body["response_metrics"]["mttd_samples"] >= 0
