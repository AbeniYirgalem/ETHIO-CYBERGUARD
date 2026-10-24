"""
Live telemetry statistics for the SOC dashboard.

Counts what the ingestion endpoint really receives: events per second over a
sliding window, events seen today (UTC), severity mix, the most frequent
detection alerts and an hourly history (last 24 hours) for the Overview
timeline. Nothing here is simulated.

Persistence
-----------
The counters and the hourly history survive an API restart. They are written
through the ``persist`` callback (the global instance uses the durable state
store), at most once every ``persist_interval`` seconds, and flushed at
shutdown. A crash can therefore lose at most the last few seconds of counts.
The per-second window is deliberately not persisted: it describes "right now".
"""

import logging
import threading
import time
from collections import Counter, deque
from datetime import datetime, timezone
from typing import Any, Callable, Deque, Dict, List, Optional

logger = logging.getLogger("ecg.telemetry")

_SEVERITIES = ("INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL")
HOURS_KEPT = 48          # buckets older than this are dropped
TIMELINE_HOURS = 24      # buckets returned to the dashboard
STATE_NAME = "telemetry_stats"
_STATE_VERSION = 1


def _as_int(value: Any) -> int:
    try:
        return max(int(value), 0)
    except (TypeError, ValueError):
        return 0


class TelemetryStats:
    def __init__(
        self,
        window_seconds: int = 60,
        clock: Callable[[], float] = time.time,
        persist: Optional[Callable[[Dict[str, Any]], Any]] = None,
        persist_interval: float = 5.0,
    ):
        self.window = window_seconds
        self._clock = clock
        self._persist = persist
        self._persist_interval = persist_interval
        self._last_persist: Optional[float] = None
        self._dirty = False
        self._lock = threading.Lock()
        self._timestamps: Deque[float] = deque(maxlen=200_000)
        self._hourly: Dict[str, Dict[str, int]] = {}
        self._reset_counters(self._today())

    # ---- internals ----
    def _today(self) -> str:
        return datetime.fromtimestamp(self._clock(), tz=timezone.utc).strftime("%Y-%m-%d")

    @staticmethod
    def _hour_key(ts: float) -> str:
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H")

    def _reset_counters(self, day: str) -> None:
        self._day = day
        self._events_today = 0
        self._by_severity: Counter = Counter()
        self._alerts: Dict[str, Dict[str, Any]] = {}

    def _roll_day(self) -> None:
        today = self._today()
        if today != self._day:
            self._reset_counters(today)

    def _prune(self, now: float) -> None:
        cutoff = now - self.window
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()

    def _prune_hourly(self, now: float) -> None:
        oldest = self._hour_key(now - HOURS_KEPT * 3600)
        for key in [k for k in self._hourly if k < oldest]:  # ISO keys sort chronologically
            del self._hourly[key]

    def _export_locked(self) -> Dict[str, Any]:
        return {
            "version": _STATE_VERSION,
            "day": self._day,
            "events_today": self._events_today,
            "by_severity": dict(self._by_severity),
            "alerts": {name: dict(entry) for name, entry in self._alerts.items()},
            "hourly": {key: dict(bucket) for key, bucket in self._hourly.items()},
        }

    def _take_snapshot_for_persist(self, now: float, force: bool = False) -> Optional[Dict[str, Any]]:
        """Caller holds the lock. Returns a document to write, or None."""
        if self._persist is None or not self._dirty:
            return None
        due = self._last_persist is None or (now - self._last_persist) >= self._persist_interval
        if not (force or due):
            return None
        self._last_persist = now
        self._dirty = False
        return self._export_locked()

    def _write(self, doc: Optional[Dict[str, Any]]) -> None:
        if doc is None or self._persist is None:
            return
        try:
            self._persist(doc)
        except Exception:  # noqa: BLE001 - persistence must never break ingestion
            logger.exception("Could not persist telemetry statistics")
            with self._lock:
                self._dirty = True  # retry on the next event / flush

    # ---- public API ----
    def record_event(self, severity: str, alerts: Optional[List[Dict[str, Any]]] = None) -> None:
        now = self._clock()
        with self._lock:
            self._roll_day()
            self._timestamps.append(now)
            self._prune(now)
            self._events_today += 1
            sev = (severity or "INFO").upper()
            sev = sev if sev in _SEVERITIES else "INFO"
            self._by_severity[sev] += 1
            bucket = self._hourly.setdefault(self._hour_key(now), {"events": 0, "critical": 0, "alerts": 0})
            bucket["events"] += 1
            if sev == "CRITICAL":
                bucket["critical"] += 1
            bucket["alerts"] += len(alerts or [])
            self._prune_hourly(now)
            for alert in alerts or []:
                name = str(alert.get("title") or alert.get("rule_name") or "Unnamed detection")
                entry = self._alerts.setdefault(
                    name,
                    {"name": name, "count": 0, "severity": alert.get("severity", "MEDIUM"),
                     "tactic": alert.get("mitre_tactic")},
                )
                entry["count"] += 1
            self._dirty = True
            doc = self._take_snapshot_for_persist(now)
        self._write(doc)

    def timeline(self) -> List[Dict[str, Any]]:
        """Last 24 hourly buckets, oldest first, including empty hours."""
        now = self._clock()
        with self._lock:
            return self._timeline_locked(now)

    def _timeline_locked(self, now: float) -> List[Dict[str, Any]]:
        current_hour = now - (now % 3600)
        rows: List[Dict[str, Any]] = []
        for back in range(TIMELINE_HOURS - 1, -1, -1):
            start = current_hour - back * 3600
            bucket = self._hourly.get(self._hour_key(start), {})
            rows.append({
                "hour": datetime.fromtimestamp(start, tz=timezone.utc).strftime("%Y-%m-%dT%H:00:00Z"),
                "events": bucket.get("events", 0),
                "critical": bucket.get("critical", 0),
                "alerts": bucket.get("alerts", 0),
            })
        return rows

    def snapshot(self) -> Dict[str, Any]:
        now = self._clock()
        with self._lock:
            self._roll_day()
            self._prune(now)
            in_window = len(self._timestamps)
            top = sorted(self._alerts.values(), key=lambda a: a["count"], reverse=True)[:5]
            return {
                "events_per_second": round(in_window / self.window, 2),
                "events_in_window": in_window,
                "window_seconds": self.window,
                "events_processed_today": self._events_today,
                "by_severity": {sev: self._by_severity.get(sev, 0) for sev in _SEVERITIES},
                "top_alerts": [dict(a) for a in top],
                "timeline": self._timeline_locked(now),
            }

    # ---- persistence ----
    def load_state(self, doc: Any) -> bool:
        """Adopt a saved document. Malformed or foreign data is ignored, never raised."""
        if not isinstance(doc, dict):
            return False
        now = self._clock()
        with self._lock:
            hourly = doc.get("hourly")
            if isinstance(hourly, dict):
                self._hourly = {}
                for key, bucket in hourly.items():
                    if isinstance(key, str) and len(key) == 13 and isinstance(bucket, dict):
                        self._hourly[key] = {
                            "events": _as_int(bucket.get("events")),
                            "critical": _as_int(bucket.get("critical")),
                            "alerts": _as_int(bucket.get("alerts")),
                        }
                self._prune_hourly(now)
            if doc.get("day") == self._today():
                self._reset_counters(self._today())
                self._events_today = _as_int(doc.get("events_today"))
                by_sev = doc.get("by_severity")
                if isinstance(by_sev, dict):
                    for sev in _SEVERITIES:
                        if _as_int(by_sev.get(sev)):
                            self._by_severity[sev] = _as_int(by_sev.get(sev))
                alerts = doc.get("alerts")
                if isinstance(alerts, dict):
                    for name, entry in alerts.items():
                        if isinstance(entry, dict) and _as_int(entry.get("count")):
                            self._alerts[str(name)] = {
                                "name": str(name),
                                "count": _as_int(entry.get("count")),
                                "severity": entry.get("severity", "MEDIUM"),
                                "tactic": entry.get("tactic"),
                            }
        return True

    def flush(self) -> None:
        """Write any unsaved counts now (called at API shutdown)."""
        with self._lock:
            doc = self._take_snapshot_for_persist(self._clock(), force=True)
        self._write(doc)

    def reset(self) -> None:
        with self._lock:
            self._timestamps.clear()
            self._hourly.clear()
            self._dirty = False
            self._reset_counters(self._today())


# ---- global instance, wired to the durable state store ----

STATE_DOCS: List[Dict[str, Any]] = []  # filled in place by state_store.restore_all()


def _persist_to_store(doc: Dict[str, Any]) -> None:
    from database import state_store  # imported lazily: keeps this module dependency-free

    if state_store.ENABLED and not state_store.save(STATE_NAME, [doc]):
        raise RuntimeError("state store did not accept the telemetry snapshot")


telemetry_stats = TelemetryStats(persist=_persist_to_store)


def register_persistence() -> None:
    """Tell the state store which list holds the saved telemetry document."""
    from database import state_store

    state_store.register(STATE_NAME, STATE_DOCS)


def restore_from_store() -> bool:
    """Apply the document that state_store.restore_all() loaded (call right after it)."""
    return telemetry_stats.load_state(STATE_DOCS[0]) if STATE_DOCS else False
