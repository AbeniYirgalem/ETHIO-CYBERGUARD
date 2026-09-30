"""
ETHIO-CYBERGUARD Attack Graph Generator
Constructs interactive node-edge topological attack graphs representing adversary progression.
"""

from typing import Dict, Any, List

class AttackGraphGenerator:
    """Generates graph structures linking adversaries, assets, artifacts, and external C2."""

    @staticmethod
    def build_graph(
        attacker_origin: str = "External Threat Actor",
        phishing_domain: str = "telebirr-bonus.xyz",
        victim_user: str = "dawit.mengistu",
        compromised_host: str = "SERVER-04",
        c2_ip: str = "185.220.101.5"
    ) -> Dict[str, Any]:
        nodes = [
            {"id": "node_attacker", "label": attacker_origin, "type": "actor", "status": "malicious", "icon": "skull"},
            {"id": "node_phish", "label": phishing_domain, "type": "infrastructure", "status": "malicious", "icon": "globe"},
            {"id": "node_user", "label": victim_user, "type": "identity", "status": "targeted", "icon": "user"},
            {"id": "node_host", "label": compromised_host, "type": "endpoint", "status": "compromised", "icon": "server"},
            {"id": "node_powershell", "label": "Obfuscated PowerShell (PID 4812)", "type": "process", "status": "executed", "icon": "terminal"},
            {"id": "node_c2", "label": f"C2 Server {c2_ip}", "type": "infrastructure", "status": "blocked", "icon": "network"}
        ]

        edges = [
            {"source": "node_attacker", "target": "node_phish", "label": "T1583 Infrastructure Setup"},
            {"source": "node_phish", "target": "node_user", "label": "T1566 Spearphishing Email"},
            {"source": "node_user", "target": "node_host", "label": "T1078 Valid Accounts"},
            {"source": "node_host", "target": "node_powershell", "label": "T1059.001 PowerShell Execution"},
            {"source": "node_powershell", "target": "node_c2", "label": "T1071.001 C2 Web Beaconing"}
        ]

        return {"nodes": nodes, "edges": edges}
