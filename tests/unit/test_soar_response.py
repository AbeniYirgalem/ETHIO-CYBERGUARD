"""
Unit test for SOAR Response Engine
Verifies human-in-the-loop approval, execution, and audit hash chain integrity.
"""

from services.response.engine import SOARResponseEngine

def test_soar_approval_and_execution_lifecycle():
    soar = SOARResponseEngine()
    
    # 1. AI agent submits recommendation
    req = soar.process_ai_recommendation(
        action_type="ISOLATE_HOST",
        target="SERVER-04",
        incident_number="INC-00042",
        reasoning="Cobalt strike beacon confirmed",
        confidence=94,
        recommended_by="AI_RISK_AGENT"
    )
    assert req["status"] == "PENDING_APPROVAL"
    appr_id = req["id"]

    # 2. Human analyst approves and executes
    result = soar.execute_approved_action(
        approval_id=appr_id,
        approver_name="Dawit Mengistu",
        approver_role="Incident Commander",
        approval_reason="Verified beacon egress with network team"
    )
    assert result["status"] == "SUCCESS"
    assert result["execution"]["status"] == "ISOLATED"
    assert result["execution"]["quarantine_profile"] == "SOC_EDR_ONLY_CHANNEL"

    # 3. Verify audit integrity
    assert soar.audit.verify_integrity() is True
