"""
ETHIO-CYBERGUARD Threat Intelligence Router
Provides indicator lookups (IOC query), threat feed status, STIX 2.1 bundle export, and Ethiopian infrastructure target intelligence.
Supports /api/threat-intelligence and /api/v1/threat-intelligence.
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.threat_intelligence.ioc_database import ThreatIntelDatabase
from services.threat_intelligence.feed_manager import feed_manager

router = APIRouter(tags=["Threat Intelligence & IOCs"])
db = ThreatIntelDatabase()

class ImportIndicatorRequest(BaseModel):
    indicator: str
    ioc_type: str = "ipv4-addr" # ipv4-addr, domain-name, url, file-hash
    severity: str = "HIGH"
    source: str = "Custom Threat Feed"
    confidence: int = 85
    expires_in_days: int = 90

@router.get("/api/threat-intelligence")
@router.get("/api/v1/threat-intelligence")
def list_threat_indicators(
    ioc_type: Optional[str] = Query(None, alias="type"),
    reputation: Optional[str] = None
):
    results = list(db.DEFAULT_IOCS.values())
    if ioc_type:
        results = [i for i in results if i["type"].upper() == ioc_type.upper()]
    if reputation:
        results = [i for i in results if i["reputation"].upper() == reputation.upper()]
    return {"total": len(results), "indicators": results}

@router.get("/api/threat-intelligence/ioc/{ioc}")
@router.get("/api/v1/threat-intelligence/ioc/{ioc}")
def lookup_ioc(ioc: str):
    record = db.lookup(ioc)
    if not record:
        return {
            "indicator": ioc,
            "reputation": "UNKNOWN",
            "confidence": 0,
            "message": "Indicator not currently observed in active malicious feeds.",
            "is_malicious": False
        }
    return {
        "indicator": ioc,
        "is_malicious": record.get("reputation") == "MALICIOUS",
        "data": record
    }

@router.get("/api/threat-intelligence/stix")
@router.get("/api/v1/threat-intelligence/stix")
def export_stix_bundle():
    """Exports active threat indicators as standard STIX 2.1 JSON bundle for SIEM/TAXII integration."""
    return feed_manager.export_stix_bundle()

@router.post("/api/threat-intelligence/import", status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/threat-intelligence/import", status_code=status.HTTP_201_CREATED)
def import_indicator(payload: ImportIndicatorRequest):
    """Ingests indicator with deduplication, confidence scores, and expiration timestamps."""
    record = feed_manager.import_indicator(
        indicator=payload.indicator,
        ioc_type=payload.ioc_type,
        severity=payload.severity,
        source=payload.source,
        confidence=payload.confidence,
        expires_in_days=payload.expires_in_days
    )
    return {
        "status": "IMPORTED",
        "message": f"Indicator {payload.indicator} ingested into active threat intel database.",
        "record": record
    }

@router.get("/api/threat-intelligence/feeds")
@router.get("/api/v1/threat-intelligence/feeds")
def list_threat_feeds():
    """Documents exact sources, update frequencies, confidence, and licenses for national & global feeds."""
    return {
        "feeds": [
            {
                "feed_id": "FEED-ETH-01",
                "name": "Ethio-CERT National Threat Bulletin",
                "authority": "INSA (Information Network Security Administration)",
                "type": "National Critical Infrastructure",
                "coverage": ["Telebirr", "CBE", "Ethio Telecom", "Government Ministries"],
                "frequency": "Hourly",
                "confidence_score": 95,
                "license": "National CERT Authorized Sharing",
                "attribution": "INSA Cyber Incident Response Directorate"
            },
            {
                "feed_id": "FEED-MISP-FIN",
                "name": "Global Financial Services ISAC / MISP Feed",
                "authority": "FS-ISAC",
                "type": "SWIFT & Core Banking Indicators",
                "coverage": ["Banking Trojans", "SWIFT Wire Fraud", "Cobalt Strike C2"],
                "frequency": "Realtime",
                "confidence_score": 92,
                "license": "TLP:AMBER ISAC Member Agreement",
                "attribution": "FS-ISAC Threat Intelligence Exchange"
            },
            {
                "feed_id": "FEED-ABUSE-CH",
                "name": "URLhaus & MalwareBazaar Threat Tracker",
                "authority": "Abuse.ch",
                "type": "Malware Stagers & Phishing Payloads",
                "coverage": ["Payload Hashes", "Phishing URLs", "Drop Sites"],
                "frequency": "Every 15 minutes",
                "confidence_score": 90,
                "license": "CC0 Public Domain",
                "attribution": "Abuse.ch Community Research Project"
            }
        ]
    }
