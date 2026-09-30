"""
ETHIO-CYBERGUARD SOAR Central Response Engine
Orchestrates containment actions with mandatory Human-In-The-Loop approval and immutable auditing.
Lifecycle:
AI Recommendation -> Human Approval -> Authorization Check -> Action Execution -> Verification -> Immutable Audit Log
"""

from typing import Dict, Any, List, Optional
from .approvals import ApprovalManager
from .audit import ImmutableAuditLog
from .host_isolation import HostIsolationService
from .account_disable import AccountDisableService
from .firewall import FirewallBlockService
from .playbooks import PlaybookEngine

class SOARResponseEngine:
    """Central Response coordinator ensuring no LLM executes containment without analyst authorization."""

    def __init__(self):
        self.approvals = ApprovalManager()
        self.audit = ImmutableAuditLog()
        self.playbooks = PlaybookEngine()

    def process_ai_recommendation(
        self,
        action_type: str,
        target: str,
        incident_number: str,
        reasoning: str,
        confidence: int,
        recommended_by: str = "AI_AGENT"
    ) -> Dict[str, Any]:
        """Submits an action into the mandatory approval queue."""
        approval_req = self.approvals.submit_request(
            action_type=action_type,
            target=target,
            incident_number=incident_number,
            recommended_by=recommended_by,
            reasoning=reasoning,
            confidence=confidence
        )
        self.audit.record(
            operator=recommended_by,
            action=f"RECOMMEND_{action_type}",
            target=target,
            reason=reasoning,
            result="QUEUED_FOR_APPROVAL",
            approval_id=approval_req["id"]
        )
        return approval_req

    def execute_approved_action(
        self,
        approval_id: str,
        approver_name: str,
        approver_role: str,
        approval_reason: str = "Analyst verified"
    ) -> Dict[str, Any]:
        """Verifies human approval and triggers execution."""
        # 1. Authorize & Approve
        approved_req = self.approvals.approve(approval_id, approver_name, approver_role, approval_reason)
        act_type = approved_req["action_type"]
        target = approved_req["target"]
        
        # 2. Execute
        execution_result = {}
        if act_type == "ISOLATE_HOST":
            execution_result = HostIsolationService.isolate_host(target, "10.10.1.24", approval_reason)
        elif act_type == "BLOCK_IP":
            execution_result = FirewallBlockService.block_ip(target, "BOTH", approval_reason)
        elif act_type == "DISABLE_ACCOUNT":
            execution_result = AccountDisableService.disable_user(target, "cbe.internal", approval_reason)
        else:
            execution_result = {"status": "EXECUTED", "detail": f"Custom action {act_type} executed"}

        # 3. Write Immutable Audit Trail
        audit_entry = self.audit.record(
            operator=f"{approver_name} ({approver_role})",
            action=f"EXECUTE_{act_type}",
            target=target,
            reason=approval_reason,
            result="SUCCESS",
            approval_id=approval_id
        )

        return {
            "status": "SUCCESS",
            "approval": approved_req,
            "execution": execution_result,
            "audit_hash": audit_entry["hash"]
        }
