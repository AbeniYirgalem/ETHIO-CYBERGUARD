# 📋 ETHIO-CYBERGUARD Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
