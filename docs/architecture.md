# 🛡️ ETHIO-CYBERGUARD System Architecture

## 1. Overview
ETHIO-CYBERGUARD is an AI-assisted Security Operations Center (SOC) and Security Information and Event Management (SIEM) platform designed for centralized threat detection, automated investigation, and human-in-the-loop response. The platform is tailored for Ethiopian educational institutions, financial organizations, state enterprises, and regional infrastructures.

```
                    ┌─────────────────────────────┐
                    │       Security Sources      │
                    │                             │
                    │ • Windows endpoints         │
                    │ • Linux servers             │
                    │ • Network devices (Routers) │
                    │ • Perimeter Firewalls       │
                    │ • Core Banking Applications │
                    │ • Ethio Telecom Cloud       │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │      DATA COLLECTION         │
                    │                             │
                    │ Windows PS1 / Linux Agent   │
                    │ Syslog RFC 5424 Receiver    │
                    │ Network Flow Sniffer        │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │    INGESTION & NORMALIZATION│
                    │                             │
                    │ Parse → Validate → Normalize│
                    │ Enrich Geo/Asset → Store    │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ Detection Engine │          │ Threat Intel     │
          │                  │          │                  │
          │ Rules (SIGMA)    │          │ Ethio-CERT IPs   │
          │ Signatures       │          │ C2 Domains       │
          │ Behavioral       │          │ Malware Hashes   │
          │ Anomaly          │          │ CVEs & Actors    │
          └────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  ▼
                    ┌─────────────────────────────┐
                    │      CORRELATION ENGINE     │
                    │                             │
                    │ Events → Alerts → Incidents │
                    │ Attack Graph & Timeline     │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │       AI ANALYSIS LAYER     │
                    │                             │
                    │ 1. Event Analysis Agent     │
                    │ 2. Threat Intel Agent       │
                    │ 3. Correlation Agent        │
                    │ 4. Investigation Agent      │
                    │ 5. Risk Assessment Agent    │
                    │ 6. Report Agent             │
                    │ 7. Security Assistant       │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │       SOC DASHBOARD         │
                    │                             │
                    │ Dark Theme (#070B12)        │
                    │ Alerts / Incidents / Risks  │
                    │ Investigations / Reports    │
                    │ AI Assistant / Analytics    │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │       RESPONSE CENTER       │
                    │                             │
                    │ AI Recommendations          │
                    │ [Human Approval Workflow]   │
                    │ Firewall & Host Execution   │
                    │ Immutable Audit Trail       │
                    └─────────────────────────────┘
```

---

## 2. Ingestion & Normalization Pipeline
Incoming logs from Windows Event Log, Linux auditd/syslog, and firewalls are ingested via HTTP/REST or Syslog UDP.
Every raw telemetry item is parsed into a unified schema:

```json
{
  "event_id": "ecg_9a8f10283c7d",
  "timestamp": "2026-09-30T10:42:21Z",
  "source": {
    "type": "endpoint",
    "hostname": "SERVER-04",
    "ip": "10.10.1.24",
    "os": "Windows"
  },
  "event_type": "process_execution",
  "severity": "CRITICAL",
  "user": "administrator",
  "process": {
    "name": "powershell.exe",
    "command_line": "powershell.exe -enc SQBFAFgA..."
  },
  "network": {
    "destination_ip": "185.220.101.5",
    "destination_port": 443
  },
  "enrichment": {
    "geo_location": {"country": "Germany", "reputation": "MALICIOUS"},
    "is_internal_network": true
  }
}
```

---

## 3. Detection Architecture
Detection uses a three-tier approach to prevent AI hallucination and false alert flooding:
1. **Rule Engine**: Evaluates fast deterministic rules (e.g. Obfuscated PowerShell execution, LSASS memory access, brute force thresholds).
2. **Behavioral Baseline Engine**: Compares activity to historical profiles.
   - Example score: +25 off-hours (03:14 AM) +20 remote IP +20 privileged credential +22 SWIFT access = **87/100**.
3. **Threat Intelligence Correlation**: Real-time cross-referencing against verified indicators (IPs, domains, hashes) from Ethio-CERT and global feeds.

---

## 4. Human-in-the-Loop Response Principle
Critical actions are never executed autonomously by an LLM:
- **AI Role**: Analyze, calculate risk, recommend specific action (e.g., `ISOLATE_HOST`, `BLOCK_IP`), provide justification and confidence score.
- **Human Role**: Authorized SOC Analyst inspects evidence, reviews potential blast radius, and clicks **[APPROVE]** or **[REJECT]**.
- **System Execution**: Only upon verified approval is the action executed and logged to an immutable audit record.
