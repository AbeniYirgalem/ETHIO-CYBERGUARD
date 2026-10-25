# 📋 ETHIO-CYBERGUARD Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.5.0] - 2026-10-24

### Added
- **Shared security state through Redis** (`services/security/shared_state.py`). The per-IP login rate limit, revoked access/refresh token ids, revoked session families and used refresh tokens are now visible to every API worker, so a logout or a refresh-token replay on one worker is enforced on all of them. Refresh-token first-use is decided atomically (`SET NX`).
- `SHARED_STATE_BACKEND` (`auto` | `redis` | `memory`). `auto` uses Redis only in production (`DEMO_MODE=false`) with `REDIS_URL` set and the `redis` package installed; demo mode and tests stay in memory. `docker-compose.prod.yml` sets it to `redis`.
- `/health/ready` reports `shared_state` (`backend`, `multi_worker_safe`).
- Saved revocations are re-published to Redis at startup, so a flushed or new Redis does not forget a logout.
- `tests/security/test_shared_state.py` (12 tests, two workers simulated with one shared client).

### Changed
- Redis trouble never stops the API: a failing call is logged once and answered from the process-local fallback, and Redis is not retried for 15 s so requests do not wait on timeouts.
- Rate limiting through Redis uses a fixed one-minute window (a client can briefly send up to twice the limit across a window boundary).
- CI coverage gate raised from 40 to 75 (measured coverage: 83%). `.coverage` and other coverage output are no longer tracked by git.
- New dependency: `redis>=5.0.0`.

### Known limit
- Incidents, SOAR actions, the audit log, telemetry and the user list are still saved as JSON snapshots that one worker writes at a time. Keep **one API worker per database** until those collections move to relational tables; only the security state above is multi-worker ready.

---

## [1.4.0] - 2026-10-24

### Security
- **Refresh-token rotation with reuse detection.** Refresh tokens are now single-use. Every login starts a session family (`fid` claim); each refresh returns a new pair in the same family and marks the old refresh token as used. If a used token is presented again after a short grace window (`REFRESH_REUSE_GRACE_SECONDS`, default 10, so two browser tabs refreshing together are not logged out), the whole family is revoked: the thief and the victim both have to sign in again. Other logins of the same user (other devices) are not affected.
- **Logout ends the whole login family**, so tokens rotated earlier in that login stop working too.
- Used-token and revoked-family lists are saved with the state store, so a restart does not forget them. Tokens issued before this release (no `fid`) keep working and join a family on their next refresh.

### Added
- **Measured MTTD and MTTR** (`services/telemetry/response_metrics.py`). `/api/dashboard/stats` now returns real averages instead of `null`: MTTD = minutes from `first_seen` to the first analyst action; MTTR = minutes from `first_seen` to the first CONTAINED/CLOSED. Incidents that have not reached the milestone are left out; with no data the value stays `null`. A `response_metrics` block reports how many incidents each average is based on. The Overview card shows both.
- CI: `dependency-audit` job (`pip-audit`, `npm audit --omit=dev --audit-level=high`), a weekly scheduled run, and a test-coverage gate (`COVERAGE_MIN`, starts at 40).
- `tests/security/test_refresh_rotation.py` and `tests/unit/test_response_metrics.py`.

---

## [1.3.0] - 2026-10-24

### Security
- **Per-organization isolation.** Incidents, SOAR actions, the audit log, dashboard numbers, event statistics, the AI assistant, reports and the live WebSocket stream are now limited to the signed-in user's organization. SUPER_ADMIN is the national administrator and sees every organization. Another organization's record answers "404 not found", never "403", so its existence is not revealed.
- **Reports were readable without logging in.** `/api/reports/*` now needs a login (guest only in demo mode).
- **AI assistant fallback leak.** An unknown incident number used to fall back to the first incident of any organization; it now falls back to the caller's own, or returns 404 when the organization has none.
- **Event deduplication no longer crosses organizations.** The organization id is part of the duplicate fingerprint, and the collector rate limit is per organization and host.
- The WebSocket handshake now takes the role and organization from the live account (not from token claims), and rejects a session retired by a password reset, like the REST API.

### Added
- `services/security/tenancy.py` (organization helpers) and `apps/api/tenancy.py` (collector organization resolver).
- **Collector keys decide the organization.** `INGEST_ORG_KEYS` (key:organization pairs) and `INGEST_DEFAULT_ORG` in `.env.example`. In demo mode only, an `X-Org-ID` header lets one server simulate several organizations.
- Per-organization telemetry (`TelemetryRegistry`): separate counters, severity mix, detections and timeline per organization, saved and restored across restarts. The national total is kept for SUPER_ADMIN.
- `/api/dashboard/stats` reports a `tenant` block (`org_id`, `scope`).
- `tests/unit/test_tenancy.py` and `tests/security/test_tenant_api_isolation.py`.

### Changed
- Audit entries carry `org_id`. The SHA-256 hash chain is unchanged and still one chain for the whole platform; `/audit-log/verify` checks it in full but tells an organization only about its own entries.
- Records saved before this release have no `org_id` and belong to Commercial Bank of Ethiopia, so existing data keeps working.
- A user's organization comes from their account's `organization` name (for example "Awash Bank" becomes `org_awash_bank`).

---

## [1.2.1] - 2026-10-24

### Added
- **Real Threat Activity Timeline.** `/api/dashboard/stats` (and the WebSocket snapshot) now include `timeline`: events, critical events and detections per UTC hour for the last 24 hours. The Overview chart draws these instead of fixed bars, labelled in the viewer's local time, with an empty-state message when nothing has been ingested.
- **Event statistics survive restarts.** Today's counters, severity mix, top detections and the hourly history are saved through the state store (at most every 5 s, and flushed at shutdown) and restored at startup. Corrupt saved data is ignored; a failing database never blocks ingestion.
- `sector_profiles` in the dashboard payload now carries `critical`, `high` and `max_severity` per sector.
- `tests/unit/test_telemetry_history.py`.

### Changed
- **Top Threat Vectors** shows real detections (or, before any telemetry, open incidents) when signed in.
- **Ethiopia radar** in live mode places open incidents on nodes by asset IP range, shows sector totals, and no longer displays invented throughput, latency, firewall or compliance values (it says "Not monitored"). Signed out, it keeps the simulated grid and is now labelled `SIMULATED`.

---

## [1.2.0] - 2026-10-24

### Added
- **Real Overview numbers.** `/api/dashboard/stats` is now calculated from the live stores: active/critical/high incidents, actions awaiting approval, audit entries, and events counted from the ingestion endpoint (events per second over a 60 s window, events today, severity mix, top detections). It needs a login. MTTD/MTTR are `null` until they are measured, instead of invented figures.
- **Live event stream.** `POST /api/v1/events/ingest` pushes each accepted event (and any detection alerts) to connected SOC consoles over the authenticated WebSocket. The web app, when signed in, shows these real events instead of the browser simulation, refreshes its numbers, and raises a toast when a detection fires. The WebSocket reconnects with backoff and refreshes an expired token.
- `scripts/demo/send_events.py` to send sample events to a running API.
- `services/telemetry/stats.py`.
- `tests/unit/test_live_pipeline.py` (10 tests).

### Fixed
- `POST /api/v1/events/ingest` crashed on every call (it read a `host_name` field that does not exist, and passed empty `process`/`network` values to the normalizer).
- Duplicate detection hashed fields the normalizer never produces, so after the first event of a given type every later event of that type was dropped as a duplicate. The hash now covers the event id, timestamp, user, host, network and command line.

### Changed
- Signed out (or offline) the Overview still shows the simulated demo figures, labelled `SIMULATED`.

---

## [1.1.9] - 2026-10-24

### Security
- **Per-IP rate limit** on login, refresh and password-reset (`AUTH_RATE_LIMIT_PER_MINUTE`, default 10, on by default when `DEMO_MODE=false`). It stops password spraying across many accounts, which the per-account lockout cannot see. Over the limit returns `429` with `Retry-After`.
- **Security headers** on every response: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, a locked-down `Content-Security-Policy` and, in production, `Strict-Transport-Security`. Auth responses are `no-store`.
- `X-Forwarded-For` is only trusted when `TRUST_PROXY=true`, and only its last entry (the one the proxy added).
- Interactive docs (`/docs`, `/redoc`) are disabled when `DEMO_MODE=false`.
- API container runs as a non-root user.

### Fixed
- `infrastructure/docker/Dockerfile.api` did not copy `scripts/`, `playbooks/` or `detection-rules/`, so the API container could not start (`main.py` imports `scripts.benchmark_eps`).
- Removed `apps/api/batch-4-ethio-cyberguard.zip`, which had been committed by mistake; `*.zip` is now ignored.

### Added
- `docker-compose.prod.yml`: required secrets, `DEMO_MODE=false`, no published database ports, health-checked start order.
- Health checks and `service_healthy` ordering in `docker-compose.yml`; PostgreSQL and Redis bind to `127.0.0.1` only.
- Web image: Nginx security headers, immutable asset caching, SPA fallback, health check; `VITE_API_URL` build argument.
- `.dockerignore` files.
- CI: Python 3.10 and 3.13 matrix, pip/npm caching, web lint, Docker image builds, compose validation and an API container health check.
- `tests/security/test_security_middleware.py` (11 tests).

---

## [1.1.8] - 2026-10-23

### Security
- **Logout now really ends the session.** `POST /api/auth/logout` revokes the presented access token and (if sent) the refresh token. Every token carries a unique `jti`; revoked IDs are persisted until the token expires, so a restart cannot undo a logout. Logout is idempotent and never fails on an expired or malformed token.
- **Password reset retires old sessions.** Each user has a `token_version`; resetting a password bumps it, so access and refresh tokens issued earlier stop working immediately.
- Production mode rejects tokens whose account no longer exists (`401`), instead of trusting the role written in the token.

### Added
- **User accounts persist** across restarts (including password changes and token versions). Default demo accounts are never restored into a production database, and the bootstrap administrator always comes from the environment.
- Web app: administrators get a **User Management** panel in Settings (create users with role and password policy checks). Signing out now revokes the session on the server.
- `tests/security/test_session_revocation.py` (11 tests).

---

## [1.1.7] - 2026-10-23

### Security (critical)
- **Closed an anonymous admin takeover.** `POST /api/auth/register` was public and honored a client-supplied `role`, so anyone could create a `SUPER_ADMIN` and receive tokens. Registration now requires the `user:admin` permission, validates the role, enforces the password policy, and returns no tokens.
- **Closed account takeover via password reset.** `POST /api/auth/password-reset` returned the reset token to the caller for any email. The token is now delivered out-of-band (server log until email/SMS is connected), stored only as a SHA-256 digest, single-use, limited to 3 live tokens per account, and the endpoint answers identically for known and unknown emails.
- **Passwords:** salted PBKDF2-SHA256 (random salt, versioned format) with constant-time verification, replacing unsalted SHA-256 for API users and a fixed global salt in `database/connection.py`. Legacy database hashes still verify. New policy: 12+ characters mixing three character classes.
- **No default accounts in production.** With `DEMO_MODE=false` the demo users are not created (in memory or in the database), `/api/auth/demo-credentials` returns 404, and the app requires `BOOTSTRAP_ADMIN_EMAIL` / `BOOTSTRAP_ADMIN_PASSWORD` to start.
- Login spends equal time for unknown users to avoid revealing which emails exist.
- `POST /api/v1/alerts/notify`, `POST /api/v1/pipeline/execute-slice` and `GET /api/v1/benchmark/run` now require a login (benchmark: administrators only, `events` limited to 100–50000). Alert payloads are validated (`channel` limited to `webhook`/`email`, bounded lengths and scores).
- WebSocket `/ws/live-events`: an invalid token is rejected (previously silently downgraded to guest) and production mode requires a token.

### Added
- `services/security/passwords.py`, `scripts/hash_password.py`, `tests/security/test_auth_hardening.py` (21 tests).

### Changed
- Registration is administrator-only and no longer returns tokens. Users created through the API live in memory until user persistence ships.

---

## [1.1.6] - 2026-10-23

### Added
- **Persistence.** Incidents, SOAR actions and the SHA-256 audit log now survive API restarts (`database/state_store.py`). SQLite by default, PostgreSQL when `DATABASE_URL` points to it. Disable with `PERSISTENCE_ENABLED=false`.
- `GET /api/v1/response/audit-log/verify` recomputes the audit hash chain and reports tampered entries.
- `GET /api/v1/incidents/{id}` (authenticated) in the incidents router.
- `database/migrations/003_state_documents.sql` and `tests/unit/test_persistence.py` (8 tests).

### Security
- Removed the unauthenticated `GET /api/v1/incidents/{incident_number}` route from `main.py` (it served mock data to anyone).
- Removed 10 dead duplicate routes and the mock incident/action lists from `main.py`; the authenticated routers own these paths.

### Fixed
- Docker: added `psycopg2-binary` to both requirements files. Previously a `postgresql://` `DATABASE_URL` crashed the API at startup.
- Tests always run on a throw-away SQLite database and can never touch a real one.
- Demo seed recommendations (ACT-001/002) are re-armed on startup so they stay approvable after a restart (demo mode only).

---

## [1.1.5] - 2026-10-23

### Added
- Web app now loads threat intelligence and the SOAR audit log from the API when signed in.
- Security Assistant sends questions to `/api/ai/chat` when signed in (local scripted replies when offline).
- Incidents "Audit Log" tab shows the real hash-chained audit trail (with SHA-256 prefix) in live mode.
- `tests/security/test_ai_threatintel_auth.py`.

### Security
- Threat-intelligence routes and all AI routes now require a login (`401` when `DEMO_MODE=false`).
- Importing indicators now requires the `rules:edit` permission.

---

## [1.1.4] - 2026-10-22

### Security
- All incident routes now require a login (`401` without a token when `DEMO_MODE=false`). Previously `GET /api/incidents` and most write routes were open to anyone.
- Incident writes (create, update, transition, comments, tasks, evidence) now require the `incident:assign` permission, so `AUDITOR`, `READ_ONLY` and `THREAT_HUNTER` can read but not change incidents.

### Changed
- Settings: the "Simulated RBAC Role" switcher is read-only while signed in to the live API (the role comes from the server). It still works in simulated demo mode.

### Added
- `tests/security/test_incidents_auth.py`.

---

## [1.1.3] - 2026-10-22

### Added
- Web app talks to the real backend: sign-in via `/api/auth/login`, live incidents and SOAR approvals (`apps/web/src/api/client.ts`).
- Login modal with demo-account hints; session kept in `sessionStorage` with automatic token refresh.
- `VITE_API_URL` setting (default `http://localhost:8000`).
- Approval note field; reviewer name and queue time now come from the API.

### Changed
- When signed out or when the backend is offline, the UI falls back to the built-in simulated data (GitHub Pages demo still works). A header strip shows `LIVE API` or `SIMULATED`.
- Approve/reject errors from the server (for example the dual-custody `403`) are shown to the user.

### Removed
- `apps/api/routes/response.py`: an old insecure duplicate of the SOAR router that nothing imported.

---

## [1.1.2] - 2026-10-22

### Security
- **Guest access is demo-only.** With `DEMO_MODE=false`, requests without a token now get `401` instead of silently acting as a guest `SECURITY_ANALYST`.
- **Real dual custody.** The user who requests a containment action can no longer approve it (`403`); a second authorized person must.
- **Production refuses weak secrets.** With `DEMO_MODE=false` the API will not start with default, short, or placeholder `JWT_SECRET` / `INGEST_API_KEY`.
- `API_SECRET_KEY` (used by docker-compose and `.env.example`) is now honored as an alias of `JWT_SECRET`; previously the hardcoded default key was always used.
- Removed unguarded duplicate SOAR routes from `apps/api/main.py` (shadowed by the authenticated router, but misleading).

### Fixed
- `.gitignore` no longer ignores every `__init__.py` file (a fresh clone was missing them).

### Added
- `.gitattributes` for consistent LF line endings.
- `tests/security/test_dual_custody_and_auth.py` (8 tests).

---

## [1.1.1] - 2026-10-22

### Security
- Added a dedicated `response:approve` permission. Approving, rejecting, and rolling back SOAR containment actions is now limited to `SUPER_ADMIN`, `SOC_MANAGER`, and `INCIDENT_COMMANDER`. `SECURITY_ANALYST` and `INCIDENT_RESPONDER` can request actions but can no longer approve them (previously any role holding `playbook:execute` could).

### Fixed
- Repaired 6 stale tests that were failing after the SOAR routes started requiring a real bearer token. Tests now log in through shared `admin_headers` / `commander_headers` fixtures in `tests/conftest.py`.
- Updated SOAR tests to match the hardened workflow (live actions require approval, dry-run actions cannot be approved).

### Changed
- Documented test count is now 112 (README, AGENTS.md).

---

## [1.1.0] - 2026-10-09

### Added
- **Unified Pipeline Engine & Common Security Graph**:
  - `services/pipeline/unified_engine.py`: Single end-to-end vertical slice linking Ingestion → ECS → SIGMA → Correlation → 7 AI Agents → Dual-Custody SOAR → Audit Log.
  - Interactive 6-scenario demonstration presets in `apps/web/src/components/UnifiedPipelineView.tsx`.
- **Specialized Security Subsystems**:
  - `services/phishing/`: RFC-822 email parser (`eml_parser.py`), cryptographic SPF/DKIM/DMARC verifier (`auth_verifier.py`), Amharic/Ge'ez script detector (`amharic_detection.py`), attachment hazard scanner (`attachment_analysis.py`), and URI heuristics (`url_analysis.py`).
  - `services/typosquat/domain_monitor.py`: openSquat-inspired permutation generator and Levenshtein string distance engine.
  - `services/osint/surface_recon.py`: SpiderFoot-inspired attack surface scanner with Ethiopian ASN discovery (`AS24757`).
  - `services/awareness/simulator.py`: CyberSatark-inspired phishing simulation and training platform.
- **Enterprise Controls & Governance**:
  - `scripts/benchmark_eps.py`: Verified multi-threaded load generator and throughput benchmark (> 51,000 EPS).
  - `services/alerting/notifier.py`: Multi-channel Slack/Teams webhook and bilingual Amharic/English email alerting.
  - `services/incident/lifecycle.py`: 7-stage incident progression with forensic evidence custody and SHA-256 hashing.
  - `services/security/rbac.py`: Role-based access control matrix and dual-custody authorization boundaries for containment actions.
  - `services/response/audit.py`: Cryptographically block-chained SHA-256 immutable audit ledger with automated tamper detection.
- **Modernized Backend & Frontend Toolchains**:
  - `apps/api/main.py`: Modernized FastAPI ASGI lifespan `@asynccontextmanager` lifecycle handler, completely eliminating startup deprecations.
  - `apps/web/vite.config.ts`: Configured Vite v8 / Rolldown manual chunk splitting (`manualChunks`), separating `vendor` (React) and `lucide` icon bundles to achieve sub-270 kB bundle sizes.
  - Upgraded dependencies: FastAPI 0.142+, SQLAlchemy 2.1.3+, Alembic 1.20+, Vite 8.3.2+, and Lucide-React 1.52+.
- **Architectural Documentation & Research**:
  - Comprehensive Technical White Paper ([`docs/ETHIO_CYBERGUARD_TECHNICAL_PAPER.md`](docs/ETHIO_CYBERGUARD_TECHNICAL_PAPER.md)).
  - STRIDE Threat Model (`docs/threat-model.md`).
  - Privacy and Data Governance Framework (`docs/privacy-data-governance.md`).
  - Backup and Disaster Recovery Guide (`docs/backup-recovery.md`).
- **Testing & Verification**:
  - Expanded test suite from 16 to **75 passing tests** (100% green pass rate) across unit, security, integration, and AI evaluation suites:
    - Added `tests/unit/test_platform_hardening.py` (15 tests).
    - Added `tests/unit/test_api_extended.py` (5 tests).
    - Increased backend service line coverage to **79% to 100%**.

### Fixed
- Fixed IPv4 host extraction slice bug in `/api/phishing/extract-urls`.
- Resolved React Compiler render purity warning in `AssistantView.tsx` via `useCallback`.
- Fixed cascading render warning in `CommandPalette.tsx` by deferring input focus and query resets.
- Preserved Vite Fast Refresh in `EthiopiaCyberRadar.tsx` by unexporting private node coordinates.

---

## [1.0.0] - 2026-09-30

### Added
- Initial full-stack implementation of ETHIO-CYBERGUARD.
- FastAPI central backend (`apps/api`) with JWT auth, ECS normalization, incident management, and SOAR execution.
- React SOC dashboard (`apps/web`) with Overview, Incidents, Threat Intel, Assistant, and Simulator views.
- 7 specialized AI agents with orchestrator (`services/ai/`).
- Database schema (`database/schema.sql`) and realistic Ethiopian enterprise seeds (`database/seeds/seeds.sql`).
- SIGMA YAML detection rules (`detection-rules/`).
- Automated GitHub Actions CI and GitHub Pages deployment workflows.
- Docker Compose multi-container production configuration.
- Apache 2.0 Open Source License.
