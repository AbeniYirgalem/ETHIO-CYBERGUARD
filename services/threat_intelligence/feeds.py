"""
ETHIO-CYBERGUARD Threat Intelligence Feeds Manager
Maintains provenance, sync health, confidence ratings, and licensing for threat intelligence sources.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone

class ThreatFeedManager:
    """Manages active threat intelligence feeds and their operational metadata."""

    FEEDS_REGISTRY = [
        {
            "feed_id": "FEED-ETH-01",
            "name": "Ethio-CERT National Threat Bulletin",
            "authority": "INSA (Information Network Security Administration)",
            "type": "National Critical Infrastructure",
            "coverage": ["Telebirr", "CBE", "Ethio Telecom", "Government Ministries"],
            "update_frequency": "Hourly",
            "confidence": 95,
            "false_positive_handling": "Multi-analyst review threshold with automated canary test",
            "license": "National CERT Authorized Threat Sharing MoU",
            "attribution": "INSA Directorate of Cyber Threat Detection",
            "last_successful_update": "2026-09-30T11:00:00Z",
            "active_indicators_count": 4820
        },
        {
            "feed_id": "FEED-FIN-02",
            "name": "Ethiopian Financial ISAC (Fin-ISAC)",
            "authority": "National Bank of Ethiopia & Banking Cyber Consortium",
            "type": "Banking & SWIFT Threat Intel",
            "coverage": ["CBE", "Awash", "Dashen", "Abyssinia", "Zemen", "Chapa"],
            "update_frequency": "Real-time SSE / Webhook",
            "confidence": 98,
            "false_positive_handling": "Bank CISO dual-authorization for SWIFT/ATM blocking lists",
            "license": "Interbank SOC Memorandum of Understanding",
            "attribution": "Ethiopian Banking Association Cyber Working Group",
            "last_successful_update": "2026-09-30T11:15:00Z",
            "active_indicators_count": 1280
        },
        {
            "feed_id": "FEED-GLB-03",
            "name": "AbuseIPDB & AlienVault OTX Curated Feed",
            "authority": "Global Open Threat Exchange",
            "type": "Global IP Reputation & C2 Botnets",
            "coverage": ["Cobalt Strike", "Emotet", "Tor Exit Nodes", "Brute Force Subnets"],
            "update_frequency": "Every 15 minutes",
            "confidence": 90,
            "false_positive_handling": "Confidence threshold filtering (> 80% consensus)",
            "license": "Open Threat Community License",
            "attribution": "AbuseIPDB / AT&T Cybersecurity",
            "last_successful_update": "2026-09-30T11:10:00Z",
            "active_indicators_count": 89400
        }
    ]

    @classmethod
    def get_all_feeds(cls) -> List[Dict[str, Any]]:
        return cls.FEEDS_REGISTRY

    @classmethod
    def get_feed_by_id(cls, feed_id: str) -> Dict[str, Any]:
        return next((f for f in cls.FEEDS_REGISTRY if f["feed_id"] == feed_id), None)
