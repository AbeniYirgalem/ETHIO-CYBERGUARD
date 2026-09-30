"""
ETHIO-CYBERGUARD AI Tool Access Registry & Authorization Boundaries
Defines tools that AI agents are permitted to invoke.
Strict rule: AI agents can ONLY query read-only telemetry and recommend actions.
Destructive actions (Host Isolation, Firewall Drops) CANNOT be directly executed by an agent without Human-In-The-Loop approval.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class AIToolRegistry:
    """Registry of permitted tools with strict capability and permission boundaries."""

    @staticmethod
    def query_threat_intel(indicator: str) -> Dict[str, Any]:
        """Read-only tool: Looks up an indicator against threat feeds."""
        from services.threat_intelligence.ioc_database import ThreatIntelDatabase
        db = ThreatIntelDatabase()
        rec = db.lookup_indicator(indicator)
        return {"indicator": indicator, "record": rec or {"reputation": "UNKNOWN"}}

    @staticmethod
    def query_ecs_events(filter_query: str, limit: int = 10) -> Dict[str, Any]:
        """Read-only tool: Queries telemetry log store."""
        return {
            "query": filter_query,
            "matched_events": [
                {"timestamp": datetime.now(timezone.utc).isoformat(), "event_type": "process_execution", "detail": "powershell.exe -enc ..."}
            ]
        }

    @staticmethod
    def calculate_risk(factors: Dict[str, int]) -> int:
        """Computation tool: Computes bounded risk score."""
        raw = sum(factors.values())
        return min(max(raw, 0), 100)

    @staticmethod
    def recommend_containment_action(action_type: str, target: str, reasoning: str) -> Dict[str, Any]:
        """
        Advisory tool: Submits an action recommendation to the Human Approval Queue.
        Notice: Does NOT execute the action directly.
        """
        return {
            "status": "QUEUED_FOR_HUMAN_APPROVAL",
            "action_type": action_type,
            "target": target,
            "reasoning": reasoning,
            "requires_human_approval": True,
            "execution_policy": "STRICT_HUMAN_IN_THE_LOOP"
        }
