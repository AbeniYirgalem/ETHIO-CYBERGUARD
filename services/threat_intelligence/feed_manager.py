"""
Threat Intelligence Feed Manager with STIX 2.1 & MISP Compatibility for ETHIO-CYBERGUARD
Handles indicator ingestion, expiration, source attribution, deduplication, and STIX serialization.
"""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

class ThreatFeedManager:
    def __init__(self):
        self.indicators: Dict[str, Dict[str, Any]] = {
            "185.220.101.5": {
                "indicator": "185.220.101.5",
                "ioc_type": "ipv4-addr",
                "threat_actor": "CobaltStrike-Actor",
                "severity": "CRITICAL",
                "confidence": 96,
                "source": "Ethio-CERT",
                "description": "Known Cobalt Strike C2 beacon endpoint targeting Ethiopian banking infrastructure",
                "created_at": "2026-04-12T00:00:00Z",
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
            },
            "update-winsec-cloud.com": {
                "indicator": "update-winsec-cloud.com",
                "ioc_type": "domain-name",
                "threat_actor": "Fin-Threat-Cluster",
                "severity": "CRITICAL",
                "confidence": 92,
                "source": "MISP-Financial-Feed",
                "description": "Empire C2 staging domain disguised as security updates",
                "created_at": "2026-08-19T00:00:00Z",
                "expires_at": (datetime.now(timezone.utc) + timedelta(days=60)).isoformat()
            }
        }

    def import_indicator(self, indicator: str, ioc_type: str, severity: str, source: str, confidence: int = 80, expires_in_days: int = 90) -> Dict[str, Any]:
        """Ingests indicator with deduplication and expiration."""
        now = datetime.now(timezone.utc)
        record = {
            "indicator": indicator.strip(),
            "ioc_type": ioc_type,
            "severity": severity.upper(),
            "confidence": min(100, max(1, confidence)),
            "source": source,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=expires_in_days)).isoformat(),
            "is_expired": False
        }
        self.indicators[indicator.strip()] = record
        return record

    def export_stix_bundle(self) -> Dict[str, Any]:
        """Serializes current threat indicators into standard STIX 2.1 JSON bundle."""
        bundle_id = f"bundle--{uuid.uuid4()}"
        objects = []

        # 1. Identity object (Producer)
        identity_id = "identity--ecg-ethio-cert-national-soc"
        objects.append({
            "type": "identity",
            "spec_version": "2.1",
            "id": identity_id,
            "created": "2026-01-01T00:00:00.000Z",
            "modified": "2026-01-01T00:00:00.000Z",
            "name": "ETHIO-CYBERGUARD National SOC Threat Intel",
            "identity_class": "organization"
        })

        # 2. Indicator objects
        for val, ind in self.indicators.items():
            stix_ind_id = f"indicator--{uuid.uuid5(uuid.NAMESPACE_DNS, val)}"
            pattern = f"[{ind['ioc_type']}:value = '{val}']"
            objects.append({
                "type": "indicator",
                "spec_version": "2.1",
                "id": stix_ind_id,
                "created": ind.get("created_at"),
                "modified": ind.get("created_at"),
                "name": f"Malicious {ind['ioc_type']} - {val}",
                "description": ind.get("description", "National SOC threat indicator"),
                "indicator_types": ["malicious-activity"],
                "pattern": pattern,
                "pattern_type": "stix",
                "valid_from": ind.get("created_at"),
                "valid_until": ind.get("expires_at"),
                "confidence": ind.get("confidence", 85),
                "created_by_ref": identity_id
            })

        return {
            "type": "bundle",
            "id": bundle_id,
            "objects": objects
        }

feed_manager = ThreatFeedManager()
