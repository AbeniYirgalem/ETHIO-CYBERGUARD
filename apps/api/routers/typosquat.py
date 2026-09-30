"""
ETHIO-CYBERGUARD Typosquatting & Brand Defense Router
Detects look-alike domains, homoglyphs, and combotypes targeting Ethiopian organizations.
Supports both POST and GET on /api/typosquat/scan and /api/v1/typosquat/scan.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from services.typosquat.domain_monitor import TyposquatMonitor

router = APIRouter(tags=["Typosquatting & Brand Defense"])
monitor = TyposquatMonitor()

class TyposquatScanRequest(BaseModel):
    target: str = "telebirr.et"
    limit: Optional[int] = 40

@router.post("/api/typosquat/scan")
@router.post("/api/v1/typosquat/scan")
def scan_typosquats_post(payload: TyposquatScanRequest):
    return monitor.scan_domain(domain_or_brand=payload.target, limit=payload.limit or 40)

@router.get("/api/typosquat/scan")
@router.get("/api/v1/typosquat/scan")
def scan_typosquats_get(target: str = "telebirr.et", limit: int = 40):
    return monitor.scan_domain(domain_or_brand=target, limit=limit)

@router.get("/api/typosquat/brands")
def list_protected_brands():
    return {
        "brands": [
            {"brand": "telebirr.et", "name": "Telebirr Mobile Money", "active_spoofs_detected": 14},
            {"brand": "combanketh.et", "name": "Commercial Bank of Ethiopia", "active_spoofs_detected": 28},
            {"brand": "awashbank.com", "name": "Awash Bank", "active_spoofs_detected": 9},
            {"brand": "dashenbanksc.com", "name": "Dashen Bank", "active_spoofs_detected": 7},
            {"brand": "chapa.co", "name": "Chapa Payment Gateway", "active_spoofs_detected": 4},
            {"brand": "ethiotelecom.et", "name": "Ethio Telecom", "active_spoofs_detected": 19}
        ]
    }
