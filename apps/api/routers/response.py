"""
ETHIO-CYBERGUARD SOAR Response Router
Provides human-in-the-loop containment action approvals, dry-run mode, rollback,
host isolation, IP blocking, account disablement, and immutable SHA-256 audit logging.
Supports /api/response and /api/v1/response.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
import hashlib
import ipaddress
import uuid

from ..dependencies import require_permission, get_current_user, security

router = APIRouter(tags=["SOAR Containment & Automated Response"])


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

def _operator_name(user: Dict[str, Any]) -> str:
    """Use the authenticated identity for audit records, never client-supplied names."""
    return str(user.get("name") or user.get("email") or user.get("id") or "unknown")


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


def _find_action(action_id: str) -> Dict[str, Any]:
    action = next((item for item in ACTIONS_STORE if item.get("id") == action_id), None)
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
            _record_audit("system", "ACTION_EXPIRED", str(action.get("target_entity", "")), "EXPIRED", str(action.get("id", "")))
            raise HTTPException(status_code=409, detail="Action approval has expired. Re-submission required.")


@router.get("/api/response/actions")
@router.get("/api/v1/response/actions")
def list_response_actions(
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("audit:read")),
):
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
    action = {
        "id": action_id,
        "incident_number": payload.incident_number,
        "action_type": "ISOLATE_HOST",
        "target_entity": f"{hostname} ({ip_address or 'DHCP'})",
        "recommended_by": _operator_name(current_user),
        "reasoning": reason,
        "confidence": 95,
        "status": "DRY_RUN_SIMULATED" if payload.dry_run else "PENDING_APPROVAL",
        "dry_run": bool(payload.dry_run),
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat(),
    }
    ACTIONS_STORE.insert(0, action)
    operator = _operator_name(current_user)
    _record_audit(operator, f"ISOLATE_HOST_{'DRY_RUN' if payload.dry_run else 'SUBMITTED'}", hostname, "SIMULATED" if payload.dry_run else "PENDING", reason)
    return {"status": "SIMULATED" if payload.dry_run else "QUEUED", "dry_run": bool(payload.dry_run), "action_id": action_id, "action": action}


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
    action = {
        "id": action_id,
        "incident_number": payload.incident_number,
        "action_type": "BLOCK_IP",
        "target_entity": ip_address,
        "direction": direction,
        "recommended_by": _operator_name(current_user),
        "reasoning": reason,
        "confidence": 99,
        "status": "DRY_RUN_SIMULATED" if payload.dry_run else "PENDING_APPROVAL",
        "dry_run": bool(payload.dry_run),
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat(),
    }
    ACTIONS_STORE.insert(0, action)
    operator = _operator_name(current_user)
    _record_audit(operator, f"BLOCK_IP_{'DRY_RUN' if payload.dry_run else 'SUBMITTED'}", ip_address, "SIMULATED" if payload.dry_run else "PENDING", reason)
    return {"status": "SIMULATED" if payload.dry_run else "QUEUED", "dry_run": bool(payload.dry_run), "action_id": action_id, "action": action}


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
    action = {
        "id": action_id,
        "incident_number": payload.incident_number,
        "action_type": "DISABLE_ACCOUNT",
        "target_entity": target,
        "recommended_by": _operator_name(current_user),
        "reasoning": reason,
        "confidence": 90,
        "status": "DRY_RUN_SIMULATED" if payload.dry_run else "PENDING_APPROVAL",
        "dry_run": bool(payload.dry_run),
        "expires_at": (now + timedelta(minutes=30)).isoformat(),
        "created_at": now.isoformat(),
    }
    ACTIONS_STORE.insert(0, action)
    operator = _operator_name(current_user)
    _record_audit(operator, f"DISABLE_ACCOUNT_{'DRY_RUN' if payload.dry_run else 'SUBMITTED'}", target, "SIMULATED" if payload.dry_run else "PENDING", reason)
    return {"status": "SIMULATED" if payload.dry_run else "QUEUED", "dry_run": bool(payload.dry_run), "action_id": action_id, "action": action}


@router.post("/api/response/actions/{action_id}/approve")
@router.post("/api/v1/response/actions/{action_id}/approve")
def approve_action(
    action_id: str,
    payload: ActionDecisionPayload,
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("response:approve")),
):
    action = _find_action(action_id)
    _require_pending_action(action)
    reason = _require_reason(payload.reason)
    operator = _operator_name(current_user)
    action["status"] = "APPROVED"
    action["executed_at"] = datetime.now(timezone.utc).isoformat()
    action["reviewed_by"] = operator
    _record_audit(operator, f"ACTION_APPROVED_{action['action_type']}", action["target_entity"], "SUCCESS", f"Approved for {action.get('incident_number')}: {reason}")
    return {"status": "SUCCESS", "message": f"Action {action_id} ({action['action_type']}) approved by the SOAR workflow.", "action": action}


@router.post("/api/response/actions/{action_id}/reject")
@router.post("/api/v1/response/actions/{action_id}/reject")
def reject_action(
    action_id: str,
    payload: ActionDecisionPayload,
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("response:approve")),
):
    action = _find_action(action_id)
    _require_pending_action(action)
    reason = _require_reason(payload.reason)
    operator = _operator_name(current_user)
    action["status"] = "REJECTED"
    action["rejection_reason"] = reason
    action["reviewed_by"] = operator
    action["rejected_at"] = datetime.now(timezone.utc).isoformat()
    _record_audit(operator, f"ACTION_REJECTED_{action['action_type']}", action["target_entity"], "REJECTED", reason)
    return {"status": "SUCCESS", "message": f"Action {action_id} rejected.", "action": action}


@router.post("/api/response/actions/{action_id}/rollback")
@router.post("/api/v1/response/actions/{action_id}/rollback")
def rollback_action(
    action_id: str,
    payload: ActionDecisionPayload,
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("response:approve")),
):
    action = _find_action(action_id)
    if action.get("status") != "APPROVED" or action.get("dry_run"):
        raise HTTPException(status_code=409, detail="Only approved, non-dry-run actions can be rolled back.")
    reason = _require_reason(payload.reason)
    operator = _operator_name(current_user)
    action["status"] = "ROLLED_BACK"
    action["rolled_back_at"] = datetime.now(timezone.utc).isoformat()
    action["rollback_reason"] = reason
    _record_audit(operator, f"ACTION_ROLLED_BACK_{action['action_type']}", action["target_entity"], "SUCCESS", reason)
    return {"status": "SUCCESS", "message": f"Action {action_id} was marked rolled back.", "action": action}


@router.get("/api/response/audit-log")
@router.get("/api/v1/response/audit-log")
def get_response_audit_log(
    current_user: Dict[str, Any] = Depends(_require_authenticated_permission("audit:read")),
):
    return {"total": len(AUDIT_LOG_STORE), "audit_logs": AUDIT_LOG_STORE}
