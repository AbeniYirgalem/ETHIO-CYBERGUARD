"""
ETHIO-CYBERGUARD Dashboard & Observability Router
Live SOC overview numbers, calculated from the real incident, SOAR and telemetry stores.
Every number is limited to the signed-in user's organization; SUPER_ADMIN sees the national total.
Supports /api/dashboard/stats and /api/v1/stats/overview.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from services.ingestion.pipeline import ingestion_pipeline
from services.security.tenancy import is_global, org_of, scope
from services.telemetry.response_metrics import compute_response_metrics
from services.telemetry.stats import telemetry_registry, telemetry_stats
from services.websocket.manager import ws_manager

from ..dependencies import get_current_user
from .incidents import INCIDENTS_STORE
from .response import ACTIONS_STORE, AUDIT_LOG_STORE

router = APIRouter(tags=["SOC Dashboard & Analytics"])

_SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}


def _active_incidents(user: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [i for i in scope(user, INCIDENTS_STORE) if str(i.get("status", "")).upper() != "CLOSED"]


@router.get("/api/dashboard/stats")
@router.get("/api/v1/stats/overview")
def get_dashboard_stats(_user: Dict[str, Any] = Depends(get_current_user)):
    national = is_global(_user)
    org_id = org_of(_user)
    active = _active_incidents(_user)

    def count(severity: str) -> int:
        return sum(1 for i in active if str(i.get("severity", "")).upper() == severity)

    response = compute_response_metrics(scope(_user, INCIDENTS_STORE))
    pending = sum(1 for a in scope(_user, ACTIONS_STORE) if a.get("status") == "PENDING_APPROVAL")
    telemetry = telemetry_stats.snapshot() if national else telemetry_registry.for_org(org_id).snapshot()

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
        severity = str(inc.get("severity", "")).upper()
        profile = sector_profiles.setdefault(
            sector, {"active_alerts": 0, "critical": 0, "high": 0, "max_severity": "INFO"}
        )
        profile["active_alerts"] += 1
        if severity == "CRITICAL":
            profile["critical"] += 1
        elif severity == "HIGH":
            profile["high"] += 1
        if _SEVERITY_RANK.get(severity, 0) > _SEVERITY_RANK.get(profile["max_severity"], 0):
            profile["max_severity"] = severity

    eps = telemetry["events_per_second"]
    if national:
        pipeline_health = f"{eps} eps, queue depth {len(ingestion_pipeline.queue)}"
        stream_clients = ws_manager.get_active_count()
    else:
        # The shared queue and the total socket count describe other organizations too.
        pipeline_health = f"{eps} eps"
        stream_clients = ws_manager.get_tenant_count(org_id)
    return {
        "tenant": {"org_id": org_id, "scope": "national" if national else "organization"},
        "metrics": {
            "events_per_second": eps,
            "events_processed_today": telemetry["events_processed_today"],
            "active_incidents": len(active),
            "critical_alerts": count("CRITICAL"),
            "high_risk_alerts": count("HIGH"),
            "medium_risk_alerts": count("MEDIUM"),
            "pending_approvals": pending,
            "audit_entries": len(scope(_user, AUDIT_LOG_STORE)),
            "assets_monitored": len({i.get("affected_asset") for i in scope(_user, INCIDENTS_STORE) if i.get("affected_asset")}),
            # Measured from incident history; null until an incident reaches the milestone.
            "mean_time_to_detect_minutes": response["mean_time_to_detect_minutes"],
            "mean_time_to_respond_minutes": response["mean_time_to_respond_minutes"],
        },
        "response_metrics": {
            "mttd_samples": response["mttd_samples"],
            "mttr_samples": response["mttr_samples"],
        },
        "telemetry": {
            "window_seconds": telemetry["window_seconds"],
            "events_in_window": telemetry["events_in_window"],
            "by_severity": telemetry["by_severity"],
        },
        # Hourly history for the Overview timeline (UTC hours, oldest first, last 24 h).
        "timeline": telemetry["timeline"],
        "top_threats": top_threats,
        "sector_profiles": sector_profiles,
        "system_health": {
            "ingestion_pipeline": pipeline_health,
            "live_stream_clients": stream_clients,
        },
    }
