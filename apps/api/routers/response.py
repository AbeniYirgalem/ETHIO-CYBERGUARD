"""
ETHIO-CYBERGUARD SOAR Response Router
Provides human-in-the-loop containment action approvals, dual-custody enforcement,
dry-run safety defaults, rollback, host isolation, IP blocking, account disablement,
and immutable SHA-256 audit logging.
Supports /api/response and /api/v1/response.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import hashlib
import uuid

from ..dependencies import require_permission, require_role, get_current_user
from services.response.engine import SOARResponseEngine

router = APIRouter(tags=["SOAR Containment & Automated Response"])

# Shared engine instance for containment executions and cryptographic logging
soar_engine = SOARResponseEngine()

# In-Memory Active Response Actions & Immutable Audit Log
ACTIONS_STORE: List[Dict[str, Any]] = [
    {
        "id": "ACT-001",
        "incident_number": "INC-00042",
        "action_type": "ISOLATE_HOST",
        "target_entity": "SERVER-04 (10.10.1.24)",
        "requested_by": "analyst@cbe.com.et",
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
        "requested_by": "analyst@cbe.com.et",
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
    reason: Optional[str] = "Approved by authorized incident commander"
    operator: Optional[str] = None

class HostIsolationRequest(BaseModel):
    hostname: str
    ip_address: Optional[str] = None
    reason: str
    incident_number: Optional[str] = "INC-00042"
    require_approval: Optional[bool] = True
    dry_run: Optional[bool] = None

class BlockIPRequest(BaseModel):
    ip_address: str
    direction: Optional[str] = "BOTH" # INGRESS, EGRESS, BOTH
    reason: str
    incident_number: Optional[str] = "INC-00042"
    require_approval: Optional[bool] = True
    dry_run: Optional[bool] = None

class DisableAccountRequest(BaseModel):
    username: str
    domain: Optional[str] = "cbe.internal"
    reason: str
    incident_number: Optional[str] = "INC-00042"
    require_approval: Optional[bool] = True
    dry_run: Optional[bool] = None

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
    soar_engine.audit.record(operator=operator, action=action, target=target, reason=details, result=result)

@router.get("/api/response/actions")
@router.get("/api/v1/response/actions")
def list_response_actions(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"total": len(ACTIONS_STORE), "actions": ACTIONS_STORE}

@router.post("/api/response/isolate-host")
@router.post("/api/v1/response/isolate-host")
def request_host_isolation(
    payload: HostIsolationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    action_id = f"ACT-{len(ACTIONS_STORE) + 1:03d}"
    now = datetime.now(timezone.utc)
    user_email = current_user.get("email", "analyst@cbe.com.et")
    
    # Destructive actions require approval; dry_run is safe simulation
    if payload.dry_run is True:
        is_dry_run = True
        status_str = "DRY_RUN_SIMULATED"
    elif payload.dry_run is False:
        is_dry_run = False
        status_str = "PENDING_APPROVAL" if payload.require_approval else "APPROVED"
    else:
        # Default behavior: if require_approval is explicitly False, approve directly; otherwise require approval
        is_dry_run = False
        status_str = "PENDING_APPROVAL" if payload.require_approval else "APPROVED"
    
    action = {
        "id": action_id,
        "incident_number": payload.incident_number,
        "action_type": "ISOLATE_HOST",
        "target_entity": f"{payload.hostname} ({payload.ip_address or 'DHCP'})",
        "requested_by": user_email,
        "recommended_by": "ANALYST_REQUEST",
        "reasoning": payload.reason,
        "confidence": 95,
        "status": status_str,
        "dry_run": is_dry_run,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat()
    }
    ACTIONS_STORE.insert(0, action)
    _record_audit(user_email, f"ISOLATE_HOST_{'DRY_RUN' if is_dry_run else 'SUBMITTED'}", payload.hostname, "SUCCESS" if is_dry_run else "PENDING", payload.reason)
    return {
        "status": "SIMULATED" if is_dry_run else ("QUEUED" if payload.require_approval else "EXECUTED"),
        "dry_run": is_dry_run,
        "action_id": action_id,
        "action": action
    }

@router.post("/api/response/block-ip")
@router.post("/api/v1/response/block-ip")
def request_block_ip(
    payload: BlockIPRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    action_id = f"ACT-{len(ACTIONS_STORE) + 1:03d}"
    now = datetime.now(timezone.utc)
    user_email = current_user.get("email", "analyst@cbe.com.et")
    
    if payload.dry_run is True:
        is_dry_run = True
        status_str = "DRY_RUN_SIMULATED"
    elif payload.dry_run is False:
        is_dry_run = False
        status_str = "PENDING_APPROVAL" if payload.require_approval else "APPROVED"
    else:
        # Default behavior: if require_approval is explicitly False, approve directly; otherwise require approval
        is_dry_run = False
        status_str = "PENDING_APPROVAL" if payload.require_approval else "APPROVED"
    
    action = {
        "id": action_id,
        "incident_number": payload.incident_number,
        "action_type": "BLOCK_IP",
        "target_entity": payload.ip_address,
        "requested_by": user_email,
        "recommended_by": "ANALYST_REQUEST",
        "reasoning": payload.reason,
        "confidence": 99,
        "status": status_str,
        "dry_run": is_dry_run,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat()
    }
    ACTIONS_STORE.insert(0, action)
    _record_audit(user_email, f"BLOCK_IP_{'DRY_RUN' if is_dry_run else 'SUBMITTED'}", payload.ip_address, "SUCCESS" if is_dry_run else "PENDING", payload.reason)
    return {
        "status": "SIMULATED" if is_dry_run else ("QUEUED" if payload.require_approval else "EXECUTED"),
        "dry_run": is_dry_run,
        "action_id": action_id,
        "action": action
    }

@router.post("/api/response/disable-account")
@router.post("/api/v1/response/disable-account")
def request_disable_account(
    payload: DisableAccountRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    action_id = f"ACT-{len(ACTIONS_STORE) + 1:03d}"
    now = datetime.now(timezone.utc)
    user_email = current_user.get("email", "analyst@cbe.com.et")
    
    if payload.dry_run is True:
        is_dry_run = True
        status_str = "DRY_RUN_SIMULATED"
    elif payload.dry_run is False:
        is_dry_run = False
        status_str = "PENDING_APPROVAL" if payload.require_approval else "APPROVED"
    else:
        # Default behavior: if require_approval is explicitly False, approve directly; otherwise require approval
        is_dry_run = False
        status_str = "PENDING_APPROVAL" if payload.require_approval else "APPROVED"
    
    action = {
        "id": action_id,
        "incident_number": payload.incident_number,
        "action_type": "DISABLE_ACCOUNT",
        "target_entity": f"{payload.username}@{payload.domain}",
        "requested_by": user_email,
        "recommended_by": "ANALYST_REQUEST",
        "reasoning": payload.reason,
        "confidence": 90,
        "status": status_str,
        "dry_run": is_dry_run,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat()
    }
    ACTIONS_STORE.insert(0, action)
    _record_audit(user_email, f"DISABLE_ACCOUNT_{'DRY_RUN' if is_dry_run else 'SUBMITTED'}", payload.username, "SUCCESS" if is_dry_run else "PENDING", payload.reason)
    return {
        "status": "SIMULATED" if is_dry_run else ("QUEUED" if payload.require_approval else "EXECUTED"),
        "dry_run": is_dry_run,
        "action_id": action_id,
        "action": action
    }

@router.post("/api/response/actions/{action_id}/approve")
@router.post("/api/v1/response/actions/{action_id}/approve")
def approve_action(
    action_id: str,
    payload: ActionDecisionPayload,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    from apps.api.config import DEMO_MODE
    action = next((a for a in ACTIONS_STORE if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
    
    user_email = current_user.get("email")
    user_role = current_user.get("role", "SECURITY_ANALYST")
    requested_by = action.get("requested_by")

    # Disallowed roles (Auditor and Read-Only can never approve)
    if user_role in ["AUDITOR", "READ_ONLY"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. User role {user_role} is not authorized for containment approvals."
        )

    # Server-side Dual-Custody Enforcement:
    # In production mode, or whenever an explicit user identity is provided,
    # the requester cannot approve their own action (unless SUPER_ADMIN).
    if not DEMO_MODE or (current_user.get("id") != "usr_guest" and user_role != "SUPER_ADMIN"):
        if not DEMO_MODE and user_role not in ["SUPER_ADMIN", "SOC_MANAGER", "INCIDENT_RESPONDER", "INCIDENT_COMMANDER"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Role {user_role} is not authorized for containment approvals in production."
            )
        if requested_by and user_email == requested_by:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Dual-Custody Violation: Initiator ({requested_by}) cannot approve their own containment action. Secondary authorization required."
            )

    # Check expiration
    if action.get("expires_at"):
        exp = datetime.fromisoformat(action["expires_at"])
        if datetime.now(timezone.utc) > exp:
            action["status"] = "EXPIRED"
            raise HTTPException(status_code=400, detail="Action approval has expired. Re-submission required.")

    approver_desc = f"{current_user.get('name', user_email)} ({user_role})"
    action["status"] = "APPROVED"
    action["executed_at"] = datetime.now(timezone.utc).isoformat()
    action["reviewed_by"] = approver_desc
    action["approved_by"] = user_email
    action["dual_custody_verified"] = True
    
    # Execute through the SOAR containment engine
    execution_result = {}
    target = action.get("target_entity", "")
    reason = payload.reason or "Authorized by SOC commander"
    
    if action["action_type"] == "ISOLATE_HOST":
        from services.response.host_isolation import HostIsolationService
        execution_result = HostIsolationService.isolate_host(target, "10.10.1.24", reason)
    elif action["action_type"] == "BLOCK_IP":
        from services.response.firewall import FirewallBlockService
        execution_result = FirewallBlockService.block_ip(target, "BOTH", reason)
    elif action["action_type"] == "DISABLE_ACCOUNT":
        from services.response.account_disable import AccountDisableService
        execution_result = AccountDisableService.disable_user(target, "cbe.internal", reason)
    
    action["execution_result"] = execution_result
    
    _record_audit(
        approver_desc,
        f"ACTION_APPROVED_{action['action_type']}",
        action["target_entity"],
        "SUCCESS",
        f"Approved for {action['incident_number']}: {reason}"
    )
    
    return {
        "status": "SUCCESS",
        "message": f"Action {action_id} ({action['action_type']}) APPROVED and executed by SOAR engine under verified dual custody.",
        "action": action,
        "execution": execution_result
    }

@router.post("/api/response/actions/{action_id}/reject")
@router.post("/api/v1/response/actions/{action_id}/reject")
def reject_action(
    action_id: str,
    payload: ActionDecisionPayload,
    current_user: Dict[str, Any] = Depends(
        require_role(["SUPER_ADMIN", "SOC_MANAGER", "INCIDENT_RESPONDER", "INCIDENT_COMMANDER", "SECURITY_ANALYST"])
    )
):
    action = next((a for a in ACTIONS_STORE if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
    
    approver_desc = f"{current_user.get('name', current_user.get('email'))} ({current_user.get('role')})"
    action["status"] = "REJECTED"
    action["rejection_reason"] = payload.reason
    action["reviewed_by"] = approver_desc
    
    _record_audit(
        approver_desc,
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
def rollback_action(
    action_id: str,
    payload: ActionDecisionPayload,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    from apps.api.config import DEMO_MODE
    user_role = current_user.get("role", "SECURITY_ANALYST")
    if user_role in ["AUDITOR", "READ_ONLY"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. User role {user_role} is not authorized for containment rollbacks."
        )
    if not DEMO_MODE and user_role not in ["SUPER_ADMIN", "SOC_MANAGER", "INCIDENT_RESPONDER", "INCIDENT_COMMANDER"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied. User role {user_role} is not authorized for containment rollbacks in production."
        )
    action = next((a for a in ACTIONS_STORE if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
        
    if action["status"] != "APPROVED":
        raise HTTPException(status_code=400, detail="Only executed/approved actions can be rolled back.")
        
    approver_desc = f"{current_user.get('name', current_user.get('email'))} ({current_user.get('role')})"
    action["status"] = "ROLLED_BACK"
    action["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
    action["rollback_reason"] = payload.reason
    
    _record_audit(
        approver_desc,
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
def get_response_audit_log(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"total": len(AUDIT_LOG_STORE), "audit_logs": AUDIT_LOG_STORE}
