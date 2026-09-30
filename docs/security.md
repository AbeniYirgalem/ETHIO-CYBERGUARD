# 🔒 ETHIO-CYBERGUARD Platform Security Architecture

Because ETHIO-CYBERGUARD is itself a mission-critical cybersecurity platform operating inside sensitive enterprise and government perimeters, security principles must be rigorously enforced across all layers.

---

## 1. Role-Based Access Control (RBAC)
Access permissions are strictly governed on the backend rather than merely hiding frontend UI elements:

| Capability | SUPER_ADMIN | SOC_MANAGER | SECURITY_ANALYST | VIEWER |
| :--- | :---: | :---: | :---: | :---: |
| View Dashboards & Incidents | ✅ | ✅ | ✅ | ✅ |
| Query Live Events & IOCs | ✅ | ✅ | ✅ | ❌ |
| Run AI Investigation Agent | ✅ | ✅ | ✅ | ❌ |
| Interact with SOC Copilot | ✅ | ✅ | ✅ | ❌ |
| Approve / Reject Response Actions | ✅ | ✅ | ❌ | ❌ |
| Edit Detection Rules | ✅ | ✅ | ❌ | ❌ |
| Manage Users & Tenants | ✅ | ❌ | ❌ | ❌ |

---

## 2. Human-in-the-Loop Safeguards
1. **No Autonomous Destructive Execution**: LLM and heuristic models are strictly isolated from direct shell execution or firewall configuration daemons.
2. **Explicit Verification Barrier**: Destructive actions (e.g., host network isolation, account suspension, port blocking) require multi-factor analyst authorization.
3. **Immutable Audit Trail**: All approval or rejection decisions, analyst identities, timestamps, and justification notes are logged to an append-only audit table.

---

## 3. AI Safety & Prompt-Injection Defenses
- **Input Sanitization**: Telemetry arguments (process command lines, DNS query strings) are stripped of instruction markers and wrapped inside structured JSON schemas before presentation to language models.
- **RAG Grounding**: The Security Assistant is constrained to answer only from verified incident evidence and telemetry in the database, explicitly preventing hallucinated indicators.
- **Output Validation**: Multi-agent outputs must conform strictly to Pydantic JSON schemas. Malformed or out-of-schema responses trigger an immediate heuristic fallback.

---

## 4. Encryption & Integrity
- **In Transit**: All communication (agent-to-backend, analyst browser-to-backend, inter-service) is encrypted via TLS 1.3.
- **At Rest**: PostgreSQL transparent data encryption (TDE) and pgcrypto for sensitive credential hashes.
- **Evidence Integrity**: All forensic evidence stored in the evidence locker is fingerprinted using SHA-256 upon ingestion to maintain forensic chain-of-custody.
