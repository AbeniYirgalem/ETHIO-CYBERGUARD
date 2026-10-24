"""Measured SOC response times (MTTD / MTTR) calculated from real incident records.

Definitions (kept deliberately simple and documented, because these numbers are shown to executives):

* MTTD - mean minutes from the incident's ``first_seen`` time to the first time an analyst acted
  on it (the earliest history entry that moves it out of ``NEW``). It measures how long a detected
  incident waited before the SOC picked it up.
* MTTR - mean minutes from ``first_seen`` to the first transition into ``CONTAINED`` or ``CLOSED``.

An incident that never reached the milestone is left out of that average. When no incident has
reached it, the value is ``None`` ("not measured yet"), never an invented number.
Negative or unreadable durations (clock skew, bad data) are ignored.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Optional

_RESPONSE_STATUSES = {"CONTAINED", "CLOSED"}


def parse_time(value: Any) -> Optional[datetime]:
    """Parse the timestamp formats used in the incident store. Naive times are treated as UTC."""
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str) and value.strip():
        text = value.strip()
        if text.endswith(("Z", "z")):
            text = text[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
    else:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _minutes_between(start: Optional[datetime], end: Optional[datetime]) -> Optional[float]:
    if start is None or end is None:
        return None
    seconds = (end - start).total_seconds()
    return seconds / 60.0 if seconds >= 0 else None


def _first_time(history: Iterable[Dict[str, Any]], accept) -> Optional[datetime]:
    times = [
        parse_time(entry.get("timestamp"))
        for entry in history
        if isinstance(entry, dict) and accept(str(entry.get("new_status") or "").upper())
    ]
    times = [t for t in times if t is not None]
    return min(times) if times else None


def compute_response_metrics(incidents: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    detect, respond = [], []
    for inc in incidents:
        start = parse_time(inc.get("first_seen"))
        history = inc.get("history") or []
        if start is None or not isinstance(history, list):
            continue
        d = _minutes_between(start, _first_time(history, lambda s: bool(s) and s != "NEW"))
        r = _minutes_between(start, _first_time(history, lambda s: s in _RESPONSE_STATUSES))
        if d is not None:
            detect.append(d)
        if r is not None:
            respond.append(r)

    def mean(values):
        return round(sum(values) / len(values), 1) if values else None

    return {
        "mean_time_to_detect_minutes": mean(detect),
        "mean_time_to_respond_minutes": mean(respond),
        "mttd_samples": len(detect),
        "mttr_samples": len(respond),
    }
