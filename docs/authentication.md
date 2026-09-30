# Authentication, RBAC & Multi-Tenancy Architecture

ETHIO-CYBERGUARD implements an enterprise-grade identity layer combining cryptographically verified JWT tokens, strict Role-Based Access Control (RBAC), and hard multi-tenant isolation.

---

## 1. Role Hierarchy & Privilege Matrix

| Role | Scope | Permissions | Dual-Custody Authority |
|---|---|---|---|
| `SUPER_ADMIN` | Platform-wide | Full configuration, rule management, user lifecycle | Can approve any action |
| `ORG_ADMIN` | Tenant-scoped | Manage organization assets, team members, alert policies | Tenant admin |
| `SOC_MANAGER` | Tenant-scoped | Oversee incident queue, approve containment actions | Primary/Secondary dual custody |
| `INCIDENT_COMMANDER`| Tenant-scoped | Lead critical containment, authorize host isolation & firewall drops | Secondary dual custody signatory |
| `SECURITY_ENGINEER`| Tenant-scoped | Triage, tune SIGMA rules, run recon, request containment | Primary dual custody initiator |
| `SOC_ANALYST` | Tenant-scoped | Triage alerts, inspect phishing emails, submit threat intel | Primary dual custody initiator |
| `AUDITOR` | Tenant-scoped | Read-only inspection of immutable cryptographic audit trail | None (Observer) |
| `VIEWER` | Tenant-scoped | Read-only executive dashboards and metrics | None (Observer) |

---

## 2. Dual-Custody Containment Workflow

Destructive containment actions cannot be executed unilaterally or by an automated AI agent without human authorization:
1. **AI Recommendation**: AI Risk Agent or Threat Intel Agent flags an asset and submits a recommendation.
2. **Primary Request**: A Tier-2 Analyst or Security Engineer verifies evidence and submits an action request.
3. **Secondary Sign-off**: An Incident Commander, SOC Manager, or Admin must sign the dual-custody authorization.
4. **Execution & Audit**: The SOAR engine executes the action and commits an immutable entry to the audit log.

---

## 3. Multi-Tenant Data Isolation

- Every asset, event, incident, rule, and phishing campaign belongs to an `org_id`.
- The `TenantSecurityManager` validates that `user.org_id == resource.org_id` on every query.
- Users from Organization A (e.g., Commercial Bank of Ethiopia) can never query or view telemetry from Organization B (e.g., Awash Bank).
