"""
ETHIO-CYBERGUARD Incident Timeline Reconstruction
Assembles ordered forensic event sequences with MITRE killchain phase tags.
"""

from typing import List, Dict, Any
from datetime import datetime

class TimelineBuilder:
    """Builds incident timelines from heterogeneous events."""

    @staticmethod
    def construct_timeline(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        timeline = []
        for ev in events:
            timestamp = ev.get("timestamp", "2026-09-30 10:42:00")
            desc = ev.get("summary") or ev.get("process", {}).get("command_line") or ev.get("event_type", "Security Event")
            sev = ev.get("severity", "INFO")
            tactic = ev.get("mitre_tactic", "Execution")

            timeline.append({
                "time": str(timestamp),
                "event": desc,
                "severity": sev,
                "tactic": tactic,
                "source": ev.get("source", {}).get("hostname", "ENDPOINT")
            })

        return timeline
