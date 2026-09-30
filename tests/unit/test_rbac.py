from services.security.rbac import RBACManager, Role, Permission

def test_tier_1_analyst_permissions():
    assert RBACManager.has_permission(Role.ANALYST_TIER_1, Permission.VIEW_INCIDENTS) is True
    assert RBACManager.has_permission(Role.ANALYST_TIER_1, Permission.RUN_OSINT_RECON) is True
    # Tier 1 cannot execute destructive containment
    assert RBACManager.has_permission(Role.ANALYST_TIER_1, Permission.EXECUTE_HOST_ISOLATION) is False
    assert RBACManager.has_permission(Role.ANALYST_TIER_1, Permission.EXECUTE_FIREWALL_BLOCK) is False

def test_dual_custody_validation():
    # Tier 1 cannot request or approve host isolation
    assert RBACManager.verify_dual_custody(
        requester_role=Role.ANALYST_TIER_1,
        approver_role=Role.INCIDENT_COMMANDER,
        action_permission=Permission.EXECUTE_HOST_ISOLATION
    ) is False

    # Tier 2 request + Incident Commander approval is valid
    assert RBACManager.verify_dual_custody(
        requester_role=Role.ANALYST_TIER_2,
        approver_role=Role.INCIDENT_COMMANDER,
        action_permission=Permission.EXECUTE_HOST_ISOLATION
    ) is True

    # Tier 2 cannot approve another Tier 2 for host isolation
    assert RBACManager.verify_dual_custody(
        requester_role=Role.ANALYST_TIER_2,
        approver_role=Role.ANALYST_TIER_2,
        action_permission=Permission.EXECUTE_HOST_ISOLATION
    ) is False
