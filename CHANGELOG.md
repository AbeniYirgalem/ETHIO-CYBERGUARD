# 📋 ETHIO-CYBERGUARD Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
