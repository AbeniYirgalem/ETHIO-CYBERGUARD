"""
ETHIO-CYBERGUARD Incidents Router
Provides complete incident lifecycle management, transitions, comments, tasks, evidence, and timeline.
Supports both /api/incidents and /api/v1/incidents paths.
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid
import hashlib

from ..dependencies import get_current_user

router = APIRouter(tags=["Incident Management & Investigation"])

# Formal Incident Status Lifecycle State Machine
VALID_STATUSES = [
    "NEW",
    "TRIAGED",
    "ASSIGNED",
    "INVESTIGATING",
    "CONTAINMENT_PENDING",
    "CONTAINED",
    "ERADICATION",
    "RECOVERY",
    "CLOSED",
    "REOPENED"
]

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
            {"id": "evi_01", "type": "COMMAND_LINE", "value": "powershell.exe -NoP -NonI -W Hidden -enc SQBFAFgA...", "hash": "sha256_31fa882910ab38c4", "recorded_at": "2026-09-30T10:45:00Z"},
            {"id": "evi_02", "type": "DESTINATION_IP", "value": "185.220.101.5", "hash": "sha256_88b2910fc3821092", "recorded_at": "2026-09-30T10:46:00Z"}
        ],
        "history": [
            {"previous_status": "NEW", "new_status": "TRIAGED", "user": "Dawit Mengistu", "reason": "Initial correlation triage", "timestamp": "2026-09-30T10:43:00Z"},
            {"previous_status": "TRIAGED", "new_status": "INVESTIGATING", "user": "Dawit Mengistu", "reason": "Active beacon confirmed", "timestamp": "2026-09-30T10:45:00Z"}
        ],
        "comments": [
            {"id": "c-01", "author": "Dawit Mengistu", "content": "Host quarantined via EDR channel. Waiting for secondary approval on firewall block.", "timestamp": "2026-09-30T10:50:00Z"}
        ],
        "tasks": [
            {"id": "t-01", "title": "Memory dump extraction from SERVER-04", "completed": True},
            {"id": "t-02", "title": "Revoke Kerberos TGT tickets for compromised service account", "completed": True},
            {"id": "t-03", "title": "INSA mandatory regulatory report notification", "completed": False}
        ]
    },
    {
        "id": "e0000000-0000-0000-0000-000000000002",
        "incident_number": "INC-00021",
        "title": "Perimeter Gateway Distributed SSH & RDP Brute Force",
        "severity": "HIGH",
        "status": "NEW",
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
        "evidence": [],
        "history": [],
        "comments": [],
        "tasks": []
    },
    {
        "id": "e0000000-0000-0000-0000-000000000003",
        "incident_number": "INC-00019",
        "title": "Telebirr Mobile Financial Lure Phishing Campaign",
        "severity": "HIGH",
        "status": "CONTAINED",
        "risk_score": 81,
        "affected_asset": "EMAIL-GATEWAY-ET",
        "asset_ip": "197.156.64.12",
        "department": "Digital Banking Operations",
        "sector": "Fintech",
        "first_seen": "2026-09-30 08:30:00+03:00",
        "last_activity": "2026-09-30 09:05:00+03:00",
        "assigned_analyst": "Abebe Kebede",
        "mitre_techniques": ["T1566.001", "T1566.002"],
        "summary": "High-volume spearphishing campaign using Amharic urgent lottery claims. Typosquatted domain telebiir-bonus-et.com blocked at perimeter DNS.",
        "evidence": [],
        "history": [],
        "comments": [],
        "tasks": []
    }
]

class CreateIncidentPayload(BaseModel):
    title: str
    severity: str = "MEDIUM"
    affected_asset: str = "SERVER-01"
    asset_ip: str = "10.10.1.10"
    department: str = "Core Banking"
    sector: str = "Banking"
    assigned_analyst: str = "Dawit Mengistu"
    summary: str
    mitre_techniques: Optional[List[str]] = None

class UpdateIncidentPayload(BaseModel):
    status: Optional[str] = None
    assigned_analyst: Optional[str] = None
    risk_score: Optional[int] = None
    summary: Optional[str] = None

class TransitionStatusPayload(BaseModel):
    new_status: str
    reason: Optional[str] = "Routine SOC lifecycle progression"

class AddCommentPayload(BaseModel):
    content: str

class AddTaskPayload(BaseModel):
    title: str

class UpdateTaskPayload(BaseModel):
    completed: bool

class AttachEvidencePayload(BaseModel):
    evidence_type: str = "COMMAND_LINE"
    value: str
    description: Optional[str] = None

@router.get("/api/incidents")
@router.get("/api/v1/incidents")
def list_all_incidents(
    status_filter: Optional[str] = Query(None, alias="status"),
    severity: Optional[str] = None,
    sector: Optional[str] = None
):
    results = INCIDENTS_STORE
    if status_filter:
        results = [i for i in results if i["status"].upper() == status_filter.upper()]
    if severity:
        results = [i for i in results if i["severity"].upper() == severity.upper()]
    if sector:
        results = [i for i in results if i.get("sector", "").lower() == sector.lower()]
    return {
        "total": len(results),
        "incidents": results
    }

@router.get("/api/incidents/{incident_id}")
def get_incident_by_id(incident_id: str):
    inc = next(
        (i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), 
        None
    )
    if not inc:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
        
    from services.correlation.correlator import CorrelationEngine
    from services.ai.orchestrator import MultiAgentOrchestrator
    correlation_engine = CorrelationEngine()
    ai_orchestrator = MultiAgentOrchestrator()
    correlated = correlation_engine.correlate_alerts([], asset_name=inc.get("affected_asset", "SERVER-04"))
    investigation = ai_orchestrator.run_investigation_pipeline(inc, [])

    return {
        "incident": inc,
        "timeline": correlated["timeline"],
        "attack_graph": correlated["attack_graph"],
        "ai_investigation": investigation.get("pipeline_results", {}),
        **inc
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
        "status": "NEW",
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
        "evidence": [],
        "history": [{"previous_status": None, "new_status": "NEW", "user": payload.assigned_analyst, "reason": "Incident opened", "timestamp": now_str}],
        "comments": [],
        "tasks": []
    }
    
    INCIDENTS_STORE.insert(0, new_inc)
    return {
        "status": "CREATED",
        "message": f"Incident {new_inc_num} successfully registered.",
        "incident": new_inc
    }

@router.post("/api/incidents/{incident_id}/transition")
@router.post("/api/v1/incidents/{incident_id}/transition")
def transition_incident_status(
    incident_id: str, 
    payload: TransitionStatusPayload, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    inc = next(
        (i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), 
        None
    )
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
        
    status_upper = payload.new_status.upper()
    if status_upper not in VALID_STATUSES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status '{payload.new_status}'. Allowed: {VALID_STATUSES}"
        )
        
    prev = inc["status"]
    inc["status"] = status_upper
    now_str = datetime.now(timezone.utc).isoformat()
    inc["last_activity"] = now_str
    
    history_entry = {
        "previous_status": prev,
        "new_status": status_upper,
        "user": current_user.get("name", "Analyst"),
        "reason": payload.reason,
        "timestamp": now_str
    }
    if "history" not in inc:
        inc["history"] = []
    inc["history"].append(history_entry)
    
    return {
        "status": "TRANSITIONED",
        "incident_number": inc["incident_number"],
        "previous_status": prev,
        "new_status": status_upper,
        "history_entry": history_entry
    }

@router.get("/api/incidents/{incident_id}/comments")
@router.get("/api/v1/incidents/{incident_id}/comments")
def list_incident_comments(incident_id: str):
    inc = next((i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), None)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"comments": inc.get("comments", [])}

@router.post("/api/incidents/{incident_id}/comments", status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/incidents/{incident_id}/comments", status_code=status.HTTP_201_CREATED)
def add_incident_comment(
    incident_id: str, 
    payload: AddCommentPayload, 
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    inc = next((i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), None)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    comment = {
        "id": f"c-{uuid.uuid4().hex[:6]}",
        "author": current_user.get("name", "Analyst"),
        "content": payload.content,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    if "comments" not in inc:
        inc["comments"] = []
    inc["comments"].append(comment)
    return {"status": "CREATED", "comment": comment}

@router.post("/api/incidents/{incident_id}/tasks", status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/incidents/{incident_id}/tasks", status_code=status.HTTP_201_CREATED)
def add_incident_task(incident_id: str, payload: AddTaskPayload):
    inc = next((i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), None)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    task = {
        "id": f"t-{uuid.uuid4().hex[:6]}",
        "title": payload.title,
        "completed": False
    }
    if "tasks" not in inc:
        inc["tasks"] = []
    inc["tasks"].append(task)
    return {"status": "CREATED", "task": task}

@router.patch("/api/incidents/{incident_id}/tasks/{task_id}")
@router.patch("/api/v1/incidents/{incident_id}/tasks/{task_id}")
def update_incident_task(incident_id: str, task_id: str, payload: UpdateTaskPayload):
    inc = next((i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), None)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    tasks = inc.get("tasks", [])
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task["completed"] = payload.completed
    return {"status": "UPDATED", "task": task}

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
    
    content_hash = hashlib.sha256(payload.value.encode("utf-8")).hexdigest()
    evidence_item = {
        "id": f"evi_{uuid.uuid4().hex[:6]}",
        "type": payload.evidence_type,
        "value": payload.value,
        "description": payload.description,
        "sha256_hash": content_hash,
        "hash": f"sha256_{content_hash[:16]}",
        "recorded_at": datetime.now(timezone.utc).isoformat()
    }
    
    if "evidence" not in inc:
        inc["evidence"] = []
    inc["evidence"].append(evidence_item)
    
    return {"status": "SUCCESS", "message": "Forensic evidence attached with integrity hash.", "evidence": evidence_item}

@router.get("/api/incidents/{incident_id}/timeline")
@router.get("/api/v1/incidents/{incident_id}/timeline")
def get_incident_timeline(incident_id: str):
    inc = next((i for i in INCIDENTS_STORE if i["id"] == incident_id or i["incident_number"].upper() == incident_id.upper()), None)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {
        "incident_number": inc["incident_number"],
        "history": inc.get("history", []),
        "comments": inc.get("comments", []),
        "evidence": inc.get("evidence", [])
    }
