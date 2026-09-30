# ETHIO-CYBERGUARD - Detection Engine Architecture

The ETHIO-CYBERGUARD Detection Engine processes ECS-normalized events in real-time, executing deterministic SIGMA-compatible YAML rules alongside behavioral anomaly thresholds.

```
      Normalized Event (ECS)
                │
                ▼
  ┌───────────────────────────┐
  │   SIGMA YAML Rule Matcher │ ─── (Checks field conditions, regex, thresholds)
  └─────────────┬─────────────┘
                │
                ▼
  ┌───────────────────────────┐
  │ Behavioral Anomaly Engine │ ─── (Evaluates deviations from user/host baselines)
  └─────────────┬─────────────┘
                │
                ▼
  ┌───────────────────────────┐
  │  Threat Intel IOC Matcher │ ─── (Checks IP, Domain, SHA256 hashes against feeds)
  └─────────────┬─────────────┘
                │
                ▼
          Alert Generated
```

## 1. Rule Format (SIGMA Compatible)

Rules are authored in YAML format under `detection-rules/`:

```yaml
id: RULE-001
title: Suspicious Obfuscated PowerShell Command Execution
status: production
description: Detects encoded or hidden PowerShell invocations commonly utilized by lateral movement tools.
references:
  - https://attack.mitre.org/techniques/T1059/001/
severity: critical
detection:
  selection:
    event_type: process_creation
    process.name: powershell.exe
    process.command_line|contains:
      - "-enc"
      - "-encodedcommand"
      - "frombase64string"
      - "downloadstring"
      - "iex"
  condition: selection
tags:
  - attack.execution
  - attack.t1059.001
```

## 2. Rule Evaluation Engine

The evaluation logic resides in `services/detection/engine.py`. Each incoming event is tested against active rules:
1. Exact field matching (e.g. `process.name == "powershell.exe"`).
2. Substring matching (`|contains`).
3. Regex matching.
4. Aggregation / sliding window frequency triggers (e.g. >10 failed logins within 5 minutes).

## 3. Alert Deduplication

When multiple matching events occur within the correlation window for the same asset or user, the engine groups them into a single parent Incident to prevent alert fatigue.
