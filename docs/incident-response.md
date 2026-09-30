# ETHIO-CYBERGUARD - Incident Response & SOAR Architecture

## 1. Human-in-the-Loop Philosophy

ETHIO-CYBERGUARD implements **Human-Approved Incident Response (SOAR)**. While AI agents automate forensic collection, threat intelligence correlation, and risk scoring, **destructive and containment actions require explicit human analyst authorization**:

```
AI Risk & Investigation Agents
              │
              ▼
  Generated Response Action
  (e.g., ISOLATE_HOST, BLOCK_IP, REVOKE_SESSION)
              │
              ▼
    SOC Response Queue
  (Status: PENDING_APPROVAL)
              │
              ▼
  ┌───────────────────────┐
  │ Analyst Human Review  │
  │ • Review evidence     │
  │ • Inspect blast radius│
  │ • [APPROVE] / [REJECT]│
  └───────────┬───────────┘
              │
      ┌───────┴───────┐
      ▼               ▼
  [APPROVED]      [REJECTED]
      │               │
  Execute via     Annotate reason &
  Agent/EDR       archive action
      │               │
      └───────┬───────┘
              ▼
    Immutable Audit Log
```

## 2. Standard Response Playbooks

1. **Host Isolation (`ISOLATE_HOST`)**:
   - Drops all network ingress and egress on the target endpoint except for encrypted management connection back to the SOC.
2. **Perimeter Firewall IP Drop (`BLOCK_IP`)**:
   - Pushes an egress/ingress firewall rule to perimeter gateways (Palo Alto, Fortinet, pfSense) blocking connection to malicious C2s.
3. **Identity Token Revocation (`REVOKE_USER_SESSION`)**:
   - Invalidates active Kerberos tickets and OAuth tokens in Microsoft Entra / Active Directory.
4. **Registrar Takedown Notice (`TAKEDOWN_DOMAIN`)**:
   - Dispatches abuse notices to domain registrars for active typosquatted fraud portals.
