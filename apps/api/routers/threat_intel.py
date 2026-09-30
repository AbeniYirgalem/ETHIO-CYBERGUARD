"""
ETHIO-CYBERGUARD Threat Intelligence Router
Provides indicator lookups (IOC query), threat feed status, and Ethiopian infrastructure target intelligence.
Supports /api/threat-intelligence and /api/v1/threat-intelligence.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

from services.threat_intelligence.ioc_database import ThreatIntelDatabase

router = APIRouter(tags=["Threat Intelligence & IOCs"])
db = ThreatIntelDatabase()

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
                "last_sync": "2026-09-30T11:00:00Z",
                "status": "ONLINE"
            },
            {
                "feed_id": "FEED-FIN-02",
                "name": "Ethiopian Financial ISAC (Fin-ISAC)",
                "authority": "National Bank of Ethiopia & Banking Cyber Consortium",
                "type": "Banking & SWIFT Threat Intel",
                "coverage": ["CBE", "Awash", "Dashen", "Abyssinia", "Zemen", "Chapa"],
                "frequency": "Real-time SSE",
                "confidence_score": 98,
                "license": "Interbank SOC Memorandum of Understanding",
                "last_sync": "2026-09-30T11:15:00Z",
                "status": "ONLINE"
            },
            {
                "feed_id": "FEED-GLB-03",
                "name": "AbuseIPDB & AlienVault OTX Curated Feed",
                "authority": "Global Open Threat Exchange",
                "type": "Global IP Reputation & C2 Botnets",
                "coverage": ["Cobalt Strike", "Emotet", "Tor Exit Nodes", "Brute Force Subnets"],
                "frequency": "Every 15 minutes",
                "confidence_score": 90,
                "license": "Open Threat Community License",
                "last_sync": "2026-09-30T11:10:00Z",
                "status": "ONLINE"
            }
        ]
    }

@router.get("/api/threat-intelligence/entities")
def list_ethiopian_entities():
    """Lists Ethiopian organizations, official domains, and typical threat vectors."""
    return {
        "entities": [
            {"brand": "telebirr", "organization": "Ethio Telecom / Telebirr", "official_domains": ["telebirr.et", "ethiotelecom.et"], "sector": "Telecom / Fintech"},
            {"brand": "cbe", "organization": "Commercial Bank of Ethiopia", "official_domains": ["combanketh.et", "cbe.com.et"], "sector": "Banking"},
            {"brand": "awash", "organization": "Awash Bank", "official_domains": ["awashbank.com"], "sector": "Banking"},
            {"brand": "dashen", "organization": "Dashen Bank", "official_domains": ["dashenbanksc.com"], "sector": "Banking"},
            {"brand": "chapa", "organization": "Chapa Financial Technologies", "official_domains": ["chapa.co"], "sector": "Payment Gateway"},
            {"brand": "safaricom", "organization": "Safaricom Ethiopia / M-PESA", "official_domains": ["safaricom.et"], "sector": "Telecom / Fintech"},
            {"brand": "insa", "organization": "INSA Cyber Directorate", "official_domains": ["insa.gov.et"], "sector": "Government / Defense"}
        ]
    }
