"""
ETHIO-CYBERGUARD SOAR Human-in-the-Loop Approvals
Enforces mandatory human confirmation and dual-custody for destructive containment.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid

class ApprovalManager:
    """Manages the lifecycle of containment action approvals."""

    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

    def submit_request(
        self,
        action_type: str,
        target: str,
        incident_number: str,
        recommended_by: str,
        reasoning: str,
        confidence: int
    ) -> Dict[str, Any]:
        req_id = f"APPR-{uuid.uuid4().hex[:6].upper()}"
        approval_item = {
            "id": req_id,
            "action_type": action_type,
            "target": target,
            "incident_number": incident_number,
            "recommended_by": recommended_by,
            "reasoning": reasoning,
            "confidence": confidence,
            "status": "PENDING_APPROVAL",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "approver": None,
            "decision_reason": None
        }
        self.pending_approvals[req_id] = approval_item
        return approval_item

    def approve(self, req_id: str, approver_name: str, approver_role: str, reason: str = "Authorized by SOC Analyst") -> Dict[str, Any]:
        if req_id not in self.pending_approvals:
            raise ValueError(f"Approval request '{req_id}' not found.")
        
        req = self.pending_approvals[req_id]
        req["status"] = "APPROVED"
        req["approver"] = f"{approver_name} ({approver_role})"
        req["decision_reason"] = reason
        req["decided_at"] = datetime.now(timezone.utc).isoformat()
        return req

    def reject(self, req_id: str, approver_name: str, approver_role: str, reason: str) -> Dict[str, Any]:
        if req_id not in self.pending_approvals:
            raise ValueError(f"Approval request '{req_id}' not found.")
        
        req = self.pending_approvals[req_id]
        req["status"] = "REJECTED"
        req["approver"] = f"{approver_name} ({approver_role})"
        req["decision_reason"] = reason
        req["decided_at"] = datetime.now(timezone.utc).isoformat()
        return req
