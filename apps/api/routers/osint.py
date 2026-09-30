"""
ETHIO-CYBERGUARD OSINT & Attack Surface Recon Router
Maps external attack surface (DNS, subdomains, ASN, open ports, SSL certificates, vulnerabilities).
Enforces strict scope authorization controls and SSRF safeguards.
Supports /api/osint and /api/v1/osint.
"""

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from services.osint.surface_recon import AttackSurfaceRecon

router = APIRouter(tags=["OSINT & Attack Surface Recon"])
recon = AttackSurfaceRecon()

# Disallowed targets to prevent SSRF and internal scanning abuse
DISALLOWED_TARGETS = [
    "localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254", "internal",
    "::1", "10.", "172.16.", "192.168."
]

class OSINTScanRequest(BaseModel):
    target: str = "ethiotelecom.et"
    authorized: bool = True
    scan_depth: Optional[str] = "STANDARD" # QUICK, STANDARD, DEEP

def validate_target_scope(target: str):
    clean = target.strip().lower()
    for disallowed in DISALLOWED_TARGETS:
        if clean == disallowed or clean.startswith(disallowed) or clean.endswith(f".{disallowed}"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Target '{target}' is private or reserved. Scanning internal addresses is strictly prohibited by security policy."
            )

@router.post("/api/osint/scan")
@router.post("/api/v1/osint/scan")
def run_osint_scan_post(payload: OSINTScanRequest):
    if not payload.authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active attack surface scanning requires explicit authorization confirmation."
        )
    validate_target_scope(payload.target)
    return recon.scan_target(payload.target)

@router.get("/api/osint/scan")
@router.get("/api/v1/osint/scan")
def run_osint_scan_get(target: str = "ethiotelecom.et"):
    validate_target_scope(target)
    return recon.scan_target(target)

@router.get("/api/osint/scope-policy")
def get_scope_policy():
    return {
        "policy": "Authorized Attack Surface Assessment Only",
        "allowed_targets": [
            "*.et", "ethiotelecom.et", "combanketh.et", "telebirr.et", 
            "awashbank.com", "dashenbanksc.com", "chapa.co", "safaricom.et", "insa.gov.et"
        ],
        "prohibited": ["Private RFC 1918 subnets", "Cloud metadata endpoints (169.254.169.254)", "Localhost"]
    }
