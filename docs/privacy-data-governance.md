# 🔒 ETHIO-CYBERGUARD Privacy & Data Governance Architecture

## 1. Scope & Regulatory Framework
ETHIO-CYBERGUARD is engineered to comply with enterprise cybersecurity operational standards and national data protection mandates (e.g. Ethiopian Personal Data Protection Proclamation, ISO/IEC 27001, and GDPR Article 32 guidelines for incident processing).

---

## 2. Data Classification Matrix

| Classification Tier | Data Types | Processing Rules | Retention Period |
| :--- | :--- | :--- | :--- |
| **Tier 1: Public / Open Source** | Public DNS records, WHOIS data, public IP ASNs, commercial threat feeds. | No encryption required at rest; cached with standard TTLs. | 90 days rolling |
| **Tier 2: Internal Telemetry** | Firewall drop counters, NetFlow aggregates, system performance metrics. | AES-256 encrypted at rest; accessible by Tier-1 Analysts. | 180 days |
| **Tier 3: Confidential Security Logs** | Windows Event Logs, Syslog messages, authentication attempts, IP addresses. | AES-256 encrypted; hashed user identifiers in non-admin views. | 365 days (regulatory standard) |
| **Tier 4: Restricted / Sensitive PII** | Full email bodies (`.eml`), memory dumps, credential strings, password hashes. | Strong salt hashing; automatic masking of sensitive credentials; access restricted to Incident Commanders. | 30 days post-incident closure |

---

## 3. Data Sanitization & Ingestion Minimization
1. **Automated Credential Redaction**:
   During ECS normalization (`services/ingestion/validators.py`), incoming telemetry matching patterns like `password=`, `token=`, or `Bearer ` is immediately redacted to `***REDACTED***`.
2. **Synthetic Demonstration Data**:
   All seed data, mock alerts, and awareness templates utilize fictional identifiers (`dawit.mengistu@cbe.com.et`, `telebirr-bonus.xyz`, `SERVER-04`), preventing exposure of real organizational assets.
3. **Right to Erasure & Data Purging**:
   Non-evidentiary logs are purged upon expiration of the defined retention window via automated cron jobs (`scripts/backup/purge_expired_logs.sh`). Evidentiary items tagged with active incident investigations are preserved until formal incident closure and sign-off.
