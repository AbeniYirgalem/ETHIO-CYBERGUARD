"""
Live telemetry statistics for the SOC dashboard.

Counts what the ingestion endpoint really receives: events per second over a
sliding window, events seen today (UTC), severity mix and the most frequent
detection alerts. Nothing here is simulated.
"""

import threading
import time
from collections import Counter, deque
from datetime import datetime, timezone
from typing import Any, Callable, Deque, Dict, List, Optional

_SEVERITIES = ("INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL")


class TelemetryStats:
    def __init__(self, window_seconds: int = 60, clock: Callable[[], float] = time.time):
        self.window = window_seconds
        self._clock = clock
        self._lock = threading.Lock()
        self._timestamps: Deque[float] = deque(maxlen=200_000)
        self._reset_counters(self._today())

    # ---- internals ----
    def _today(self) -> str:
        return datetime.fromtimestamp(self._clock(), tz=timezone.utc).strftime("%Y-%m-%d")

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

    # ---- public API ----
    def record_event(self, severity: str, alerts: Optional[List[Dict[str, Any]]] = None) -> None:
        now = self._clock()
        with self._lock:
            self._roll_day()
            self._timestamps.append(now)
            self._prune(now)
            self._events_today += 1
            sev = (severity or "INFO").upper()
            self._by_severity[sev if sev in _SEVERITIES else "INFO"] += 1
            for alert in alerts or []:
                name = str(alert.get("title") or alert.get("rule_name") or "Unnamed detection")
                entry = self._alerts.setdefault(
                    name,
                    {"name": name, "count": 0, "severity": alert.get("severity", "MEDIUM"),
                     "tactic": alert.get("mitre_tactic")},
                )
                entry["count"] += 1

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
            }

    def reset(self) -> None:
        with self._lock:
            self._timestamps.clear()
            self._reset_counters(self._today())


telemetry_stats = TelemetryStats()
