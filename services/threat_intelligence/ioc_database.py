"""
ETHIO-CYBERGUARD - Threat Intelligence IOC Database & Lookup Service
Aggregates indicators of compromise (IP, Domain, URL, SHA256) with national & global reputation.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone


class ThreatIntelDatabase:
    """
    In-memory and persistent Threat Intelligence Database.
    Correlates observables with known malicious actors, malware families, and confidence scores.
    """

    DEFAULT_IOCS: Dict[str, Dict[str, Any]] = {
        "185.220.101.5": {
            "indicator": "185.220.101.5",
            "type": "IPV4",
            "reputation": "MALICIOUS",
            "confidence": 98,
            "threat_actor": "APT-CobaltStrike-Cluster",
            "malware": "Cobalt Strike Beacon",
            "country": "Germany",
            "source": "Ethio-CERT Feed / AbuseIPDB",
            "first_seen": "2026-04-12"
        },
        "196.188.99.12": {
            "indicator": "196.188.99.12",
            "type": "IPV4",
            "reputation": "MALICIOUS",
            "confidence": 95,
            "threat_actor": "Fin-Fraud Regional Syndicate",
            "malware": "Phishing OTP Harvester",
            "country": "Ethiopia (Host Hijacked)",
            "source": "INSA Cyber Threat Advisory",
            "first_seen": "2026-09-28"
        },
        "telebirr-bonus.xyz": {
            "indicator": "telebirr-bonus.xyz",
            "type": "DOMAIN",
            "reputation": "MALICIOUS",
            "confidence": 99,
            "threat_actor": "Mobile Money Fraudsters",
            "malware": "Telebirr Credential Stealer",
            "country": "Unknown (Privacy Guard)",
            "source": "Ethio Telecom CERT Blacklist",
            "first_seen": "2026-09-29"
        },
        "cbe-ebanking-auth.net": {
            "indicator": "cbe-ebanking-auth.net",
            "type": "DOMAIN",
            "reputation": "MALICIOUS",
            "confidence": 97,
            "threat_actor": "Bank Phishing Campaign",
            "malware": "CBE Internet Banking Clone",
            "country": "Seychelles",
            "source": "Commercial Bank Security Center",
            "first_seen": "2026-09-27"
        },
        "update-winsec-cloud.com": {
            "indicator": "update-winsec-cloud.com",
            "type": "DOMAIN",
            "reputation": "MALICIOUS",
            "confidence": 92,
            "threat_actor": "Lazarus-Linked Cluster",
            "malware": "Empire C2 Stager",
            "country": "Russia",
            "source": "Global MISP Community",
            "first_seen": "2026-08-19"
        },
        "7d4b29c9103a89e924a2734ef0350d24fb4b3e6480c55ffc06a928db6928e469": {
            "indicator": "7d4b29c9103a89e924a2734ef0350d24fb4b3e6480c55ffc06a928db6928e469",
            "type": "SHA256",
            "reputation": "MALICIOUS",
            "confidence": 100,
            "threat_actor": "Lazarus Group",
            "malware": "Mimikatz LSASS Infiltrator",
            "country": "North Korea",
            "source": "CISA KEV / VirusTotal 68/70",
            "first_seen": "2026-01-10"
        }
    }

    def __init__(self):
        self.iocs = dict(self.DEFAULT_IOCS)

    def lookup_indicator(self, value: str) -> Optional[Dict[str, Any]]:
        """Look up an observable value (IP, domain, hash)."""
        clean_val = value.strip().lower()
        # Direct match
        if clean_val in self.iocs:
            return self.iocs[clean_val]

        # Case-insensitive / domain suffix matching
        for k, v in self.iocs.items():
            if k.lower() == clean_val or clean_val.endswith(f".{k.lower()}"):
                return v

        return None

    def add_indicator(self, indicator: str, ioc_type: str, reputation: str, confidence: int, threat_actor: str, malware: str) -> None:
        self.iocs[indicator.strip().lower()] = {
            "indicator": indicator,
            "type": ioc_type.upper(),
            "reputation": reputation.upper(),
            "confidence": confidence,
            "threat_actor": threat_actor,
            "malware": malware,
            "country": "Unknown",
            "source": "SOC Analyst Manual Entry",
            "first_seen": datetime.now(timezone.utc).strftime("%Y-%m-%d")
        }

    def get_all_indicators(self) -> List[Dict[str, Any]]:
        return list(self.iocs.values())
