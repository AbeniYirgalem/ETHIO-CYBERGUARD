"""SOAR human-in-the-loop approval lifecycle management."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid


class ApprovalManager:
    """Manage approval requests with single-decision state transitions."""

    def __init__(self):
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _required_text(value: str, field: str, max_length: int = 2000) -> str:
        cleaned = (value or "").strip()
        if not cleaned:
            raise ValueError(f"{field} must not be empty.")
        if len(cleaned) > max_length:
            raise ValueError(f"{field} must be {max_length} characters or fewer.")
        return cleaned

    def submit_request(
        self,
        action_type: str,
        target: str,
        incident_number: str,
        recommended_by: str,
        reasoning: str,
        confidence: int,
    ) -> Dict[str, Any]:
        action_type = self._required_text(action_type, "action_type", 100).upper()
        target = self._required_text(target, "target", 512)
        incident_number = self._required_text(incident_number, "incident_number", 100)
        recommended_by = self._required_text(recommended_by, "recommended_by", 256)
        reasoning = self._required_text(reasoning, "reasoning")
        if isinstance(confidence, bool) or not isinstance(confidence, int) or not 0 <= confidence <= 100:
            raise ValueError("confidence must be an integer between 0 and 100.")

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
            "decision_reason": None,
        }
        self.pending_approvals[req_id] = approval_item
        return approval_item

    def _get_pending(self, req_id: str) -> Dict[str, Any]:
        req = self.pending_approvals.get(req_id)
        if req is None:
            raise ValueError(f"Approval request '{req_id}' not found.")
        if req.get("status") != "PENDING_APPROVAL":
            raise ValueError(
                f"Approval request '{req_id}' has already been decided: {req.get('status', 'UNKNOWN')}."
            )
        return req

    def approve(
        self,
        req_id: str,
        approver_name: str,
        approver_role: str,
        reason: str = "Authorized by SOC Analyst",
    ) -> Dict[str, Any]:
        req = self._get_pending(req_id)
        approver_name = self._required_text(approver_name, "approver_name", 256)
        approver_role = self._required_text(approver_role, "approver_role", 128)
        reason = self._required_text(reason, "reason")
        req["status"] = "APPROVED"
        req["approver"] = f"{approver_name} ({approver_role})"
        req["decision_reason"] = reason
        req["decided_at"] = datetime.now(timezone.utc).isoformat()
        return req

    def reject(
        self, req_id: str, approver_name: str, approver_role: str, reason: str
    ) -> Dict[str, Any]:
        req = self._get_pending(req_id)
        approver_name = self._required_text(approver_name, "approver_name", 256)
        approver_role = self._required_text(approver_role, "approver_role", 128)
        reason = self._required_text(reason, "reason")
        req["status"] = "REJECTED"
        req["approver"] = f"{approver_name} ({approver_role})"
        req["decision_reason"] = reason
        req["decided_at"] = datetime.now(timezone.utc).isoformat()
        return req
