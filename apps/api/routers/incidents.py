"""
ETHIO-CYBERGUARD Incidents Router
Provides incident listing, detail querying, incident creation, status updates, and evidence management.
Supports both /api/incidents and /api/v1/incidents paths.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

router = APIRouter(tags=["Incident Management & Investigation"])

# In-Memory Incident Store (Seeded with realistic Ethiopian scenarios)
INCIDENTS_STORE: List[Dict[str, Any]] = [
    {
        "id": "e0000000-0000-0000-0000-000000000001",
        "incident_number": "INC-00042",
        "title": "Suspicious Obfuscated PowerShell Activity & C2 Beaconing",
        "severity": "CRITICAL",
        "status": "INVESTIGATING",
        "risk_score": 92,
        "affected_asset": "SERVER-04",
        "asset_ip": "10.10.1.24",
        "department": "Core Banking Infrastructure",
        "sector": "Banking",
        "first_seen": "2026-09-30 10:42:00+03:00",
        "last_activity": "2026-09-30 11:18:00+03:00",
        "assigned_analyst": "Dawit Mengistu",
        "mitre_techniques": ["T1059.001", "T1071.001", "T1003.001"],
        "summary": "Privileged service account initiated hidden PowerShell with base64 encoded command, establishing outbound beaconing to known malicious C2 IP 185.220.101.5.",
        "evidence": [
            {"type": "COMMAND_LINE", "value": "powershell.exe -NoP -NonI -W Hidden -enc SQBFAFgA...", "hash": "sha256_31fa..."},
            {"type": "DESTINATION_IP", "value": "185.220.101.5", "hash": "sha256_88b2..."}
        ]
    },
    {
        "id": "e0000000-0000-0000-0000-000000000002",
        "incident_number": "INC-00021",
        "title": "Perimeter Gateway Distributed SSH & RDP Brute Force",
        "severity": "HIGH",
        "status": "OPEN",
        "risk_score": 78,
        "affected_asset": "FW-PERIMETER-01",
        "asset_ip": "197.156.70.1",
        "department": "Network Security",
        "sector": "Telecom",
        "first_seen": "2026-09-30 09:15:00+03:00",
        "last_activity": "2026-09-30 09:22:00+03:00",
        "assigned_analyst": "Sara Yohannes",
        "mitre_techniques": ["T1110.001", "T1110.003"],
        "summary": "Over 1,200 failed authentication attempts detected within 4 minutes originating from distributed IP ranges targeting perimeter firewall management interface.",
        "evidence": [
            {"type": "SYSLOG_RECORD", "value": "pam_unix(sshd:auth): authentication failure; logname= uid=0 euid=0", "hash": "sha256_91aa..."}
        ]
    },
    {
        "id": "e0000000-0000-0000-0000-000000000003",
        "incident_number": "INC-00019",
        "title": "Unusual Off-Hours Privileged SWIFT Access from Remote IP",
        "severity": "MEDIUM",
        "status": "INVESTIGATING",
        "risk_score": 64,
        "affected_asset": "LAPTOP-FINANCE-22",
        "asset_ip": "10.10.4.88",
        "department": "Treasury & SWIFT Processing",
        "sector": "Banking",
        "first_seen": "2026-09-30 03:14:00+03:00",
        "last_activity": "2026-09-30 03:45:00+03:00",
        "assigned_analyst": "Dawit Mengistu",
        "mitre_techniques": ["T1078.002", "T1048"],
        "summary": "Treasury workstation user logged in at 03:14 AM EAT from unmanaged residential IP subnet, accessing SWIFT payment file transfer directory.",
        "evidence": [
            {"type": "USER_SESSION", "value": "User 'yared.t' logged in via OpenVPN from 196.188.12.99", "hash": "sha256_12ef..."}
        ]
    }
]

class CreateIncidentPayload(BaseModel):
    title: str
    severity: str = "HIGH"
    affected_asset: str
    asset_ip: str
    department: Optional[str] = "IT Infrastructure"
    sector: Optional[str] = "Banking"
    summary: str
    mitre_techniques: Optional[List[str]] = []
    assigned_analyst: Optional[str] = "Dawit Mengistu"

class UpdateIncidentPayload(BaseModel):
    status: Optional[str] = None
    assigned_analyst: Optional[str] = None
    risk_score: Optional[int] = None
    summary: Optional[str] = None

class AttachEvidencePayload(BaseModel):
    evidence_type: str
    value: str
    description: Optional[str] = None

@router.get("/api/incidents")
@router.get("/api/v1/incidents")
def list_incidents(
    severity: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    sector: Optional[str] = None,
    query: Optional[str] = None
):
    results = INCIDENTS_STORE
    if severity:
        results = [i for i in results if i["severity"].upper() == severity.upper()]
    if status_filter:
        results = [i for i in results if i["status"].upper() == status_filter.upper()]
    if sector:
        results = [i for i in results if i.get("sector", "").lower() == sector.lower()]
    if query:
        q = query.lower()
        results = [
            i for i in results 
            if q in i["title"].lower() or q in i["incident_number"].lower() or q in i["affected_asset"].lower()
        ]
    return {"total": len(results), "incidents": results}

@router.get("/api/incidents/{incident_id}")
@router.get("/api/v1/incidents/{incident_id}")
def get_incident_by_id(incident_id: str):
    inc = next(
        (i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), 
        None
    )
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident '{incident_id}' not found")
    
    # Generated attack graph & timeline for deep investigation
    timeline = [
        {"time": inc["first_seen"], "event": "Initial detection trigger observed", "source": "SIGMA Engine"},
        {"time": inc["last_activity"], "event": "Correlated anomaly confirmed by AI Correlation Agent", "source": "AI Correlation"},
        {"time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"), "event": f"Active state: {inc['status']}", "source": "SOC Lifecycle"}
    ]
    
    attack_graph = {
        "nodes": [
            {"id": "node_threat_actor", "label": "External Threat Actor", "type": "actor", "status": "malicious"},
            {"id": "node_asset", "label": inc["affected_asset"], "type": "endpoint", "status": "compromised"},
            {"id": "node_c2", "label": "C2 Server 185.220.101.5", "type": "infrastructure", "status": "blocked"}
        ],
        "edges": [
            {"source": "node_threat_actor", "target": "node_asset", "label": "T1566 Phishing / T1110 Brute Force"},
            {"source": "node_asset", "target": "node_c2", "label": "T1071 Egress Beaconing"}
        ]
    }
    
    return {
        "incident": inc,
        "timeline": timeline,
        "attack_graph": attack_graph,
        "evidence_count": len(inc.get("evidence", []))
    }

@router.post("/api/incidents", status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/incidents", status_code=status.HTTP_201_CREATED)
def create_incident(payload: CreateIncidentPayload):
    new_inc_num = f"INC-{len(INCIDENTS_STORE) + 43:05d}"
    now_str = datetime.now(timezone.utc).isoformat()
    
    new_inc = {
        "id": str(uuid.uuid4()),
        "incident_number": new_inc_num,
        "title": payload.title,
        "severity": payload.severity.upper(),
        "status": "OPEN",
        "risk_score": 85 if payload.severity.upper() == "CRITICAL" else 65,
        "affected_asset": payload.affected_asset,
        "asset_ip": payload.asset_ip,
        "department": payload.department,
        "sector": payload.sector,
        "first_seen": now_str,
        "last_activity": now_str,
        "assigned_analyst": payload.assigned_analyst,
        "mitre_techniques": payload.mitre_techniques or ["T1059"],
        "summary": payload.summary,
        "evidence": []
    }
    
    INCIDENTS_STORE.insert(0, new_inc)
    return {
        "status": "CREATED",
        "message": f"Incident {new_inc_num} successfully registered.",
        "incident": new_inc
    }

@router.patch("/api/incidents/{incident_id}")
@router.patch("/api/v1/incidents/{incident_id}")
def update_incident(incident_id: str, payload: UpdateIncidentPayload):
    inc = next(
        (i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), 
        None
    )
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if payload.status:
        inc["status"] = payload.status.upper()
    if payload.assigned_analyst:
        inc["assigned_analyst"] = payload.assigned_analyst
    if payload.risk_score is not None:
        inc["risk_score"] = payload.risk_score
    if payload.summary:
        inc["summary"] = payload.summary
    inc["last_activity"] = datetime.now(timezone.utc).isoformat()
    
    return {"status": "UPDATED", "incident": inc}

@router.post("/api/incidents/{incident_id}/evidence")
def attach_incident_evidence(incident_id: str, payload: AttachEvidencePayload):
    inc = next(
        (i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), 
        None
    )
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    import hashlib
    content_hash = hashlib.sha256(payload.value.encode("utf-8")).hexdigest()
    evidence_item = {
        "id": f"evi_{uuid.uuid4().hex[:6]}",
        "type": payload.evidence_type,
        "value": payload.value,
        "description": payload.description,
        "hash": f"sha256_{content_hash[:16]}",
        "recorded_at": datetime.now(timezone.utc).isoformat()
    }
    
    if "evidence" not in inc:
        inc["evidence"] = []
    inc["evidence"].append(evidence_item)
    
    return {"status": "SUCCESS", "message": "Forensic evidence attached with integrity hash.", "evidence": evidence_item}
