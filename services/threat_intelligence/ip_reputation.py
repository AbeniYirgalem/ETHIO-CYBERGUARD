"""
ETHIO-CYBERGUARD Threat Intelligence - IP Reputation & C2 Botnet Intelligence
"""

from typing import Dict, Any

class IPReputationService:
    """Evaluates IP addresses against known threat actors, proxies, and C2 servers."""

    MALICIOUS_IPS = {
        "185.220.101.5": {
            "threat_actor": "APT-CobaltStrike-Cluster",
            "malware": "Cobalt Strike Beacon",
            "country": "Germany (Tor Exit / Bulletproof Host)",
            "confidence": 98,
            "category": "C2 Infrastructure"
        },
        "196.188.99.12": {
            "threat_actor": "Fin-Fraud Regional Syndicate",
            "malware": "Phishing OTP Harvester",
            "country": "Ethiopia (Compromised Host)",
            "confidence": 95,
            "category": "Compromised Relay"
        }
    }

    @staticmethod
    def check_ip(ip: str) -> Dict[str, Any]:
        clean_ip = ip.strip()
        if clean_ip in IPReputationService.MALICIOUS_IPS:
            data = IPReputationService.MALICIOUS_IPS[clean_ip]
            return {
                "ip": clean_ip,
                "is_malicious": True,
                "reputation": "MALICIOUS",
                "confidence": data["confidence"],
                "threat_actor": data["threat_actor"],
                "malware": data["malware"],
                "country": data["country"]
            }
        return {
            "ip": clean_ip,
            "is_malicious": False,
            "reputation": "CLEAN",
            "confidence": 75
        }
