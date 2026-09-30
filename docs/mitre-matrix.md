# ETHIO-CYBERGUARD - MITRE ATT&CK Matrix Coverage

This document outlines the MITRE ATT&CK Enterprise Matrix mapping for ETHIO-CYBERGUARD's detection rules, behavioral baselines, and multi-agent AI correlation.

## 📊 Tactics & Techniques Coverage Table

| MITRE Tactic | Technique ID | Technique Name | Detection Mechanism | Severity | Test Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Initial Access** | `T1566.001` | Phishing: Spearphishing Attachment | ThePhish RFC-822 Parser & Attachment Hash Audit | HIGH | Verified |
| **Initial Access** | `T1566.002` | Phishing: Spearphishing Link | openSquat Typosquatting & IP Host Detector | CRITICAL | Verified |
| **Execution** | `T1059.001` | Command & Scripting: PowerShell | SIGMA Rule `suspicious_powershell_obfuscation.yml` | CRITICAL | Verified |
| **Execution** | `T1059.004` | Command & Scripting: Unix Shell | Linux Auditd Collector & Regex Matcher | HIGH | Verified |
| **Persistence** | `T1078.002` | Valid Accounts: Domain Accounts | Anomaly Detection: Off-Hours SWIFT Directory Access | HIGH | Verified |
| **Persistence** | `T1136.001` | Create Account: Local Account | Windows Security Event ID 4720 | HIGH | Verified |
| **Privilege Escalation** | `T1068` | Exploitation for Privilege Escalation | Linux Auditd SUID execution tracking | HIGH | Verified |
| **Defense Evasion** | `T1027` | Obfuscated Files or Information | Base64 decode + Entropy Analysis | HIGH | Verified |
| **Credential Access** | `T1003.001` | OS Credential Dumping: LSASS Memory | SIGMA Rule `mimikatz_lsass_dump.yml` | CRITICAL | Verified |
| **Credential Access** | `T1110.001` | Brute Force: Password Guessing | Perimeter Syslog Ingestion (Threshold: >10 in 5m) | HIGH | Verified |
| **Discovery** | `T1046` | Network Service Discovery | SpiderFoot Recon & Port Scan Correlator | MEDIUM | Verified |
| **Discovery** | `T1087` | Account Discovery | Active Directory Query Anomaly | LOW | Verified |
| **Lateral Movement** | `T1021.001` | Remote Services: Remote Desktop (RDP) | Internal Network Flow Correlator | HIGH | Verified |
| **Lateral Movement** | `T1021.002` | Remote Services: SMB/Windows Admin Shares | SMB Lateral Pipe Monitor | HIGH | Verified |
| **Command & Control** | `T1071.001` | Application Layer Protocol: Web (C2) | Threat Intel IOC Matcher (185.220.101.5) | CRITICAL | Verified |
| **Command & Control** | `T1568.002` | Dynamic Resolution: Domain Fluxing (DGA) | Shannon Entropy & NXDomain Spikes | HIGH | Verified |
| **Exfiltration** | `T1048` | Exfiltration Over Alternative Protocol | DNS Tunneling & Egress Spike Monitor | CRITICAL | Verified |

---

## 🇪🇹 Ethiopian Threat Context & Regional Rules

1. **Telebirr & CBE Birr Credential Harvesters**:
   - Monitored under `T1566.002` using Amharic keyword extraction and non-official domain inspection (`services/phishing/email_analyzer.py`).
2. **SWIFT / National Payment Switch (EthSwitch) Anomalies**:
   - Monitored under `T1078` detecting off-hours access to critical financial transfer nodes outside standard EAT (UTC+3) banking hours.
3. **Government Portal Spoofing (INSA / ERCA / Gov.et)**:
   - Monitored under `T1566.001` and `openSquat` domain mutation rules.
