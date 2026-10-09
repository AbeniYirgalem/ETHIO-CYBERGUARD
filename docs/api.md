# 🌐 ETHIO-CYBERGUARD REST & WebSocket API Specification

**Version**: 1.1.0  
**Schema Compliance**: Elastic Common Schema (ECS), OpenAPI 3.1, JSON Schema, Prometheus 0.0.4  
**Protocols**: HTTP/1.1, HTTP/2, WebSockets (RFC 6455)  
**Security**: Bearer JWT (HMAC-SHA256), Dual-Custody Approval Gates, API Keys (`X-Agent-Key`), Tenant Isolation  

---

## 📌 Base URLs & Path Conventions

| Environment | Base URL | WebSocket URI |
| :--- | :--- | :--- |
| **Production** | `https://soc.ethio-cyberguard.et/api/v1` | `wss://soc.ethio-cyberguard.et/ws/live-events` |
| **Local Development** | `http://localhost:8000/api/v1` | `ws://localhost:8000/ws/live-events` |

> [!NOTE]
> All core endpoints support both `/api/v1/...` and backwards-compatible `/api/...` prefix aliases.

---

## 1. Authentication, MFA & Identity Management (`/api/v1/auth`)

### Endpoints

| Method | Endpoint | Description | Required RBAC Role |
| :--- | :--- | :--- | :--- |
| `POST` | `/auth/login` | Authenticate with email & password; returns JWT access + refresh tokens | Anonymous |
| `POST` | `/auth/register` | Register a new analyst account (governed by tenant invitation) | `SUPER_ADMIN` / `ORG_ADMIN` |
| `POST` | `/auth/refresh` | Rotate expired access token using valid refresh token | Authenticated |
| `POST` | `/auth/logout` | Revoke current user session and invalidate refresh tokens | Authenticated |
| `GET` | `/auth/me` | Fetch active user profile, tenant UUID, and assigned RBAC permissions | Authenticated |
| `POST` | `/auth/change-password` | Update current account password with complexity validation | Authenticated |
| `POST` | `/auth/mfa/setup` | Generate TOTP QR code secret for two-factor authentication | Authenticated |
| `POST` | `/auth/mfa/verify` | Verify TOTP 6-digit passcode to finalize MFA activation | Authenticated |

#### Example Login Request
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "dawit.mengistu@cbe.com.et", "password": "SecurePassword123!"}'
```

#### Example Response (`200 OK`)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "email": "dawit.mengistu@cbe.com.et",
    "role": "SECURITY_ANALYST",
    "organization": "Commercial Bank of Ethiopia"
  }
}
```

---

## 2. Telemetry Ingestion, DLQ & Normalization (`/api/v1/events`)

Ingests endpoint, network, firewall, and syslog telemetry in ECS JSON format. Automatically evaluates rate limits (sliding window), computes SHA-256 deduplication hashes, and routes unparseable logs to the Dead-Letter Queue (DLQ).

### Endpoints

| Method | Endpoint | Description | Headers |
| :--- | :--- | :--- | :--- |
| `POST` | `/events/ingest` | Ingest single raw or ECS telemetry event | `X-Agent-Key: <token>` |
| `POST` | `/events/batch` | High-throughput batch ingestion (up to 5,000 events/batch) | `X-Agent-Key: <token>` |
| `GET` | `/events` | Query normalized events with query filters (`since`, `hostname`, `severity`) | `Authorization: Bearer <JWT>` |
| `GET` | `/events/stats` | Retrieve ingestion throughput metrics, EPS rates, and buffer utilization | `Authorization: Bearer <JWT>` |
| `GET` | `/events/dead-letter-queue` | Inspect failed/malformed telemetry events in the DLQ | `SUPER_ADMIN`, `SOC_MANAGER` |

#### Ingestion Payload (`POST /api/v1/events/ingest`)
```json
{
  "event_type": "process_execution",
  "host_name": "SERVER-04",
  "ip_address": "10.10.1.24",
  "user": "NT AUTHORITY\\SYSTEM",
  "process": {
    "name": "powershell.exe",
    "command_line": "powershell.exe -enc SQBFAFgA...",
    "parent_name": "services.exe"
  },
  "network": {
    "destination_ip": "185.220.101.5",
    "destination_port": 443
  }
}
```

#### Response (`200 OK`)
```json
{
  "status": "ACCEPTED",
  "event_id": "ecg_9a8f10283c7d",
  "event_hash": "c8a329d91a9b2...",
  "queue_depth": 14,
  "alerts_triggered": 1,
  "alerts": [
    {
      "rule_id": "SIGMA-PS-001",
      "title": "Obfuscated PowerShell Execution",
      "severity": "CRITICAL"
    }
  ]
}
```

---

## 3. Alerts & Incidents (`/api/v1/incidents` & `/api/v1/alerts`)

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/incidents` | List active security incidents filtered by status, severity, and tenant |
| `GET` | `/incidents/{incident_number}` | Retrieve complete incident dossier, MITRE tactics, timeline, and risk breakdown |
| `PATCH` | `/incidents/{incident_number}` | Update incident status (`OPEN`, `INVESTIGATING`, `CONTAINED`, `RESOLVED`) |
| `POST` | `/incidents/{incident_number}/investigate` | Trigger on-demand pipeline execution across all 7 AI agents |
| `GET` | `/incidents/{incident_number}/timeline` | Retrieve chronological forensic event timeline |
| `GET` | `/incidents/{incident_number}/graph` | Retrieve entity relationship graph nodes (assets, users, IPs, processes) |
| `GET` | `/alerts` | Query active real-time alert notifications |
| `POST` | `/alerts/notify` | Dispatch critical alert notification across Webhook, SMS, or Telegram |

---

## 4. Threat Intelligence & Feeds (`/api/v1/threat-intelligence`)

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/threat-intelligence` | Query active indicators (IPs, domains, hashes, URLs) with confidence scores |
| `POST` | `/threat-intelligence/lookup` | On-demand indicator reputation query against Ethio-CERT, MISP, and local cache |
| `GET` | `/threat-intelligence/feeds` | List external threat feed synchronization status and last pull timestamps |
| `POST` | `/threat-intelligence/import` | Ingest external STIX 2.1 or CSV threat indicator packages |
| `GET` | `/threat-intelligence/stats` | Threat intel summary metrics (total active IOCs, high-confidence counts) |

#### Example Lookup Request (`POST /api/v1/threat-intelligence/lookup`)
```json
{
  "indicator_type": "ip",
  "indicator_value": "185.220.101.5"
}
```

#### Response (`200 OK`)
```json
{
  "indicator": "185.220.101.5",
  "reputation": "MALICIOUS",
  "confidence": 98,
  "threat_actor": "Cobalt Strike C2",
  "campaign": "Targeted African Financial Infrastructure",
  "source": "Ethio-CERT Feed / MISP",
  "first_seen": "2026-09-15T08:00:00Z"
}
```

---

## 5. Phishing, Amharic Ge'ez NLP & Telebirr Shield (`/api/v1/phishing`)

Specialized detection pipeline targeting banking phishing, SMS fraudulent lures, and Amharic Ge'ez script scams.

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/phishing/analyze` | Parse email body/headers; extracts URLs, evaluates SPF/DKIM/DMARC, scores risk |
| `POST` | `/phishing/extract-urls` | Deep URL parser; extracts IP-in-URL addresses, port anomalies, and path fragments |
| `POST` | `/phishing/telebirr-scan` | Specialized check for Telebirr brand impersonation, OTP harvest, and bonus scams |
| `POST` | `/phishing/amharic-detect` | Ge'ez NLP detector identifying Amharic social engineering phrases |

#### Example Amharic Phishing Payload
```json
{
  "raw_content": "እንኳን ደስ አሎት! የ10,000 ብር የቴሌብር ቦነስ አሸንፈዋል። ሽልማቱን ለመቀበል ፒን (PIN) ቁጥርዎን ያረጋግጡ፡ http://196.188.99.12/claim",
  "sender": "support@telebirr-bonus.xyz",
  "subject": "የቴሌብር ቦነስ ሽልማት"
}
```

---

## 6. Brand Defense & Typosquatting (`/api/v1/typosquat`)

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/typosquat/scan` | Scan for registered and newly observed typosquats of target domain (e.g. `telebirr.et`) |
| `POST` | `/typosquat/check` | Check single domain candidate against Levenshtein, bitsquatting, and homoglyph algorithms |
| `GET` | `/typosquat/telebirr-brands` | Pre-computed risk index of known lookalike variations for Telebirr and CBE |

---

## 7. OSINT & External Attack Surface Reconnaissance (`/api/v1/osint`)

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/osint/scan` | Execute passive perimeter recon for target domain (DNS records, ASN, open ports) |
| `GET` | `/osint/domain/{domain}` | Query domain DNS MX, SPF, DMARC, nameservers, and certificate transparency |
| `GET` | `/osint/ip/{ip}` | Query IP geolocation, BGP AS route, reverse DNS, and honeypot interaction history |

---

## 8. SOAR Containment & Dual-Custody Approval (`/api/v1/response`)

> [!CAUTION]
> In accordance with ETHIO-CYBERGUARD security invariants, all destructive containment actions (`ISOLATE_HOST`, `BLOCK_IP`, `DISABLE_ACCOUNT`) require human analyst authorization. Actions cannot be executed autonomously by LLMs.

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/response/actions` | Retrieve pending, approved, and executed containment actions |
| `POST` | `/response/isolate-host` | Submit host network isolation request (dry-run or live approval queue) |
| `POST` | `/response/block-ip` | Submit perimeter firewall egress/ingress block request |
| `POST` | `/response/disable-account` | Submit Active Directory / Entra account suspension request |
| `POST` | `/response/actions/{action_id}/approve` | Sign dual-custody authorization and execute containment via connector |
| `POST` | `/response/actions/{action_id}/reject` | Reject containment recommendation with recorded operational justification |
| `POST` | `/response/actions/{action_id}/rollback` | Revert executed action (e.g., reconnect isolated host, remove firewall drop) |
| `GET` | `/response/audit-log` | Retrieve immutable SHA-256 cryptographically chained audit log |

#### Dual-Custody Approval Request (`POST /api/v1/response/actions/ACT-001/approve`)
```json
{
  "reason": "Confirmed C2 beaconing in memory dump. Analyst authorization granted.",
  "operator": "Dawit Mengistu (Security Analyst)"
}
```

---

## 9. External Connectors & Circuit Breakers (`/api/v1/connectors`)

Manages external integration adapters for Next-Gen Firewalls (Palo Alto, Fortinet), EDR agents, DNS Sinkholes, and Secure Email Gateways. Connectors implement the **Circuit Breaker** pattern to protect SOC throughput when downstream APIs experience transient failure.

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/connectors` | List all registered connectors, health statuses, and circuit states (`CLOSED`, `OPEN`, `HALF_OPEN`) |
| `POST` | `/connectors/{connector_id}/test` | Trigger diagnostic heartbeat test against specified connector |
| `POST` | `/connectors/{connector_id}/reset` | Manually reset tripped circuit breaker to `CLOSED` after external service restoration |

---

## 10. Asynchronous Background Jobs (`/api/v1/jobs`)

Long-running forensic jobs (e.g. bulk OSINT scans, multi-gigabyte log analyses, report compilations) execute asynchronously in worker threads.

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/jobs` | Enqueue asynchronous job (`job_type`: `phishing_analysis`, `osint_scan`, `report_generation`) |
| `GET` | `/jobs/{job_id}` | Query execution status (`QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`), progress %, and result |
| `GET` | `/jobs` | List recent background jobs with pagination |

---

## 11. Health, Readiness & Prometheus Telemetry

### Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health/live` | Kubernetes Liveness Probe (process responsiveness ping) |
| `GET` | `/health/ready` | Kubernetes Readiness Probe (verifies DB connection, queue buffer, and connector health) |
| `GET` | `/health` / `/api/v1/health` | System health overview including active WebSocket client count |
| `GET` | `/metrics` | Prometheus format metrics exposition (`ecg_uptime_seconds`, `ecg_websocket_active_connections`, `ecg_ingestion_queue_depth`, `ecg_ingestion_dlq_total`, `ecg_events_per_second_capacity`) |

---

## 12. Real-Time WebSockets (`/ws/live-events`)

Provides low-latency, bidirectional telemetry streaming for the SOC HUD Console. Clients receive incoming alerts, new incident correlations, and background job completions.

### Handshake & Authentication
Connect with query parameter token:
```text
ws://localhost:8000/ws/live-events?token=<JWT_TOKEN>
```

### Initial Server Welcome Message
```json
{
  "type": "CONNECTION_ESTABLISHED",
  "message": "Connected to authenticated ETHIO-CYBERGUARD live SOC telemetry stream",
  "tenant_channel": "tenant:Commercial Bank of Ethiopia",
  "role": "SECURITY_ANALYST",
  "timestamp": "2026-10-09T18:00:00Z"
}
```

### Keepalive Protocol
- Client sends: `ping`
- Server responds: `pong`
