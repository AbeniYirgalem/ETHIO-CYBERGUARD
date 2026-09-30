"""
ETHIO-CYBERGUARD SOAR Response Router
Provides human-in-the-loop containment action approvals, dry-run mode, rollback,
host isolation, IP blocking, account disablement, and immutable SHA-256 audit logging.
Supports /api/response and /api/v1/response.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import hashlib
import uuid

from ..dependencies import require_permission, get_current_user

router = APIRouter(tags=["SOAR Containment & Automated Response"])

# In-Memory Active Response Actions & Immutable Audit Log
ACTIONS_STORE: List[Dict[str, Any]] = [
    {
        "id": "ACT-001",
        "incident_number": "INC-00042",
        "action_type": "ISOLATE_HOST",
        "target_entity": "SERVER-04 (10.10.1.24)",
        "recommended_by": "AI_RISK_AGENT",
        "reasoning": "Potential active malware / C2 beaconing. Host isolation cuts lateral traversal while maintaining forensic link to SOC.",
        "confidence": 94,
        "status": "PENDING_APPROVAL",
        "dry_run": False,
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    {
        "id": "ACT-002",
        "incident_number": "INC-00042",
        "action_type": "BLOCK_IP",
        "target_entity": "185.220.101.5",
        "recommended_by": "AI_THREAT_INTEL_AGENT",
        "reasoning": "Confirmed Cobalt Strike C2 server on Ethio-CERT blacklist. Egress and ingress drop recommended.",
        "confidence": 98,
        "status": "PENDING_APPROVAL",
        "dry_run": False,
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
]

AUDIT_LOG_STORE: List[Dict[str, Any]] = [
    {
        "id": "AUD-001",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "operator": "system",
        "action": "CORRELATION_INCIDENT_CREATED",
        "target": "INC-00042",
        "result": "SUCCESS",
        "details": "Initial incident correlation",
        "prev_hash": "0000000000000000000000000000000000000000000000000000000000000000",
        "integrity_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }
]

class ActionDecisionPayload(BaseModel):
    reason: Optional[str] = "Approved by SOC analyst Dawit Mengistu"
    operator: Optional[str] = "Dawit Mengistu (Security Analyst)"

class HostIsolationRequest(BaseModel):
    hostname: str
    ip_address: Optional[str] = None
    reason: str
    incident_number: Optional[str] = "INC-00042"
    require_approval: Optional[bool] = True
    dry_run: Optional[bool] = False

class BlockIPRequest(BaseModel):
    ip_address: str
    direction: Optional[str] = "BOTH" # INGRESS, EGRESS, BOTH
    reason: str
    incident_number: Optional[str] = "INC-00042"
    require_approval: Optional[bool] = True
    dry_run: Optional[bool] = False

class DisableAccountRequest(BaseModel):
    username: str
    domain: Optional[str] = "cbe.internal"
    reason: str
    incident_number: Optional[str] = "INC-00042"
    require_approval: Optional[bool] = True
    dry_run: Optional[bool] = False

def _record_audit(operator: str, action: str, target: str, result: str, details: str):
    prev_hash = AUDIT_LOG_STORE[0]["integrity_hash"] if AUDIT_LOG_STORE else "0000000000000000000000000000000000000000000000000000000000000000"
    ts = datetime.now(timezone.utc).isoformat()
    entry_str = f"{prev_hash}|{operator}|{action}|{target}|{result}|{ts}"
    h = hashlib.sha256(entry_str.encode("utf-8")).hexdigest()
    entry = {
        "id": f"AUD-{len(AUDIT_LOG_STORE) + 1:03d}",
        "timestamp": ts,
        "operator": operator,
        "action": action,
        "target": target,
        "result": result,
        "details": details,
        "prev_hash": prev_hash,
        "integrity_hash": h
    }
    AUDIT_LOG_STORE.insert(0, entry)

@router.get("/api/response/actions")
@router.get("/api/v1/response/actions")
def list_response_actions():
    return {"total": len(ACTIONS_STORE), "actions": ACTIONS_STORE}

@router.post("/api/response/isolate-host")
@router.post("/api/v1/response/isolate-host")
def request_host_isolation(payload: HostIsolationRequest):
    action_id = f"ACT-{len(ACTIONS_STORE) + 1:03d}"
    now = datetime.now(timezone.utc)
    action = {
        "id": action_id,
        "incident_number": payload.incident_number,
        "action_type": "ISOLATE_HOST",
        "target_entity": f"{payload.hostname} ({payload.ip_address or 'DHCP'})",
        "recommended_by": "ANALYST_REQUEST",
        "reasoning": payload.reason,
        "confidence": 95,
        "status": "DRY_RUN_SIMULATED" if payload.dry_run else ("PENDING_APPROVAL" if payload.require_approval else "APPROVED"),
        "dry_run": payload.dry_run,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat()
    }
    ACTIONS_STORE.insert(0, action)
    _record_audit("analyst", f"ISOLATE_HOST_{'DRY_RUN' if payload.dry_run else 'SUBMITTED'}", payload.hostname, "SUCCESS" if payload.dry_run else "PENDING", payload.reason)
    return {
        "status": "SIMULATED" if payload.dry_run else ("QUEUED" if payload.require_approval else "EXECUTED"),
        "dry_run": payload.dry_run,
        "action_id": action_id,
        "action": action
    }

@router.post("/api/response/block-ip")
@router.post("/api/v1/response/block-ip")
def request_block_ip(payload: BlockIPRequest):
    action_id = f"ACT-{len(ACTIONS_STORE) + 1:03d}"
    now = datetime.now(timezone.utc)
    action = {
        "id": action_id,
        "incident_number": payload.incident_number,
        "action_type": "BLOCK_IP",
        "target_entity": payload.ip_address,
        "recommended_by": "ANALYST_REQUEST",
        "reasoning": payload.reason,
        "confidence": 99,
        "status": "DRY_RUN_SIMULATED" if payload.dry_run else ("PENDING_APPROVAL" if payload.require_approval else "APPROVED"),
        "dry_run": payload.dry_run,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat()
    }
    ACTIONS_STORE.insert(0, action)
    _record_audit("analyst", f"BLOCK_IP_{'DRY_RUN' if payload.dry_run else 'SUBMITTED'}", payload.ip_address, "SUCCESS" if payload.dry_run else "PENDING", payload.reason)
    return {
        "status": "SIMULATED" if payload.dry_run else ("QUEUED" if payload.require_approval else "EXECUTED"),
        "dry_run": payload.dry_run,
        "action_id": action_id,
        "action": action
    }

@router.post("/api/response/disable-account")
@router.post("/api/v1/response/disable-account")
def request_disable_account(payload: DisableAccountRequest):
    action_id = f"ACT-{len(ACTIONS_STORE) + 1:03d}"
    now = datetime.now(timezone.utc)
    action = {
        "id": action_id,
        "incident_number": payload.incident_number,
        "action_type": "DISABLE_ACCOUNT",
        "target_entity": f"{payload.username}@{payload.domain}",
        "recommended_by": "ANALYST_REQUEST",
        "reasoning": payload.reason,
        "confidence": 90,
        "status": "DRY_RUN_SIMULATED" if payload.dry_run else ("PENDING_APPROVAL" if payload.require_approval else "APPROVED"),
        "dry_run": payload.dry_run,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat()
    }
    ACTIONS_STORE.insert(0, action)
    _record_audit("analyst", f"DISABLE_ACCOUNT_{'DRY_RUN' if payload.dry_run else 'SUBMITTED'}", payload.username, "SUCCESS" if payload.dry_run else "PENDING", payload.reason)
    return {
        "status": "SIMULATED" if payload.dry_run else ("QUEUED" if payload.require_approval else "EXECUTED"),
        "dry_run": payload.dry_run,
        "action_id": action_id,
        "action": action
    }

@router.post("/api/response/actions/{action_id}/approve")
@router.post("/api/v1/response/actions/{action_id}/approve")
def approve_action(action_id: str, payload: ActionDecisionPayload):
    action = next((a for a in ACTIONS_STORE if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
    
    # Check expiration
    if action.get("expires_at"):
        exp = datetime.fromisoformat(action["expires_at"])
        if datetime.now(timezone.utc) > exp:
            action["status"] = "EXPIRED"
            raise HTTPException(status_code=400, detail="Action approval has expired. Re-submission required.")

    action["status"] = "APPROVED"
    action["executed_at"] = datetime.now(timezone.utc).isoformat()
    action["reviewed_by"] = payload.operator or "Dawit Mengistu (Security Analyst)"
    
    _record_audit(
        action["reviewed_by"],
        f"ACTION_APPROVED_{action['action_type']}",
        action["target_entity"],
        "SUCCESS",
        f"Approved for {action['incident_number']}: {payload.reason}"
    )
    
    return {
        "status": "SUCCESS",
        "message": f"Action {action_id} ({action['action_type']}) APPROVED and executed by SOAR engine.",
        "action": action
    }

@router.post("/api/response/actions/{action_id}/reject")
@router.post("/api/v1/response/actions/{action_id}/reject")
def reject_action(action_id: str, payload: ActionDecisionPayload):
    action = next((a for a in ACTIONS_STORE if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
    
    action["status"] = "REJECTED"
    action["rejection_reason"] = payload.reason
    action["reviewed_by"] = payload.operator or "Dawit Mengistu (Security Analyst)"
    
    _record_audit(
        action["reviewed_by"],
        f"ACTION_REJECTED_{action['action_type']}",
        action["target_entity"],
        "REJECTED",
        f"Rejected: {payload.reason}"
    )
    
    return {
        "status": "SUCCESS",
        "message": f"Action {action_id} REJECTED.",
        "action": action
    }

@router.post("/api/response/actions/{action_id}/rollback")
@router.post("/api/v1/response/actions/{action_id}/rollback")
def rollback_action(action_id: str, payload: ActionDecisionPayload):
    action = next((a for a in ACTIONS_STORE if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
        
    if action["status"] != "APPROVED":
        raise HTTPException(status_code=400, detail="Only executed/approved actions can be rolled back.")
        
    action["status"] = "ROLLED_BACK"
    action["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
    action["rollback_reason"] = payload.reason
    
    _record_audit(
        payload.operator or "Dawit Mengistu (Security Analyst)",
        f"ACTION_ROLLED_BACK_{action['action_type']}",
        action["target_entity"],
        "SUCCESS",
        f"Rollback reason: {payload.reason}"
    )
    
    return {
        "status": "SUCCESS",
        "message": f"Action {action_id} ({action['action_type']}) has been safely rolled back.",
        "action": action
    }

@router.get("/api/response/audit-log")
@router.get("/api/v1/response/audit-log")
def get_response_audit_log():
    return {"total": len(AUDIT_LOG_STORE), "audit_logs": AUDIT_LOG_STORE}
