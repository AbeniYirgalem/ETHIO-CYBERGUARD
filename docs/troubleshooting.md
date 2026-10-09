# 🔧 Troubleshooting & Operational Guide

**Platform Version**: 1.1.0  
**Target Audience**: SOC Engineers, System Administrators, DevOps Operators  

---

## 1. Backend API Diagnostics

### Issue: `Port 8000 already in use`
- **Cause**: An orphaned `uvicorn` instance or background process is bound to port 8000.
- **Remediation**:
  ```powershell
  # Windows PowerShell:
  Get-NetTCPConnection -LocalPort 8000 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
  ```
  ```bash
  # Linux / macOS:
  lsof -i :8000 | awk 'NR>1 {print $2}' | xargs -r kill -9
  ```

### Issue: `ModuleNotFoundError: No module named 'services'`
- **Cause**: Command executed from a subfolder rather than the repository root, omitting root modules from `PYTHONPATH`.
- **Remediation**: Always execute `uvicorn` and `pytest` from the root repository directory:
  ```bash
  python -m uvicorn apps.api.main:app --reload
  ```

### Issue: `503 Service Unavailable on /health/ready`
- **Cause**: Kubernetes readiness probe failed because a dependency (Database, Ingestion Queue, or Connectors) is unhealthy.
- **Remediation**: Query the diagnostic details:
  ```bash
  curl -s http://localhost:8000/health/ready | jq .
  ```
  Inspect the `checks` dictionary to pinpoint whether the issue is database connectivity or connector timeouts.

---

## 2. Ingestion & Connector Diagnostics

### Issue: Ingestion Returns `429 Too Many Requests`
- **Cause**: Collector exceeded the sliding-window rate limit (default: 60,000 requests/minute per client).
- **Remediation**:
  - Verify that the collector is not in an aggressive retry loop.
  - Enable batch ingestion via `/api/v1/events/batch` rather than single-event posts.
  - Tune `MAX_INGESTION_RATE` in `.env` if legitimate burst traffic is expected.

### Issue: Ingestion Events Not Appearing in Alerts / DLQ Spike
- **Cause**: Malformed payload rejected by schema ingress validator and routed to Dead-Letter Queue.
- **Remediation**: Inspect the DLQ buffer:
  ```bash
  curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/v1/events/dead-letter-queue
  ```
  Check the `validation_error` field to identify missing ECS fields (e.g., missing `event_type` or unparseable timestamp).

### Issue: External Connector Status is `OPEN` (Circuit Breaker Tripped)
- **Cause**: 5 consecutive connection timeouts or failures occurred while communicating with the external firewall or EDR gateway.
- **Remediation**:
  1. Test external gateway availability via `/api/v1/connectors/{connector_id}/test`.
  2. Once the external appliance is operational, reset the circuit breaker:
     ```bash
     curl -X POST http://localhost:8000/api/v1/connectors/firewall/reset
     ```

---

## 3. Frontend Web Console & WebSocket Diagnostics

### Issue: WebSocket Fails to Establish Connection (`ws://localhost:8000/ws/live-events`)
- **Remediation**:
  1. Confirm the backend is running and listening on port 8000.
  2. Verify that the client origin is permitted in `.env` under `ALLOWED_ORIGINS` (e.g., `http://localhost:5173`, `http://localhost:3000`).
  3. Ensure a valid JWT token query parameter is passed (`?token=<JWT>`) if running in authenticated mode.

### Issue: Dual-Custody Approval Returns `Action approval has expired`
- **Cause**: The 30-minute authorization window for the containment recommendation has elapsed.
- **Remediation**: Re-submit the containment recommendation from the Incident Dossier view, or re-run the AI Risk Assessment agent.

### Issue: Sound Alarms Not Audible
- **Cause**: Web Audio API requires a user gesture (click or keypress) before playing audio to prevent browser auto-play blocks.
- **Remediation**: Click anywhere on the HUD console or toggle the audio mute key (<kbd>M</kbd>) to initialize the audio context.
