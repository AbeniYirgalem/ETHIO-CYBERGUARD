# Detection Rules & SIGMA Rule Engine Guide

ETHIO-CYBERGUARD incorporates a high-speed SIGMA-compatible YAML detection engine loaded with community standards and customized rules for the Ethiopian national threat landscape.

---

## 1. Directory Structure

Rules are organized by domain category in `detection-rules/`:
```
detection-rules/
├── windows/           # PowerShell obfuscation, LSASS dumps, Task persistence, VSSAdmin
├── linux/             # SSH brute force, cron persistence, reverse shells, shadow access
├── network/           # C2 beaconing, DNS tunneling, port scanning, abnormal egress
├── authentication/    # Distributed brute-force, password spraying, off-hours SWIFT access
├── phishing/          # Telebirr scam lures, CBE fake KYC clones, macro documents
└── ethiopia/          # Regional SMS spoofing, .gov.et defacements, Chapa API leaks
```

---

## 2. SIGMA Rule Format

Every rule conforms to the standardized SIGMA YAML schema:
```yaml
id: win-sigma-001
title: Suspicious Obfuscated PowerShell Execution
status: stable
description: Detects encoded or obfuscated PowerShell commands often used in initial stagers.
author: ETHIO-CYBERGUARD Detection Team
version: 1.2.0
date: 2026-09-30
references:
  - https://attack.mitre.org/techniques/T1059/001/
tags:
  - attack.execution
  - attack.t1059.001
logsource:
  category: process_creation
  product: windows
detection:
  selection:
    process.name: powershell.exe
    process.command_line:
      - '*-enc*'
      - '*-encodedcommand*'
      - '*downloadstring*'
      - '*invoke-expression*'
  condition: selection
falsepositives:
  - Legitimate enterprise deployment scripts utilizing base64 encoding (e.g. SCCM, Ansible)
severity: critical
```

---

## 3. Hot-Reloading & Evaluation

Rules are evaluated dynamically by `services.detection.evaluator.SigmaRuleEvaluator`. When a normalized ECS event arrives, the engine scans active criteria in parallel, firing alerts tagged with MITRE ATT&CK techniques.
