# 📋 ETHIO-CYBERGUARD Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-09-30

### Added
- **Unified Pipeline Engine & Common Security Graph**:
  - `services/pipeline/unified_engine.py`: Single end-to-end vertical slice linking Ingestion → ECS → SIGMA → Correlation → 7 AI Agents → Dual-Custody SOAR → Audit Log.
  - Interactive 6-scenario demonstration presets in `apps/web/src/components/UnifiedPipelineView.tsx`.
- **Specialized Security Subsystems**:
  - `services/phishing/`: RFC-822 email parser (`eml_parser.py`), cryptographic SPF/DKIM/DMARC verifier (`auth_verifier.py`), and Amharic/English fraud scoring (`risk_scorer.py`).
  - `services/typosquat/domain_monitor.py`: openSquat-inspired permutation generator and Levenshtein string distance engine.
  - `services/osint/surface_recon.py`: SpiderFoot-inspired attack surface scanner with Ethiopian ASN discovery (`AS24757`).
  - `services/awareness/simulator.py`: CyberSatark-inspired phishing simulation and training platform.
- **Enterprise Controls & Governance**:
  - `scripts/benchmark_eps.py`: Verified multi-threaded load generator and throughput benchmark (> 51,000 EPS).
  - `services/alerting/notifier.py`: Multi-channel Slack/Teams webhook and bilingual Amharic/English email alerting.
  - `services/incident/lifecycle.py`: 7-stage incident progression with forensic evidence custody and SHA-256 hashing.
  - `services/security/rbac.py`: Role-based access control matrix and dual-custody authorization boundaries for containment actions.
- **Architectural Documentation**:
  - STRIDE Threat Model (`docs/threat-model.md`).
  - Privacy and Data Governance Framework (`docs/privacy-data-governance.md`).
  - Backup and Disaster Recovery Guide (`docs/backup-recovery.md`).
- **Testing**:
  - Expanded test suite from 16 to **23 passing tests** across unit, security, integration, and AI evaluation suites.

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
