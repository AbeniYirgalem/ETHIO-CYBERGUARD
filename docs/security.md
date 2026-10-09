# 🔒 ETHIO-CYBERGUARD Platform Security Architecture

**Platform Version**: 1.1.0  
**Security Model**: Defense-in-Depth, Dual-Custody SOAR, Cryptographic Chain of Custody, Multi-Tenant Hard Isolation  
**Compliance Standard**: INSA Critical National Infrastructure Directives, ISO/IEC 27001, OWASP Top 10  

---

## 1. 7-Tier Role-Based Access Control (RBAC) Matrix

Access permissions are enforced strictly at the API and database levels rather than merely toggling frontend visibility:

| Capability | SUPER_ADMIN | SOC_MANAGER | INCIDENT_RESPONDER | SECURITY_ANALYST | THREAT_HUNTER | AUDITOR | READ_ONLY |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **View Dashboards & Incidents** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Query Live Telemetry & Events** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Search & Query Threat IOCs** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Run Multi-Agent AI Investigation**| ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Interact with SOC Copilot** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Submit Containment Recommendation**| ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Sign Dual-Custody Approval Gate** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Rollback Containment Actions** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Manage SIGMA Detection Rules** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Inspect Chained Audit Log** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Manage Tenant & User Lifecycle** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## 2. Dual-Custody Containment Invariants

To prevent rogue operator actions or automated algorithm runaway, high-consequence containment operations (`ISOLATE_HOST`, `BLOCK_IP`, `DISABLE_ACCOUNT`, `SINKHOLE_DOMAIN`) adhere to strict requirements:
1. **Separation of Initiator and Approver**: Tier-1/Tier-2 analysts and AI agents may initiate containment requests, but only a certified `INCIDENT_RESPONDER`, `SOC_MANAGER`, or `SUPER_ADMIN` may sign the approval gate.
2. **Action Expiration**: Pending actions expire after 30 minutes to prevent stale containment orders from executing after network topography has changed.
3. **One-Click Reversibility**: Every destructive action is paired with an automated rollback handler to instantly restore operational capability in case of false positives.

---

## 3. Cryptographic Chain of Custody

All containment actions, approvals, rejections, and administrative state changes are recorded in an append-only ledger secured by SHA-256 hash chaining:
$$\text{Entry Hash}_n = \text{SHA-256}\left(\text{Hash}_{n-1} \,\|\, \text{Timestamp} \,\|\, \text{Operator} \,\|\, \text{Action} \,\|\, \text{Target} \,\|\, \text{Outcome}\right)$$

Any attempt to alter or delete historic audit records invalidates subsequent hashes in the chain, guaranteeing forensic integrity during post-incident INSA audits.

---

## 4. Multi-Tenant Hard Isolation

- **Tenant Partitioning**: All database records (`events`, `alerts`, `incidents`, `evidence`) require non-null `organization_id` foreign keys.
- **Query Filter Injection**: SQLAlchemy session wrappers automatically bind the calling user's tenant ID to all queries. Cross-tenant reads or writes are rejected at the ORM layer.
- **WebSocket Channel Isolation**: Live telemetry streams are divided into discrete channels (`tenant:<org_name>`), preventing cross-tenant broadcast contamination.

---

## 5. Network & Cryptographic Controls

- **Transport Security**: All external communications (Agent-to-API, Web-to-API, Inter-service) mandate TLS 1.3 encryption.
- **Authentication**: JWT access tokens signed with HMAC-SHA256 (3,600s TTL) with cryptographically rotating refresh tokens.
- **API Collector Keys**: Telemetry agents authenticate with dedicated `X-Agent-Key` headers tied to unique endpoint asset IDs.
- **Secrets Management**: Zero hardcoded secrets in the codebase; all credentials, tokens, and database keys are sourced from protected environment variables (`.env`).
