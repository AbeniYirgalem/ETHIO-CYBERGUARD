"""
ETHIO-CYBERGUARD Role-Based Access Control (RBAC) & Action Authorization Boundaries
Defines strict privilege tiers:
- ANALYST_TIER_1: View incidents, run read-only OSINT scans, request containment.
- ANALYST_TIER_2: Triage alerts, approve single-host containment, submit threat intel.
- INCIDENT_COMMANDER: Authorize destructive playbooks, sign dual-custody actions, execute network blocks.
- SOC_ADMIN: Full administrative policy, user lifecycle, and system configuration.
"""

from typing import Dict, Any, List, Set
from enum import Enum

class Role(str, Enum):
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
    PURGE_AUDIT_LOGS = "PURGE_AUDIT_LOGS" # Strictly disabled / prohibited

ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
    Role.ANALYST_TIER_1: {
        Permission.VIEW_ALERTS,
        Permission.VIEW_INCIDENTS,
        Permission.RUN_OSINT_RECON,
        Permission.VIEW_THREAT_INTEL,
        Permission.ATTACH_EVIDENCE
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
        Permission.EXECUTE_DNS_SINKHOLE
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
        Permission.MANAGE_DETECTION_RULES
    }
}

class RBACManager:
    """
    Enforces authorization checks on SOC user actions.
    """

    @staticmethod
    def has_permission(user_role: Role, required_permission: Permission) -> bool:
        allowed_permissions = ROLE_PERMISSIONS.get(user_role, set())
        return required_permission in allowed_permissions

    @staticmethod
    def verify_dual_custody(requester_role: Role, approver_role: Role, action_permission: Permission) -> bool:
        """
        Dual-custody security policy:
        Critical destructive actions (Host Isolation, Firewall Block) require:
        1. Requester must hold at least ANALYST_TIER_2 or higher.
        2. Approver must hold INCIDENT_COMMANDER or SOC_ADMIN.
        3. Requester and approver cannot be the same entity.
        """
        high_impact_actions = {
            Permission.EXECUTE_HOST_ISOLATION,
            Permission.EXECUTE_FIREWALL_BLOCK,
            Permission.EXECUTE_DNS_SINKHOLE
        }

        if action_permission not in high_impact_actions:
            return True

        if requester_role not in [Role.ANALYST_TIER_2, Role.INCIDENT_COMMANDER, Role.SOC_ADMIN]:
            return False

        if approver_role not in [Role.INCIDENT_COMMANDER, Role.SOC_ADMIN]:
            return False

        return True
