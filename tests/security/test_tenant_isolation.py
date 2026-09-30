"""
Security Tests: Multi-Tenancy Boundary Isolation and Dual-Custody Bypass Protection
"""

import pytest
from services.security.rbac import TenantSecurityManager, RBACManager, Role, Permission

def test_tenant_cross_access_prevention():
    # User from CBE (org_cbe) cannot access Awash Bank (org_awash) records
    assert TenantSecurityManager.can_access_tenant(
        user_org_id="org_cbe_01",
        target_org_id="org_awash_02",
        user_role=Role.SOC_ANALYST
    ) is False

    # Same organization access is permitted
    assert TenantSecurityManager.can_access_tenant(
        user_org_id="org_cbe_01",
        target_org_id="org_cbe_01",
        user_role=Role.SOC_ANALYST
    ) is True

    # SUPER_ADMIN has national cross-tenant oversight
    assert TenantSecurityManager.can_access_tenant(
        user_org_id="org_insa_national",
        target_org_id="org_cbe_01",
        user_role=Role.SUPER_ADMIN
    ) is True

def test_tenant_dataset_filtering():
    incidents = [
        {"id": "inc_01", "org_id": "org_cbe_01", "title": "CBE Incident"},
        {"id": "inc_02", "org_id": "org_awash_02", "title": "Awash Incident"}
    ]

    filtered = TenantSecurityManager.filter_by_tenant(
        items=incidents,
        user_org_id="org_cbe_01",
        user_role=Role.SOC_ANALYST
    )
    assert len(filtered) == 1
    assert filtered[0]["id"] == "inc_01"

def test_soar_dual_custody_bypass_prevention():
    # Analyst cannot self-approve destructive host isolation
    assert RBACManager.verify_dual_custody(
        requester_role=Role.SOC_ANALYST,
        approver_role=Role.SOC_ANALYST,
        action_permission=Permission.EXECUTE_HOST_ISOLATION
    ) is False
