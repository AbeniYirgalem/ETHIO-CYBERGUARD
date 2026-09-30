# SIEM Telemetry Collectors & Ingestion Pipeline

ETHIO-CYBERGUARD provides lightweight, production-ready telemetry collectors designed to ingest events from heterogeneous enterprise endpoints, perimeter devices, and email gateways.

---

## 1. Supported Collectors

### 1. Windows Endpoint Collector (`collectors/endpoint/windows_collector.ps1`)
- Monitors Windows Event Log channels:
  - `Security` (Event IDs: 4624 Logon, 4625 Failed Logon, 4688 Process Creation, 4720 Account Created)
  - `Microsoft-Windows-PowerShell/Operational` (Event ID: 4104 Script Block Logging)
  - `Microsoft-Windows-Sysmon/Operational` (Event ID: 1 Process Creation, 3 Network Connect)
- Forwards batched events to the Central API Ingestion endpoint.

### 2. Linux Auditd & Syslog Collector (`collectors/endpoint/linux_collector.py`)
- Tails `/var/log/auth.log`, `/var/log/secure`, and auditd `/var/log/audit/audit.log`.
- Extracts interactive shell executions, `sudo` invocations, and SSH authentication failures.

### 3. Central Syslog Receiver (`collectors/syslog/syslog_receiver.py`)
- Listens on UDP port 5140 (configurable for RFC 5424 and RFC 3164 Syslog).
- Receives logs from firewalls (Palo Alto, Fortinet, Cisco ASA) and network switches.

### 4. Email Gateway Ingest (`collectors/email/email_collector.py` & `email_mta_ingest.py`)
- Interfaces with Postfix / Sendmail milters or Microsoft 365 / Google Workspace webhooks.
- Passes raw MIME payloads to the automated phishing and header forensics analyzer.

---

## 2. Ingestion Pipeline Stages

```
Raw Telemetry Event
        ↓
Parser & Normalizer (services/ingestion/normalizer.py)
        ↓
ECS Standardized Event (services/ingestion/schema.py)
        ↓
Threat Intelligence Enrichment (services/threat_intelligence/enrichment.py)
        ↓
SIGMA Detection Engine (detection/evaluator.py)
        ↓
Incident Correlation (services/correlation/correlator.py)
        ↓
WebSocket Real-Time Broadcast & Incident Store
```
