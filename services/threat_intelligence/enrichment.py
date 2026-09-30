"""
ETHIO-CYBERGUARD Threat Intelligence - Pipeline Enrichment Service
Enriches normalized ECS events with threat reputation, geolocation, and national entity context.
"""

from typing import Dict, Any, Optional
from .ioc_database import ThreatIntelDatabase
from .ethiopian_entities import get_entity_by_domain

class EventEnricher:
    """Enriches security events with threat intelligence observables."""

    def __init__(self, db: Optional[ThreatIntelDatabase] = None):
        self.db = db or ThreatIntelDatabase()

    def enrich_event(self, ecs_event: Dict[str, Any]) -> Dict[str, Any]:
        enriched = dict(ecs_event)
        threat_intel = {"is_flagged": False, "indicators": []}

        # Check destination IP
        dest_ip = ecs_event.get("destination", {}).get("ip")
        if dest_ip:
            rec = self.db.lookup_indicator(dest_ip)
            if rec and rec.get("reputation") == "MALICIOUS":
                threat_intel["is_flagged"] = True
                threat_intel["indicators"].append({
                    "observable": dest_ip,
                    "reputation": "MALICIOUS",
                    "actor": rec.get("threat_actor"),
                    "malware": rec.get("malware"),
                    "confidence": rec.get("confidence", 90)
                })

        # Check domain in network or process
        domain = ecs_event.get("destination", {}).get("domain")
        if domain:
            rec = self.db.lookup_indicator(domain)
            if rec and rec.get("reputation") == "MALICIOUS":
                threat_intel["is_flagged"] = True
                threat_intel["indicators"].append({
                    "observable": domain,
                    "reputation": "MALICIOUS",
                    "actor": rec.get("threat_actor"),
                    "confidence": rec.get("confidence", 90)
                })

        enriched["threat_intelligence"] = threat_intel
        return enriched
