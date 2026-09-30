"""
ETHIO-CYBERGUARD Reporting & Compliance Export Router
Generates executive summaries, technical incident reports, compliance audits,
and supports JSON, CSV, and markdown export formats.
Supports /api/reports and /api/v1/reports.
"""

from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
import json

from .incidents import INCIDENTS_STORE

router = APIRouter(tags=["Security Reports & Governance"])

@router.get("/api/reports/incident/{incident_number}")
@router.get("/api/v1/reports/incident/{incident_number}")
def generate_incident_report(incident_number: str, format: str = "json"):
    inc = next(
        (i for i in INCIDENTS_STORE if i["incident_number"].upper() == incident_number.upper()), 
        None
    )
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_number}' not found")
    
    report_data = {
        "report_id": f"REP-{inc['incident_number']}",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "classification": "CONFIDENTIAL // TLP:AMBER",
        "incident": inc,
        "executive_summary": (
            f"On {inc['first_seen']}, high-severity threat activity was confirmed on asset {inc['affected_asset']}. "
            f"Automated AI correlation linked initial execution to lateral traversal attempts. "
            f"Current risk rating is {inc['risk_score']}/100 with containment playbooks initialized."
        ),
        "technical_findings": [
            {"finding": "MITRE Technique Execution", "details": inc.get("mitre_techniques", [])},
            {"finding": "Root Cause", "details": inc.get("summary")},
            {"finding": "Impact Assessment", "details": "Potential exposure to transaction ledger; isolated by SOAR response policy."}
        ],
        "compliance_alignment": {
            "insa_directive_2026": "COMPLIANT - Mandatory 24h cyber incident notification filed",
            "pci_dss_v4": "ISOLATION_VERIFIED",
            "iso_27001_a12": "INCIDENT_MANAGEMENT_DOCUMENTED"
        },
        "remediation_recommendations": [
            "Revoke compromised Kerberos service ticket and reset account credentials.",
            "Enforce strict egress firewall filtering on port 443 to unverified external subnets.",
            "Deploy endpoint memory protection policy to thwart unmanaged PowerShell spawning."
        ]
    }
    
    if format.lower() == "csv":
        csv_content = (
            "Field,Value\n"
            f"IncidentNumber,{inc['incident_number']}\n"
            f"Title,\"{inc['title']}\"\n"
            f"Severity,{inc['severity']}\n"
            f"Status,{inc['status']}\n"
            f"RiskScore,{inc['risk_score']}\n"
            f"Asset,{inc['affected_asset']}\n"
            f"Department,\"{inc['department']}\"\n"
            f"GeneratedAt,{report_data['generated_at']}\n"
        )
        return Response(content=csv_content, media_type="text/csv")
        
    return report_data

@router.get("/api/reports/executive")
@router.get("/api/v1/reports/executive")
def generate_executive_overview_report():
    return {
        "report_title": "ETHIO-CYBERGUARD Executive Cybersecurity Posture Report",
        "reporting_period": "Q3 2026",
        "organization": "Commercial Bank of Ethiopia & National Digital Infrastructure",
        "overall_security_index": 88.4,
        "threat_summary": {
            "total_attacks_blocked": 14209,
            "phishing_susceptibility_rate": "3.8% (down from 14.2%)",
            "critical_incident_dwell_time_avg": "8.5 minutes",
            "mean_time_to_contain": "12.3 minutes"
        },
        "top_strategic_risks": [
            "Regional Mobile Money Social Engineering / Telebirr credential harvesting",
            "State-sponsored lateral traversal targeting SWIFT core transaction subnets",
            "Look-alike phishing domains targeting executive wire transfers"
        ],
        "certifications_status": {
            "INSA Cyber Directive": "COMPLIANT",
            "NBE Cybersecurity Standard": "VERIFIED",
            "ISO 27001 ISMS": "CERTIFIED"
        }
    }

@router.get("/api/reports/compliance")
def get_compliance_status():
    return {
        "frameworks": [
            {"framework": "INSA National Cyber Directive 2026", "score": "98%", "status": "COMPLIANT"},
            {"framework": "National Bank of Ethiopia (NBE) Financial Guidelines", "score": "96%", "status": "COMPLIANT"},
            {"framework": "ISO/IEC 27001:2022", "score": "94%", "status": "AUDITED"},
            {"framework": "PCI-DSS v4.0", "score": "99%", "status": "CERTIFIED"}
        ]
    }
