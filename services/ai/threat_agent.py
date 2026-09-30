"""
AI Agent 2: Threat Intelligence Agent
Correlates events and incidents with known indicators, threat actors, and campaign intelligence.
"""

from typing import Dict, Any, List

class ThreatIntelligenceAgent:
    def __init__(self, model_client=None):
        self.model_client = model_client

    def enrich(self, indicators: List[str]) -> Dict[str, Any]:
        results = []
        for ind in indicators:
            if ind == "185.220.101.5":
                results.append({
                    "indicator": ind,
                    "type": "IPV4",
                    "reputation": "MALICIOUS",
                    "confidence": 0.96,
                    "first_seen": "2026-04-12",
                    "threat_actor": "APT-CobaltStrike-Actor",
                    "associated_malware": "Cobalt Strike TeamServer Beacon",
                    "campaign": "Operation Red Nile Targeting African Financial Systems",
                    "geo": "Germany / Tor Exit Relay Node",
                    "related_incidents": ["INC-00021", "INC-00042"]
                })
            elif "update-winsec-cloud" in ind:
                results.append({
                    "indicator": ind,
                    "type": "DOMAIN",
                    "reputation": "MALICIOUS",
                    "confidence": 0.92,
                    "threat_actor": "Fin-Threat Cluster",
                    "campaign": "Executive Spear-phishing Q3",
                    "related_incidents": ["INC-00019"]
                })
            else:
                results.append({
                    "indicator": ind,
                    "type": "UNKNOWN",
                    "reputation": "BENIGN",
                    "confidence": 0.70
                })

        return {
            "agent": "ThreatIntelligenceAgent",
            "matches_count": len([r for r in results if r.get("reputation") == "MALICIOUS"]),
            "enrichments": results,
            "threat_landscape_summary": "Indicators correlate with known advanced persistent threats targeting regional financial infrastructure."
        }
