# 🛡️ ETHIO-CYBERGUARD STRIDE Threat Model

This document establishes the threat boundaries, attack surfaces, security assumptions, and mitigations protecting the **ETHIO-CYBERGUARD** platform itself against adversary compromise.

---

## 1. System Architecture & Trust Boundaries

```
[ External Internet / Untrusted Zone ]
   │  • Foreign Mail Servers
   │  • Public DNS / Whois
   │  • External Threat Intel Feeds
   ▼
┌────────────────────────────────────────────────────────┐
│ Boundary 1: Edge Perimeter & Ingestion Filter          │
│   • Prompt Injection Sanitizer (<UNTRUSTED_LOG_DATA>) │
│   • Ingestion Rate Limiter (Token Bucket)              │
└────────────────────────────────────────────────────────┘
   │
   ▼
┌────────────────────────────────────────────────────────┐
│ Boundary 2: Core Processing & Multi-Agent AI Tier      │
│   • ECS Canonicalization                               │
│   • Deterministic Risk Engine                          │
│   • 7 AI Agents (Zero Direct Shell Access)             │
└────────────────────────────────────────────────────────┘
   │
   ▼
┌────────────────────────────────────────────────────────┐
│ Boundary 3: SOAR Containment & Dual-Custody Barrier    │
│   • Human-in-the-Loop Analyst Verification             │
│   • Dual-Custody Approval Required for Destructive Ops │
│   • Append-Only Cryptographic Audit Log                │
└────────────────────────────────────────────────────────┘
```

---

## 2. STRIDE Threat Analysis Matrix

| Threat Category | Potential Vector in ETHIO-CYBERGUARD | Specific Impact | Implemented Mitigation |
| :--- | :--- | :--- | :--- |
| **Spoofing** | Attacker transmits falsified Syslog/NetFlow packets claiming to originate from internal banking core (`10.10.1.24`). | Triggers false alarms or cloaks real malicious activity. | **HMAC-SHA256 log signing** on endpoint collectors, RFC 5425 TLS client-certificate mutual authentication on Syslog gateways. |
| **Tampering** | Rogue actor or malware alters historical incident records or modifies SIGMA detection rules. | Destroys forensic evidence chain of custody and conceals breach. | **SHA-256 Merkle-tree chained audit records** (`ForensicsEvidence.sha256`); PostgreSQL append-only write permissions for analyst accounts. |
| **Repudiation** | SOC analyst disavows executing a destructive host isolation or perimeter IP drop action. | Inability to trace insider threats or rogue containment actions. | **Dual-Custody Enforcement (`verify_dual_custody`)**: High-impact containment playbooks require distinct requester and approver identities. |
| **Information Disclosure** | Unauthenticated actor intercepts sensitive packet captures, RFC-822 email bodies, or credentials harvested during phishing triage. | Data breach of PII, financial customer data, or internal server topology. | Role-Based Access Control (**RBAC**); automated credential masking (`***`) in ingestion validators; TLS 1.3 encryption in transit. |
| **Denial of Service** | Volumetric log flood (e.g. > 100,000 EPS) targeting the ingestion API. | Resource exhaustion leading to blind spots during an active breach. | Asynchronous batch processing queue, backpressure handling, verified throughput of **51,000+ EPS** in benchmark tests. |
| **Elevation of Privilege** | Attacker injects prompt escape sequences (`Ignore all previous instructions...`) into raw email bodies to hijack AI agent tools. | AI agent executes unauthorized shell commands or approves playbooks. | **Delimited Input Encapsulation** (`<UNTRUSTED_LOG_DATA>`), strict regex sanitizer (`validators.py`), read-only tools for AI agents. |

---

## 3. High-Impact Action Authorization Matrix

Containment playbooks possess the capability to impact production banking systems. ETHIO-CYBERGUARD enforces a strict separation of duties:

| Action | Impact Level | Minimum Requester Role | Minimum Approver Role | Reversible? |
| :--- | :--- | :--- | :--- | :--- |
| **Isolate Host** | `CRITICAL` | `ANALYST_TIER_2` | `INCIDENT_COMMANDER` | Yes (via EDR Un-isolate) |
| **Drop Perimeter IP** | `HIGH` | `ANALYST_TIER_2` | `INCIDENT_COMMANDER` | Yes (Expire ACL) |
| **Disable AD User** | `MEDIUM` | `ANALYST_TIER_2` | `ANALYST_TIER_2` | Yes (Re-enable) |
| **DNS Sinkhole** | `CRITICAL` | `ANALYST_TIER_2` | `SOC_ADMIN` | Yes (Revert Zone) |
| **Registrar Takedown** | `MEDIUM` | `ANALYST_TIER_1` | `ANALYST_TIER_2` | External Process |

---

## 4. Supply Chain & Dependency Hardening
- Dependencies are locked in `apps/web/package-lock.json` and pinned in Python requirements.
- Container base images utilize minimal alpine/slim distributions with non-root runtime users.
- Automated static code scanning (`bandit`, `eslint`) integrated into GitHub Actions CI pipeline.
