# 🌐 ETHIO-CYBERGUARD REST & WebSocket API Specification

## Base URL
- Production: `https://soc.ethio-cyberguard.et/api/v1`
- Development: `http://localhost:8000/api/v1`

---

## 1. Authentication & Users
- `POST /auth/login`: Authenticate via email & password, returns JWT bearer token.
- `GET /auth/me`: Returns current authenticated analyst profile and RBAC role.
- `POST /auth/mfa/verify`: Validates TOTP two-factor code.

---

## 2. Ingestion & Events
- `POST /events/ingest`: Ingest raw or pre-normalized security events from collectors.
  - **Headers**: `X-Agent-Key: <token>`
  - **Payload**: Standard event dictionary (process, network, source, user).
  - **Response**: `200 OK` with generated `event_id` and array of triggered alerts.
- `GET /events`: Paginated list of events with query filters (`hostname`, `severity`, `since`).

---

## 3. Alerts & Incidents
- `GET /alerts`: Query active alerts categorized by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
- `GET /incidents`: Query all security incidents with status (`OPEN`, `INVESTIGATING`, `CONTAINED`, `RESOLVED`).
- `GET /incidents/{incident_number}`: Retrieve complete incident dossier including:
  - Incident metadata & risk breakdown
  - Chronological timeline events
  - Attack relationship graph nodes & links
  - Multi-agent AI investigation outputs
- `PATCH /incidents/{incident_number}`: Update incident status or assign to an analyst.

---

## 4. Threat Intelligence
- `GET /threat-intelligence`: List active threat indicators (IPs, domains, hashes, actors).
- `POST /threat-intelligence/lookup`: On-demand reputation lookup for a specific indicator.

---

## 5. Multi-Agent AI Endpoints
- `POST /ai/investigate/{incident_number}`: Trigger on-demand pipeline execution of the 7 AI agents.
- `POST /ai/assistant/chat`: Grounded interactive conversational endpoint.
  - **Payload**: `{"query": "Why is INC-00042 critical?", "incident_number": "INC-00042"}`
  - **Response**: Response text with telemetry citations.

---

## 6. Response & Human Approval
- `GET /response/actions`: Retrieve pending and executed containment actions.
- `POST /response/actions/{action_id}/approve`: Analyst approval to execute action.
- `POST /response/actions/{action_id}/reject`: Analyst rejection with justification note.

---

## 7. Reports
- `GET /reports/{incident_number}/technical`: Export Markdown technical forensic report.
- `GET /reports/{incident_number}/executive`: Export Markdown executive briefing.
