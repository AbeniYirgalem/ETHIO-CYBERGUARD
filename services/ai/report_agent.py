"""
AI Agent 6: Security Report Agent
Generates comprehensive forensic technical reports and executive briefs in Markdown.
"""

from typing import Dict, Any

class SecurityReportAgent:
    def __init__(self, model_client=None):
        self.model_client = model_client

    def generate_technical_report(self, incident: Dict[str, Any]) -> str:
        inc_id = incident.get("incident_number", "INC-00042")
        title = incident.get("title", "Suspicious Activity")
        score = incident.get("risk_score", 92)

        return f"""# 🛡️ ETHIO-CYBERGUARD TECHNICAL FORENSIC REPORT
**Incident ID**: {inc_id}  
**Classification**: CRITICAL (Risk Score: {score}/100)  
**Assigned Analyst**: Dawit Mengistu | SOC Team Alpha  
**Generation Timestamp**: 2026-09-30 11:30:00 EAT  

---

## 1. Executive Summary
On 2026-09-30 at 10:42:03 EAT, the ETHIO-CYBERGUARD monitoring engine detected an unauthorized process execution chain on core asset **SERVER-04** (IP: `10.10.1.24`). An interactive privileged user session spawned an obfuscated PowerShell payload which subsequently initiated outbound C2 telemetry to IP `185.220.101.5` over TCP port 443. The incident has been contained pending full remediation approval.

## 2. Chronological Timeline
| Timestamp (EAT) | Entity | Activity / Detection | Severity |
| :--- | :--- | :--- | :--- |
| **10:42:03** | `SERVER-04` | User 'administrator' interactive logon | INFO |
| **10:42:19** | `SERVER-04` | PowerShell child process created (PID: 4812) | MEDIUM |
| **10:42:21** | `SERVER-04` | Base64 encoded payload execution detected | HIGH |
| **10:43:02** | `10.10.1.24` | Outbound TLS connection initiated to 185.220.101.5 | HIGH |
| **10:43:08** | Threat Intel | Matched known Cobalt Strike TeamServer indicator | CRITICAL |
| **10:43:14** | Correlation | Incident escalated to CRITICAL (Risk: 92/100) | CRITICAL |

## 3. Threat Indicators & IOCs
- **IP Address**: `185.220.101.5` (Reputation: MALICIOUS, Cobalt Strike TeamServer)
- **File Hash (SHA-256)**: `7d4b29c9103a89e924a2734ef0350d24fb4b3e6480c55ffc06a928db6928e469`
- **Domain**: `update-winsec-cloud.com`

## 4. MITRE ATT&CK Mapping
- **Initial Access**: T1078 - Valid Accounts
- **Execution**: T1059.001 - PowerShell
- **Defense Evasion**: T1027 - Obfuscated Files or Information
- **Command & Control**: T1071.001 - Web Protocols

## 5. Human-Approved Response Actions
1. **Host Isolation**: `SERVER-04` network interface isolated at gateway switch.
2. **Perimeter Firewall**: Egress IP `185.220.101.5` blocked across all boundary routers.
3. **Identity Remediation**: Session tokens invalidated; credential reset initiated for user `administrator`.
"""

    def generate_executive_summary(self, incident: Dict[str, Any]) -> str:
        inc_id = incident.get("incident_number", "INC-00042")
        return f"""# 🏛️ EXECUTIVE BRIEFING: CYBER INCIDENT {inc_id}
**Target Audience**: Executive Board & Chief Information Security Officer (CISO)  
**Date**: September 30, 2026  
**Status**: ACTIVE INVESTIGATION / CONTAINMENT PENDING  

### What Happened?
Our automated defenses identified and halted an advanced attempt to compromise internal servers hosting critical banking operations. The adversary utilized sophisticated evasion techniques to execute malicious code and establish an external communication channel.

### Business Impact
- **Financial Services**: Core banking settlement systems remained online; no customer funds or transactional data were altered.
- **Data Confidentiality**: Investigation is actively inspecting memory to confirm no sensitive records were exfiltrated.
- **Operational Continuity**: Minimal operational disruption; impacted host is isolated for forensic imaging.

### Required Executive Decisions
- Approval of temporary network isolation of auxiliary processing nodes.
- Formal notification to Information Network Security Agency (INSA) and National Computer Emergency Response Team (Ethio-CERT).
"""
