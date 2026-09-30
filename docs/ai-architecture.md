# 🤖 ETHIO-CYBERGUARD Multi-Agent AI Architecture

## Overview
ETHIO-CYBERGUARD deploys seven dedicated, specialized AI agents coordinated by a central orchestrator. Rather than using an ungrounded general-purpose chatbot, each agent has a strictly delineated operational envelope, structured JSON input/output schemas, and rigorous grounding against actual security telemetry.

```
                      INCIDENT DETECTED
                             │
                             ▼
                    ┌─────────────────┐
                    │  ORCHESTRATOR   │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Event Agent  │     │ Threat Agent │     │ Correlation  │
│ (Telemetry)  │     │ (IOC Match)  │     │ (Kill-chain) │
└───────┬──────┘     └───────┬──────┘     └───────┬──────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             ▼
                    ┌─────────────────┐
                    │  Investigation  │
                    │      Agent      │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │ Risk Assessment │
                    │      Agent      │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │  Report Agent   │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │ SOC Assistant   │
                    │ (Interactive)   │
                    └─────────────────┘
```

---

## The 7 Specialized AI Agents

### 1. Security Event Analysis Agent
- **Purpose**: Rapidly inspects normalized events for malicious indicators, living-off-the-land (LotL) execution signatures, and evasion techniques.
- **Input**: Normalized event JSON (process name, command-line arguments, parent lineage, network sockets).
- **Output**: Malicious classification (`true`/`false`), confidence rating (0.00-1.00), reasons, and MITRE ATT&CK technique IDs.

### 2. Threat Intelligence Agent
- **Purpose**: Enriches observed entities against known campaigns, threat actors (e.g. Cobalt Strike, APT clusters targeting African financial infrastructure), and historical indicator databases.
- **Input**: Extracted IPs, domains, hashes, and URLs.
- **Output**: Reputation grade, threat actor mapping, campaign name, first/last seen timestamps.

### 3. Incident Correlation Agent
- **Purpose**: Assembles disparate security alerts occurring across multiple assets or accounts into a unified incident lifecycle.
- **Input**: Correlated alerts within a rolling temporal sliding window.
- **Output**: Kill-chain progression map (e.g., Initial Access → Execution → Defense Evasion → C2), attack path narrative.

### 4. Investigation Agent
- **Purpose**: Serves as the Tier-3 forensic investigator. Synthesizes answers to critical SOC questions:
  1. What happened?
  2. When did the intrusion begin?
  3. Which systems, accounts, and network segments are compromised?
  4. What specific evidence corroborates the hypothesis?
  5. What concrete forensic actions should the analyst take next?

### 5. Risk Assessment Agent
- **Purpose**: Computes an explainable, granular composite risk score (0-100) instead of a black-box rating.
- **Formula & Factors**:
  - Asset Criticality Weight
  - Privileged Credential Exposure
  - Confirmed External C2 Communication
  - Potential Lateral Traversal Radius
- **Output**: Overall score, sub-scores (Impact, Likelihood, Confidence, Exposure), and plain-language business impact analysis.

### 6. Security Report Agent
- **Purpose**: Automatically authors publication-ready reports for technical and executive stakeholders.
- **Outputs**:
  - **Technical Forensic Report**: MITRE matrix, evidence hash table, timeline, IOC list.
  - **Executive Briefing**: High-level impact summary, regulatory implications (INSA / Ethio-CERT), required business decisions.

### 7. Security Assistant (Grounded SOC Copilot)
- **Purpose**: Interactive conversational interface that security analysts can query directly during an incident.
- **Grounding & Guardrails**:
  - Grounded strictly in platform evidence (Event IDs, Sysmon logs, Threat Intel records).
  - Explicitly prohibited from fabricating unobserved indicators or events.
  - Cites exact telemetry records for every assertion made.
