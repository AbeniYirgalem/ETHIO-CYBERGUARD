"""
ETHIO-CYBERGUARD Incident Builder
Combines individual multi-stage alerts across the attack killchain into a cohesive unified incident.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone
import uuid
from .timeline import TimelineBuilder
from .attack_graph import AttackGraphGenerator
from .entity_resolution import EntityResolver

class IncidentBuilder:
    """Builds unified multi-stage incidents from related alerts."""

    @staticmethod
    def build_from_chain(
        chain_events: List[Dict[str, Any]],
        title: str = "Correlated Multi-Stage Intrusion",
        sector: str = "Banking"
    ) -> Dict[str, Any]:
        resolution = EntityResolver.link_entities(chain_events)
        timeline = TimelineBuilder.construct_timeline(chain_events)
        attack_graph = AttackGraphGenerator.build_graph(
            compromised_host=resolution["primary_host"],
            victim_user=resolution["primary_user"]
        )

        return {
            "id": str(uuid.uuid4()),
            "incident_number": f"INC-{abs(hash(title)) % 90000 + 10000}",
            "title": title,
            "severity": "CRITICAL" if any(e.get("severity") == "CRITICAL" for e in chain_events) else "HIGH",
            "status": "INVESTIGATING",
            "risk_score": 92 if any(e.get("severity") == "CRITICAL" for e in chain_events) else 75,
            "affected_asset": resolution["primary_host"],
            "assigned_analyst": "Dawit Mengistu",
            "department": "Core Infrastructure",
            "sector": sector,
            "first_seen": timeline[0]["time"] if timeline else datetime.now(timezone.utc).isoformat(),
            "last_activity": timeline[-1]["time"] if timeline else datetime.now(timezone.utc).isoformat(),
            "timeline": timeline,
            "attack_graph": attack_graph,
            "correlated_events_count": len(chain_events)
        }
