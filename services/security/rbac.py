"""
ETHIO-CYBERGUARD Role-Based Access Control (RBAC) & Multi-Tenancy Isolation
Defines strict privilege tiers:
- SUPER_ADMIN: Full platform administration across all tenants.
- ORG_ADMIN: Organization administrator (manage tenant users and assets).
- SOC_MANAGER / INCIDENT_COMMANDER: Dual-custody authorization for host isolation and network blocking.
- SOC_ANALYST / SECURITY_ENGINEER: Triage alerts, run OSINT scans, inspect phishing, request containment.
- AUDITOR: Read-only access to immutable audit trails and compliance reports.
- VIEWER: Read-only visibility to high-level dashboards.
"""

from typing import Dict, Any, List, Set, Optional
from enum import Enum

class Role(str, Enum):
    # Core Enterprise Roles
    SUPER_ADMIN = "SUPER_ADMIN"
    ORG_ADMIN = "ORG_ADMIN"
    SOC_MANAGER = "SOC_MANAGER"
    SOC_ANALYST = "SOC_ANALYST"
    SECURITY_ENGINEER = "SECURITY_ENGINEER"
    AUDITOR = "AUDITOR"
    VIEWER = "VIEWER"
    
    # Aliases for Tier-based operations
    ANALYST_TIER_1 = "ANALYST_TIER_1"
    ANALYST_TIER_2 = "ANALYST_TIER_2"
    INCIDENT_COMMANDER = "INCIDENT_COMMANDER"
    SOC_ADMIN = "SOC_ADMIN"

class Permission(str, Enum):
    # Read permissions
    VIEW_ALERTS = "VIEW_ALERTS"
    VIEW_INCIDENTS = "VIEW_INCIDENTS"
    RUN_OSINT_RECON = "RUN_OSINT_RECON"
    VIEW_THREAT_INTEL = "VIEW_THREAT_INTEL"
    VIEW_AUDIT_LOGS = "VIEW_AUDIT_LOGS"
    
    # Write / Triage
    ASSIGN_INCIDENTS = "ASSIGN_INCIDENTS"
    UPDATE_INCIDENT_STATE = "UPDATE_INCIDENT_STATE"
    ATTACH_EVIDENCE = "ATTACH_EVIDENCE"
    
    # High-Impact Containment Actions (Dual-Custody)
    EXECUTE_HOST_ISOLATION = "EXECUTE_HOST_ISOLATION"
    EXECUTE_FIREWALL_BLOCK = "EXECUTE_FIREWALL_BLOCK"
    EXECUTE_ACCOUNT_DISABLE = "EXECUTE_ACCOUNT_DISABLE"
    EXECUTE_DNS_SINKHOLE = "EXECUTE_DNS_SINKHOLE"
    SUBMIT_REGISTRAR_TAKEDOWN = "SUBMIT_REGISTRAR_TAKEDOWN"
    
    # Administrative
    MANAGE_USERS = "MANAGE_USERS"
    MANAGE_DETECTION_RULES = "MANAGE_DETECTION_RULES"
    PURGE_AUDIT_LOGS = "PURGE_AUDIT_LOGS" # Strictly prohibited for tamper resistance

ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.VIEWER: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.VIEW_THREAT_INTEL
    },
    Role.AUDITOR: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.VIEW_THREAT_INTEL,
        Permission.VIEW_AUDIT_LOGS
    },
    Role.ANALYST_TIER_1: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.ATTACH_EVIDENCE
    },
    Role.SOC_ANALYST: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.ASSIGN_INCIDENTS,
        Permission.UPDATE_INCIDENT_STATE,
        Permission.ATTACH_EVIDENCE,
        Permission.EXECUTE_ACCOUNT_DISABLE,
        Permission.SUBMIT_REGISTRAR_TAKEDOWN
    },
    Role.ANALYST_TIER_2: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.ASSIGN_INCIDENTS,
        Permission.UPDATE_INCIDENT_STATE,
        Permission.ATTACH_EVIDENCE,
        Permission.EXECUTE_ACCOUNT_DISABLE,
        Permission.SUBMIT_REGISTRAR_TAKEDOWN
    },
    Role.SECURITY_ENGINEER: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.ASSIGN_INCIDENTS,
        Permission.UPDATE_INCIDENT_STATE,
        Permission.ATTACH_EVIDENCE,
        Permission.MANAGE_DETECTION_RULES,
        Permission.EXECUTE_DNS_SINKHOLE
    },
    Role.INCIDENT_COMMANDER: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.ASSIGN_INCIDENTS,
        Permission.UPDATE_INCIDENT_STATE,
        Permission.ATTACH_EVIDENCE,
        Permission.EXECUTE_ACCOUNT_DISABLE,
        Permission.SUBMIT_REGISTRAR_TAKEDOWN,
        Permission.EXECUTE_HOST_ISOLATION,
        Permission.EXECUTE_FIREWALL_BLOCK,
        Permission.EXECUTE_DNS_SINKHOLE,
        Permission.VIEW_AUDIT_LOGS
    },
    Role.SOC_MANAGER: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.ASSIGN_INCIDENTS,
        Permission.UPDATE_INCIDENT_STATE,
        Permission.ATTACH_EVIDENCE,
        Permission.EXECUTE_ACCOUNT_DISABLE,
        Permission.SUBMIT_REGISTRAR_TAKEDOWN,
        Permission.EXECUTE_HOST_ISOLATION,
        Permission.EXECUTE_FIREWALL_BLOCK,
        Permission.EXECUTE_DNS_SINKHOLE,
        Permission.VIEW_AUDIT_LOGS,
        Permission.MANAGE_USERS
    },
    Role.ORG_ADMIN: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.MANAGE_USERS,
        Permission.MANAGE_DETECTION_RULES,
        Permission.VIEW_AUDIT_LOGS
    },
    Role.SOC_ADMIN: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.ASSIGN_INCIDENTS,
        Permission.UPDATE_INCIDENT_STATE,
        Permission.ATTACH_EVIDENCE,
        Permission.EXECUTE_ACCOUNT_DISABLE,
        Permission.SUBMIT_REGISTRAR_TAKEDOWN,
        Permission.EXECUTE_HOST_ISOLATION,
        Permission.EXECUTE_FIREWALL_BLOCK,
        Permission.EXECUTE_DNS_SINKHOLE,
        Permission.MANAGE_USERS,
        Permission.MANAGE_DETECTION_RULES,
        Permission.VIEW_AUDIT_LOGS
    },
    Role.SUPER_ADMIN: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.ASSIGN_INCIDENTS,
        Permission.UPDATE_INCIDENT_STATE,
        Permission.ATTACH_EVIDENCE,
        Permission.EXECUTE_ACCOUNT_DISABLE,
        Permission.SUBMIT_REGISTRAR_TAKEDOWN,
        Permission.EXECUTE_HOST_ISOLATION,
        Permission.EXECUTE_FIREWALL_BLOCK,
        Permission.EXECUTE_DNS_SINKHOLE,
        Permission.MANAGE_USERS,
        Permission.MANAGE_DETECTION_RULES,
        Permission.VIEW_AUDIT_LOGS
    }
}

class RBACManager:
    """Enforces authorization checks on SOC user actions."""

    @staticmethod
    def has_permission(user_role: Role, required_permission: Permission) -> bool:
        allowed = ROLE_PERMISSIONS.get(user_role, set())
        return required_permission in allowed

    @staticmethod
    def verify_dual_custody(
        requester_role: Role,
        approver_role: Role,
        action_permission: Permission
    ) -> bool:
        """
        High-impact containment (Host Isolation, Firewall Drop) requires dual custody:
        Requester cannot be Tier 1.
        Approver must be Incident Commander, SOC Manager, or Admin.
        Requester and approver must not be the same role/person.
        """
        if requester_role == Role.ANALYST_TIER_1:
            return False
        if requester_role == approver_role:
            return False
        privileged = {Role.INCIDENT_COMMANDER, Role.SOC_MANAGER, Role.SOC_ADMIN, Role.SUPER_ADMIN}
        return approver_role in privileged

    @staticmethod
    def validate_dual_custody(action: str, primary_role: Role, secondary_role: Role) -> bool:
        return RBACManager.verify_dual_custody(primary_role, secondary_role, Permission.EXECUTE_HOST_ISOLATION)

class TenantSecurityManager:
    """Enforces strict multi-tenancy isolation between organizations."""

    @staticmethod
    def can_access_tenant(user_org_id: str, target_org_id: str, user_role: Role) -> bool:
        # SUPER_ADMIN has platform-wide authority
        if user_role == Role.SUPER_ADMIN:
            return True
        # All other users are strictly restricted to their own organization
        return user_org_id == target_org_id

    @staticmethod
    def filter_by_tenant(items: List[Dict[str, Any]], user_org_id: str, user_role: Role) -> List[Dict[str, Any]]:
        if user_role == Role.SUPER_ADMIN:
            return items
        return [i for i in items if i.get("org_id") == user_org_id or i.get("organization") == user_org_id]
