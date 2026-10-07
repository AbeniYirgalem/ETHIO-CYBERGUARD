# AGENTS.md — AI Coding Agent Operating Guide

> **Project**: ETHIO-CYBERGUARD  
> **Repository**: [https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD](https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD)  
> **Domain**: Autonomous AI-Assisted Security Operations Center (SOC), SIEM & Critical Infrastructure Threat Intelligence  
> **License**: Apache-2.0  

---

## 1. System Overview & Architecture

ETHIO-CYBERGUARD is an enterprise cybersecurity platform designed for critical national infrastructure (banking, telecommunications, energy, and government sectors) with native Ethiopian threat intelligence context (INSA compliance, Ethio-CERT feeds, Telebirr phishing protection).

```
[ Telemetry Ingestion ] (WinEvent, Syslog, NetFlow)
         │
         ▼
[ ECS Normalizer ] ───► [ SIGMA Rule Engine ] ───► [ In-Memory / DB Event Store ]
                                  │
                                  ▼
[ 7 Specialized AI Agents ] ───► [ Correlation & Incident Lifecycle Engine ]
                                  │
                                  ▼
[ SOAR Response Playbooks ] ◄─── [ Dual-Custody Approval Gate ] ◄─── [ Web UI / CLI ]
```

### Core Technologies
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, Web Audio API synthesizer.
- **Backend API**: FastAPI, Uvicorn, Python 3.10+, Pydantic v2, SQLite / PostgreSQL.
- **Data & Ingestion**: ECS (Elastic Common Schema) JSON events, SIGMA rule evaluator, geo-IP enrichment.
- **Testing**: `pytest` (54 tests, 100% green pass rate), `tsc -b && vite build`.
- **Security Controls**: Role-Based Access Control (RBAC, 7 tiers), JWT authentication with refresh rotation, dual-custody SOAR approvals.

---

## 2. Directory Structure

```text
ETHIO-CYBERGUARD/
├── apps/
│   ├── api/                 # FastAPI REST application (routes, models, database)
│   │   ├── main.py          # API entrypoint, routes, and middleware
│   │   ├── requirements.txt # Backend Python dependencies
│   │   └── ...
│   └── web/                 # React 19 frontend
│       ├── src/
│       │   ├── components/  # SOC dashboard views, modals, HUD palette, radar
│       │   ├── utils/       # Sound synthesizer, formatters
│       │   └── types.ts     # TypeScript interface definitions
│       └── package.json
├── services/                # Seven specialized AI security agents
│   ├── event_analysis/      # Anomaly scoring & triage agent
│   ├── threat_intel/        # IOC correlation & MISP/Ethio-CERT feed agent
│   ├── correlation/         # Multi-source incident correlation agent
│   ├── investigation/       # Automated evidence gathering agent
│   ├── risk_assessment/     # Explainable risk formula evaluator
│   ├── executive_report/    # Board-level executive briefing generator
│   └── assistant/           # Conversational interactive SOC Copilot
├── detection/               # Detection engine & SIGMA rule evaluator
├── playbooks/               # SOAR automation playbooks (quarantine, block IP, disable user)
├── tests/                   # Pytest automated test suite (unit, integration, security)
└── .github/                 # Workflows (CI, Pages deployment, Docker package)
```

---

## 3. Development Setup & Commands

### Prerequisites
- Python 3.10 or higher
- Node.js 20 or higher, with `npm`

### Backend Setup
```bash
# Install dependencies
pip install -r apps/api/requirements.txt
pip install -r requirements-dev.txt

# Run backend API server
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup
```bash
# Navigate to web application
cd apps/web
npm install

# Start local development server
npm run dev

# Run production build & type checks
npm run build
```

---

## 4. Testing & Quality Verification

All automated tests MUST pass with 100% success before submitting changes or pushing commits.

```bash
# Run entire test suite (54 unit, integration, and security tests)
python -m pytest tests/ -v

# Run targeted test suites
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/security/ -v

# Verify frontend TypeScript compilation and bundle packaging
npm --prefix apps/web run build
```

---

## 5. Security & Invariant Rules for AI Agents

When editing or proposing changes to this codebase, always preserve the following core security invariants:

1. **Dual-Custody SOAR Approval**: Destructive mitigation actions (`isolate_host`, `block_ip`, `suspend_account`) MUST require approval from a certified Security Analyst or Incident Responder. Never bypass the approval state machine.
2. **Tenant Isolation**: Data access queries must always filter by `tenant_id` / `organization`. Never allow cross-organization data leakage.
3. **No Hardcoded Secrets**: Use environment variables (`.env`) for secrets, API tokens, and database credentials.
4. **ECS Schema Compliance**: All telemetry events ingested into the pipeline must conform to the Elastic Common Schema (`timestamp`, `source`, `destination`, `user`, `process`, `event_type`).
5. **No Broken Links or Missing Assets**: Always ensure Vite `base: './'` is preserved and that all static assets and icons compile without warnings.
