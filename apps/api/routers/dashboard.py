"""
ETHIO-CYBERGUARD Dashboard & Observability Router
Live SOC overview numbers, calculated from the real incident, SOAR and telemetry stores.
Supports /api/dashboard/stats and /api/v1/stats/overview.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from services.ingestion.pipeline import ingestion_pipeline
from services.telemetry.stats import telemetry_stats
from services.websocket.manager import ws_manager

from ..dependencies import get_current_user
from .incidents import INCIDENTS_STORE
from .response import ACTIONS_STORE, AUDIT_LOG_STORE

router = APIRouter(tags=["SOC Dashboard & Analytics"])

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}


def _active_incidents() -> List[Dict[str, Any]]:
    return [i for i in INCIDENTS_STORE if str(i.get("status", "")).upper() != "CLOSED"]


@router.get("/api/dashboard/stats")
@router.get("/api/v1/stats/overview")
def get_dashboard_stats(_user: Dict[str, Any] = Depends(get_current_user)):
    active = _active_incidents()

    def count(severity: str) -> int:
        return sum(1 for i in active if str(i.get("severity", "")).upper() == severity)

    pending = sum(1 for a in ACTIONS_STORE if a.get("status") == "PENDING_APPROVAL")
    telemetry = telemetry_stats.snapshot()

    # Top threats: detection alerts actually seen; before any telemetry, the open incidents.
    if telemetry["top_alerts"]:
        top_threats = [
            {"name": a["name"], "count": a["count"], "severity": a["severity"],
             "tactic": a.get("tactic"), "source": "detections"}
            for a in telemetry["top_alerts"]
        ]
    else:
        ranked = sorted(
            active, key=lambda i: _SEVERITY_RANK.get(str(i.get("severity", "")).upper(), 0), reverse=True
        )
        top_threats = [
            {"name": i.get("title"), "count": 1, "severity": i.get("severity"),
             "tactic": None, "source": "incidents"}
            for i in ranked[:5]
        ]

    sector_profiles: Dict[str, Dict[str, Any]] = {}
    for inc in active:
        sector = inc.get("sector") or "Unassigned"
        profile = sector_profiles.setdefault(sector, {"active_alerts": 0})
        profile["active_alerts"] += 1

    eps = telemetry["events_per_second"]
    return {
        "metrics": {
            "events_per_second": eps,
            "events_processed_today": telemetry["events_processed_today"],
            "active_incidents": len(active),
            "critical_alerts": count("CRITICAL"),
            "high_risk_alerts": count("HIGH"),
            "medium_risk_alerts": count("MEDIUM"),
            "pending_approvals": pending,
            "audit_entries": len(AUDIT_LOG_STORE),
            "assets_monitored": len({i.get("affected_asset") for i in INCIDENTS_STORE if i.get("affected_asset")}),
            # Not measured yet: reported as null instead of an invented figure.
            "mean_time_to_detect_minutes": None,
            "mean_time_to_respond_minutes": None,
        },
        "telemetry": {
            "window_seconds": telemetry["window_seconds"],
            "events_in_window": telemetry["events_in_window"],
            "by_severity": telemetry["by_severity"],
        },
        "top_threats": top_threats,
        "sector_profiles": sector_profiles,
        "system_health": {
            "ingestion_pipeline": f"{eps} eps, queue depth {len(ingestion_pipeline.queue)}",
            "live_stream_clients": ws_manager.get_active_count(),
        },
    }
