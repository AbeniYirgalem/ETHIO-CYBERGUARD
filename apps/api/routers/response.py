"""
ETHIO-CYBERGUARD SOAR Response Router
Provides human-in-the-loop containment action approvals, dual-custody enforcement,
dry-run safety defaults, rollback, host isolation, IP blocking, account disablement,
and immutable SHA-256 audit logging.
Supports /api/response and /api/v1/response.
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import hashlib
import ipaddress
import uuid

from ..dependencies import require_permission, get_current_user, security
from ..config import DEMO_MODE
from database import state_store
from services.security.tenancy import org_of, record_org, is_global, scope, can_access
from ..dependencies import require_permission, require_role, get_current_user
from services.response.engine import SOARResponseEngine

def _persist_response_writes(request: Request):
    """After any state-changing request, snapshot actions and the audit log to the database."""
    try:
        yield
    finally:
        if request.method != "GET":
            state_store.save("response_actions")
            state_store.save("audit_log")


router = APIRouter(
    tags=["SOAR Containment & Automated Response"],
    dependencies=[Depends(_persist_response_writes)],
)


def _require_authenticated_permission(permission: str):
    """Require a real bearer token as well as the role's permission.

    get_current_user supports a guest fallback for public/demo views, so
    permission checks alone are not sufficient for sensitive SOAR routes.
    """
    def guard(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        current_user: Dict[str, Any] = Depends(require_permission(permission)),
    ) -> Dict[str, Any]:
        if credentials is None or not credentials.credentials:
            raise HTTPException(status_code=401, detail="Authentication required for SOAR response operations.")
        return current_user
    return guard

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

def _record_audit(operator: str, action: str, target: str, result: str, details: str, org_id: Optional[str] = None):
    prev_hash = AUDIT_LOG_STORE[0]["integrity_hash"] if AUDIT_LOG_STORE else "0000000000000000000000000000000000000000000000000000000000000000"
    ts = datetime.now(timezone.utc).isoformat()
    entry_str = f"{prev_hash}|{operator}|{action}|{target}|{result}|{ts}"
    h = hashlib.sha256(entry_str.encode("utf-8")).hexdigest()
    entry = {
        "id": f"AUD-{len(AUDIT_LOG_STORE) + 1:03d}",
        "org_id": org_id or record_org(None),
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

def _operator_name(user: Dict[str, Any]) -> str:
    """Use the authenticated identity for audit records, never client-supplied names."""
    return str(user.get("name") or user.get("email") or user.get("id") or "unknown")


def _user_key(user: Dict[str, Any]) -> str:
    """Stable identity used for separation-of-duties checks."""
    return str(user.get("id") or user.get("email") or "unknown")


def _require_reason(reason: Optional[str]) -> str:
    cleaned = (reason or "").strip()
    if not cleaned:
        raise HTTPException(status_code=422, detail="A non-empty reason is required.")
    if len(cleaned) > 2000:
        raise HTTPException(status_code=422, detail="Reason must be 2000 characters or fewer.")
    return cleaned


def _validate_ip(value: Optional[str], *, required: bool = False) -> Optional[str]:
    if value is None or not value.strip():
        if required:
            raise HTTPException(status_code=422, detail="A valid IP address is required.")
        return None
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid IPv4 or IPv6 address.") from exc


def _next_action_id() -> str:
    numbers = []
    for action in ACTIONS_STORE:
        action_id = str(action.get("id", ""))
        if action_id.startswith("ACT-") and action_id[4:].isdigit():
            numbers.append(int(action_id[4:]))
    return f"ACT-{max(numbers, default=0) + 1:03d}"


def _find_action(action_id: str, user: Dict[str, Any]) -> Dict[str, Any]:
    """Another organization's action is reported exactly like one that does not exist."""
    action = next(
        (item for item in ACTIONS_STORE if item.get("id") == action_id and can_access(user, item)), None
    )
    if action is None:
        raise HTTPException(status_code=404, detail=f"Action '{action_id}' not found")
    return action


def _require_pending_action(action: Dict[str, Any]) -> None:
    if action.get("status") != "PENDING_APPROVAL":
        raise HTTPException(
            status_code=409,
            detail=f"Action cannot be decided from status '{action.get('status', 'UNKNOWN')}'.",
        )
    expires_at = action.get("expires_at")
    if expires_at:
        try:
            expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=500, detail="Action has an invalid expiry timestamp.") from exc
        if expiry <= datetime.now(timezone.utc):
            action["status"] = "EXPIRED"
            _record_audit("system", "ACTION_EXPIRED", str(action.get("target_entity", "")), "EXPIRED", str(action.get("id", "")), org_id=record_org(action))
            raise HTTPException(status_code=409, detail="Action approval has expired. Re-submission required.")


@router.get("/api/response/actions")
@router.get("/api/v1/response/actions")
def list_response_actions(
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("audit:read")),
):
    visible = scope(current_user, ACTIONS_STORE)
    return {"total": len(visible), "actions": visible}

def list_response_actions(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {"total": len(ACTIONS_STORE), "actions": ACTIONS_STORE}

@router.post("/api/response/isolate-host")
@router.post("/api/v1/response/isolate-host")
def request_host_isolation(
    payload: HostIsolationRequest,
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("response:isolate_host")),
):
    hostname = payload.hostname.strip()
    if not hostname or len(hostname) > 253:
        raise HTTPException(status_code=422, detail="Hostname must contain 1 to 253 characters.")
    ip_address = _validate_ip(payload.ip_address)
    reason = _require_reason(payload.reason)
    if not payload.require_approval and not payload.dry_run:
        raise HTTPException(status_code=400, detail="Destructive response actions must require human approval.")

    now = datetime.now(timezone.utc)
    action_id = _next_action_id()
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
        "org_id": org_of(current_user),
        "incident_number": payload.incident_number,
        "action_type": "ISOLATE_HOST",
        "target_entity": f"{hostname} ({ip_address or 'DHCP'})",
        "recommended_by": _operator_name(current_user),
        "requested_by_id": _user_key(current_user),
        "reasoning": reason,
        "confidence": 95,
        "status": "DRY_RUN_SIMULATED" if payload.dry_run else "PENDING_APPROVAL",
        "dry_run": bool(payload.dry_run),
        "target_entity": f"{payload.hostname} ({payload.ip_address or 'DHCP'})",
        "requested_by": user_email,
        "recommended_by": "ANALYST_REQUEST",
        "reasoning": payload.reason,
        "confidence": 95,
        "status": status_str,
        "dry_run": is_dry_run,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat(),
    }
    ACTIONS_STORE.insert(0, action)
    operator = _operator_name(current_user)
    _record_audit(operator, f"ISOLATE_HOST_{'DRY_RUN' if payload.dry_run else 'SUBMITTED'}", hostname, "SIMULATED" if payload.dry_run else "PENDING", reason, org_id=org_of(current_user))
    return {"status": "SIMULATED" if payload.dry_run else "QUEUED", "dry_run": bool(payload.dry_run), "action_id": action_id, "action": action}

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
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("response:block_ip")),
):
    ip_address = _validate_ip(payload.ip_address, required=True)
    reason = _require_reason(payload.reason)
    direction = (payload.direction or "BOTH").strip().upper()
    if direction not in {"INGRESS", "EGRESS", "BOTH"}:
        raise HTTPException(status_code=422, detail="Direction must be INGRESS, EGRESS, or BOTH.")
    if not payload.require_approval and not payload.dry_run:
        raise HTTPException(status_code=400, detail="Destructive response actions must require human approval.")

    now = datetime.now(timezone.utc)
    action_id = _next_action_id()
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
        "org_id": org_of(current_user),
        "incident_number": payload.incident_number,
        "action_type": "BLOCK_IP",
        "target_entity": ip_address,
        "direction": direction,
        "recommended_by": _operator_name(current_user),
        "requested_by_id": _user_key(current_user),
        "reasoning": reason,
        "confidence": 99,
        "status": "DRY_RUN_SIMULATED" if payload.dry_run else "PENDING_APPROVAL",
        "dry_run": bool(payload.dry_run),
        "target_entity": payload.ip_address,
        "requested_by": user_email,
        "recommended_by": "ANALYST_REQUEST",
        "reasoning": payload.reason,
        "confidence": 99,
        "status": status_str,
        "dry_run": is_dry_run,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat(),
    }
    ACTIONS_STORE.insert(0, action)
    operator = _operator_name(current_user)
    _record_audit(operator, f"BLOCK_IP_{'DRY_RUN' if payload.dry_run else 'SUBMITTED'}", ip_address, "SIMULATED" if payload.dry_run else "PENDING", reason, org_id=org_of(current_user))
    return {"status": "SIMULATED" if payload.dry_run else "QUEUED", "dry_run": bool(payload.dry_run), "action_id": action_id, "action": action}

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
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("user:admin")),
):
    username = payload.username.strip()
    domain = (payload.domain or "cbe.internal").strip()
    if not username or len(username) > 256 or not domain or len(domain) > 253:
        raise HTTPException(status_code=422, detail="A valid username and domain are required.")
    reason = _require_reason(payload.reason)
    if not payload.require_approval and not payload.dry_run:
        raise HTTPException(status_code=400, detail="Destructive response actions must require human approval.")

    now = datetime.now(timezone.utc)
    action_id = _next_action_id()
    target = f"{username}@{domain}"
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
        "org_id": org_of(current_user),
        "incident_number": payload.incident_number,
        "action_type": "DISABLE_ACCOUNT",
        "target_entity": target,
        "recommended_by": _operator_name(current_user),
        "requested_by_id": _user_key(current_user),
        "reasoning": reason,
        "confidence": 90,
        "status": "DRY_RUN_SIMULATED" if payload.dry_run else "PENDING_APPROVAL",
        "dry_run": bool(payload.dry_run),
        "target_entity": f"{payload.username}@{payload.domain}",
        "requested_by": user_email,
        "recommended_by": "ANALYST_REQUEST",
        "reasoning": payload.reason,
        "confidence": 90,
        "status": status_str,
        "dry_run": is_dry_run,
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat(),
    }
    ACTIONS_STORE.insert(0, action)
    operator = _operator_name(current_user)
    _record_audit(operator, f"DISABLE_ACCOUNT_{'DRY_RUN' if payload.dry_run else 'SUBMITTED'}", target, "SIMULATED" if payload.dry_run else "PENDING", reason, org_id=org_of(current_user))
    return {"status": "SIMULATED" if payload.dry_run else "QUEUED", "dry_run": bool(payload.dry_run), "action_id": action_id, "action": action}

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
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("response:approve")),
):
    action = _find_action(action_id, current_user)
    _require_pending_action(action)
    if action.get("requested_by_id") and action["requested_by_id"] == _user_key(current_user):
        raise HTTPException(
            status_code=403,
            detail="Dual-custody control: the requester cannot approve their own action.",
        )
    reason = _require_reason(payload.reason)
    operator = _operator_name(current_user)
    action["status"] = "APPROVED"
    action["executed_at"] = datetime.now(timezone.utc).isoformat()
    action["reviewed_by"] = operator
    _record_audit(operator, f"ACTION_APPROVED_{action['action_type']}", action["target_entity"], "SUCCESS", f"Approved for {action.get('incident_number')}: {reason}", org_id=org_of(current_user))
    return {"status": "SUCCESS", "message": f"Action {action_id} ({action['action_type']}) approved by the SOAR workflow.", "action": action}

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
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("response:approve")),
):
    action = _find_action(action_id, current_user)
    _require_pending_action(action)
    reason = _require_reason(payload.reason)
    operator = _operator_name(current_user)
    action["status"] = "REJECTED"
    action["rejection_reason"] = reason
    action["reviewed_by"] = operator
    action["rejected_at"] = datetime.now(timezone.utc).isoformat()
    _record_audit(operator, f"ACTION_REJECTED_{action['action_type']}", action["target_entity"], "REJECTED", reason, org_id=org_of(current_user))
    return {"status": "SUCCESS", "message": f"Action {action_id} rejected.", "action": action}

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
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("response:approve")),
):
    action = _find_action(action_id, current_user)
    if action.get("status") != "APPROVED" or action.get("dry_run"):
        raise HTTPException(status_code=409, detail="Only approved, non-dry-run actions can be rolled back.")
    reason = _require_reason(payload.reason)
    operator = _operator_name(current_user)
    action["status"] = "ROLLED_BACK"
    action["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
    action["rollback_reason"] = reason
    _record_audit(operator, f"ACTION_ROLLED_BACK_{action['action_type']}", action["target_entity"], "SUCCESS", reason, org_id=org_of(current_user))
    return {"status": "SUCCESS", "message": f"Action {action_id} was marked rolled back.", "action": action}


@router.get("/api/response/audit-log")
@router.get("/api/v1/response/audit-log")
def get_response_audit_log(
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("audit:read")),
):
    visible = scope(current_user, AUDIT_LOG_STORE)
    return {"total": len(visible), "audit_logs": visible}


@router.get("/api/response/audit-log/verify")
@router.get("/api/v1/response/audit-log/verify")
def verify_response_audit_log(
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("audit:read")),
):
    """Recompute the SHA-256 hash chain and report any tampered or re-ordered entries.

    The chain is one tamper-evident sequence for the whole platform, so it is always checked in
    full. An organization is told whether the chain is intact and which of ITS OWN entries are
    broken; it never learns the ids or number of other organizations' entries.
    """
    result = verify_audit_chain(AUDIT_LOG_STORE)
    if is_global(current_user):
        return result
    mine = {str(entry.get("id")) for entry in scope(current_user, AUDIT_LOG_STORE)}
    return {
        "valid": result["valid"],
        "entries": len(mine),
        "broken_entries": [entry_id for entry_id in result["broken_entries"] if entry_id in mine],
    }


def verify_audit_chain(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Verify an audit log stored newest-first. The oldest entry is the genesis anchor."""
    ordered = list(reversed(entries))
    broken: List[str] = []
    for index, entry in enumerate(ordered):
        if index == 0:
            continue
        previous = ordered[index - 1]
        expected = hashlib.sha256(
            "|".join(
                [
                    str(entry.get("prev_hash")),
                    str(entry.get("operator")),
                    str(entry.get("action")),
                    str(entry.get("target")),
                    str(entry.get("result")),
                    str(entry.get("timestamp")),
                ]
            ).encode("utf-8")
        ).hexdigest()
        if entry.get("prev_hash") != previous.get("integrity_hash") or entry.get("integrity_hash") != expected:
            broken.append(str(entry.get("id")))
    return {"valid": not broken, "entries": len(entries), "broken_entries": broken}


_DEMO_SEED_ACTION_IDS = {"ACT-001", "ACT-002"}


def _rearm_demo_seed_actions() -> None:
    """Demo only: keep untouched seed recommendations approvable after a restart."""
    if not DEMO_MODE:
        return
    for action in ACTIONS_STORE:
        if (
            action.get("id") in _DEMO_SEED_ACTION_IDS
            and action.get("status") in ("PENDING_APPROVAL", "EXPIRED")
            and not action.get("reviewed_by")
        ):
            action["status"] = "PENDING_APPROVAL"
            action["expires_at"] = (datetime.now(timezone.utc) + timedelta(minutes=30)).isoformat()


# Durable storage: restored at API startup (see database/state_store.py)
state_store.register("response_actions", ACTIONS_STORE)
state_store.register("audit_log", AUDIT_LOG_STORE)
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
