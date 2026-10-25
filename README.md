<div align="center">

# 🛡️ ETHIO-CYBERGUARD
### Autonomous AI-Powered Security Operations Center & Critical Infrastructure Threat Intelligence
#### የኢትዮጵያ ወሳኝ መሰረተ-ልማቶች የሳይበር ደህንነት፣ የስጋት መረጃ እና የፈጣን ምላሽ ማዕከል

```text
+--------------------------------------------------------------------------------------------------+
|  [>] SYSTEM: ETHIO-CYBERGUARD NATIONAL SOC COMMAND          [STATUS: DEFCON-2 // ELEVATED]       |
+--------------------------------------------------------------------------------------------------+
|                                                                                                  |
|                       ______________  __________                                                 |
|                      / ____/_  __/ / / /  _/ __ \                                                |
|                     / __/   / / / /_/ // // / / /                                                |
|                    / /___  / / / __  // // /_/ /                                                 |
|                   /_____/ /_/ /_/ /_/___/\____/                                                  |
|                                                                                                  |
|       ________  ______  __________  ________  _____    ____  ____                                |
|      / ____/\ \/ / __ )/ ____/ __ \/ ____/ / / /   |  / __ \/ __ \                               |
|     / /      \  / __  / __/ / /_/ / / __/ / / / /| | / /_/ / / / /                               |
|    / /___    / / /_/ / /___/ _, _/ /_/ / /_/ / ___ |/ _, _/ /_/ /                                |
|    \____/   /_/_____/_____/_/ |_|\____/\____/_/  |_/_/ |_/_____/                                 |
|                                                                                                  |
|  [+] 7 SPECIALIZED AI AGENTS   [+] 51,000+ EPS SIGMA ENGINE   [+] NATIVE ETHIOPIAN THREAT INTEL  |
|  [+] INSA DIRECTIVE COMPLIANT  [+] DUAL-CUSTODY SOAR ACTION   [+] TELEBIRR & CBE FRAUD SHIELD    |
+--------------------------------------------------------------------------------------------------+
```

<p align="center">
  <strong>Autonomous AI SIEM, Threat Intelligence & Human-in-the-Loop Incident Response</strong>
  <br />
  <strong>በአርቴፊሻል ኢንተለጀንስ የተደገፈ የሳይበር ደህንነት ክትትል፣ የስጋት መረጃ እና የሰው ማረጋገጫ ያለው ፈጣን ምላሽ</strong>
  <br />
  <em>Defending Ethiopian Banking, Telecommunications, Government & Critical Infrastructure Networks.</em>
  <br />
  <em>የኢትዮጵያ ባንኮችን፣ ቴሌኮሙኒኬሽንን፣ የኤሌክትሪክ ሃይልን እና የመንግስት ተቋማትን ከሳይበር ጥቃት የመከላከል ብሄራዊ መድረክ።</em>
</p>

<p align="center">
  <a href="https://mr-nobody-anonymous.github.io/ETHIO-CYBERGUARD/"><img src="https://img.shields.io/badge/⚡_Live_SOC_Demo-Active_Online-00D9FF?style=for-the-badge&logo=github&logoColor=black" alt="Live Demo" /></a>
  <img src="https://img.shields.io/badge/Defense_Status-DEFCON_2-FF1744?style=for-the-badge" alt="DEFCON 2" />
  <img src="https://img.shields.io/badge/AI_Engine-7_Specialized_Agents-9333EA?style=for-the-badge&logo=openai" alt="7 AI Agents" />
  <img src="https://img.shields.io/badge/Throughput-51,000+_EPS-00D9FF?style=for-the-badge&logo=speedtest" alt="51k+ EPS" />
  <img src="https://img.shields.io/badge/Automated_Tests-279%2F279_Passing-22C55E?style=for-the-badge&logo=pytest" alt="279/279 Passing" />
  <img src="https://img.shields.io/badge/Frontend-React_19_+_Tailwind-22C55E?style=for-the-badge&logo=react" alt="React 19" />
  <img src="https://img.shields.io/badge/Backend-FastAPI_Python_3.10+-F59E0B?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue?style=for-the-badge" alt="License" /></a>
</p>

<p align="center">
  <a href="https://mr-nobody-anonymous.github.io/ETHIO-CYBERGUARD/">
    <img src="./docs/images/platform-overview.png" alt="ETHIO-CYBERGUARD Centralized Threat Detection & AI Investigation Platform" width="100%" />
  </a>
</p>

</div>

---

## 📋 Table of Contents

1. [Project Overview](#-1-project-overview)
2. [Main Features](#-2-main-features)
3. [System Architecture](#-3-system-architecture)
4. [Live Demo URL](#-4-live-demo-url)
5. [Operational Workspaces](#-5-operational-workspaces)
6. [Quick Start Guide](#-6-quick-start-guide)
7. [Environment Configuration](#-7-environment-configuration)
8. [Core API Endpoints](#-8-core-api-endpoints)
9. [Testing & Quality Verification](#-9-testing--quality-verification)
10. [Production Notes](#-10-production-notes)
11. [Roadmap](#-11-roadmap)
12. [Contribution & License](#-12-contribution--license)
13. [Project Team & Contributors](#-13-project-team--contributors)

---

## 💡 1. Project Overview

**ETHIO-CYBERGUARD** is an enterprise-grade cybersecurity operations platform designed to defend corporate, financial, governmental, and critical infrastructure networks. It unifies high-throughput SIEM log telemetry ingestion, real-time SIGMA detection, automated MITRE ATT&CK correlation, multi-agent AI incident investigation, and human-in-the-loop SOAR response workflows.

Unlike conventional Western-centric SIEM/SOAR platforms, ETHIO-CYBERGUARD incorporates native detection heuristics for **Ethiopian regional threat vectors**:
- **Financial & Mobile Money Fraud**: Impersonation detection for Telebirr, Commercial Bank of Ethiopia (CBE), Awash Bank, Dashen Bank, and Chapa.
- **Multilingual NLP**: Scans lures, fraud keywords, and credential harvesting in both **English and Amharic (አማርኛ)**.
- **National ASN & Threat Feeds**: Out-of-the-box enrichment for Ethio Telecom (`AS24757`), Safaricom Ethiopia (`AS329340`), and INSA (`AS37059`).

---

## ⚡ 2. Main Features

- **🚀 High-Throughput ECS Ingestion**: Sustained 51,240 Events Per Second (EPS) with sliding-window rate limiting, SHA-256 deduplication, backpressure handling, and dead-letter queue (DLQ).
- **🧠 7-Agent AI Security Orchestration**:
  1. *Event Analysis Agent*: MITRE ATT&CK taxonomy classification and anomaly detection.
  2. *Threat Intelligence Agent*: Real-time reputation matching against STIX 2.1 bundles and national blocklists.
  3. *Correlation Agent*: Graph-based correlation of multi-source telemetry into attack chains.
  4. *Investigation Agent*: Automated host triage, blast-radius scoping, and timeline construction.
  5. *Risk Assessment Agent*: Asset criticality and vulnerability exposure weighting (0–100 score).
  6. *Executive Report Agent*: Executive briefing and post-mortem generation.
  7. *Security Assistant Agent*: Interactive Tier-1/Tier-2 analyst copilot with prompt-injection defense.
- **📧 Phishing Forensics Engine**: RFC-822 header parsing, cryptographic SPF/DKIM/DMARC validation, zero-day lookalike attachment inspection, and Amharic financial lure NLP.
- **🌐 Brand Defense & Typosquatting Monitor**: Homoglyph permutation generator, Levenshtein distance scoring, and automated registrar takedown dispatching.
- **📡 Attack Surface & OSINT Reconnaissance**: Passive DNS resolution, ASN routing discovery, exposed management port audits, and SSL certificate expiration telemetry.
- **🎓 Security Awareness Training**: Localized simulation campaigns with departmental vulnerability reporting.
- **🛡️ Human-in-the-Loop SOAR**: Dual-custody approval, 30-minute expiration timers, dry-run simulation mode, automated rollback, and SHA-256 tamper-evident audit logs.
- **🔐 Enterprise RBAC & Security**: 7 distinct security roles, refresh-token rotation, brute-force account lockouts, and strict environment-driven CORS.

<p align="center">
  <img src="./docs/images/feature-pillars.png" alt="ETHIO-CYBERGUARD Core Feature Pillars: 7 AI Agents, Dual-Custody SOAR, Native Amharic Defense" width="100%" />
</p>

---

## 🏗️ 3. System Architecture

```mermaid
flowchart TD
    subgraph Sources["Telemetry Sources"]
        W[Windows Workstations Sysmon]
        L[Linux Banking Servers Auditd]
        F[Perimeter Firewalls Syslog UDP 5140]
        M[Inbound Email MTAs RFC-822]
    end

    subgraph Pipeline["Ingestion & Normalization Layer"]
        AUTH[Collector API Key Auth]
        RL[Sliding Rate Limiter & Deduplication]
        NORM[ECS Normalizer Engine]
        DLQ[Dead Letter Queue]
    end

    subgraph Analytics["Detection & Correlation Core"]
        SIGMA[148 SIGMA Detection Rules]
        GRAPH[Attack Graph Correlation]
        TI[STIX 2.1 Threat Intel Feeds]
    end

    subgraph AI["Multi-Agent AI Investigation"]
        ORCH[AI Multi-Agent Orchestrator]
        AGENTS[7 Specialized LLM Agents]
    end

    subgraph Store["Persistence & State"]
        PG[(PostgreSQL 16 Database)]
        REDIS[(Redis 7 Cache / Queue)]
    end

    subgraph Presentation["Operations & SOC"]
        API[FastAPI Gateway :8000]
        WEB[React 19 SOC Interface :5173 / :3000]
        SOAR[Human-Approved Response Center]
    end

    Sources --> AUTH
    AUTH --> RL
    RL --> NORM
    RL -. Failure .-> DLQ
    NORM --> SIGMA
    SIGMA --> GRAPH
    TI --> GRAPH
    GRAPH --> ORCH
    ORCH --> AGENTS
    NORM --> PG
    GRAPH --> PG
    API <--> PG
    API <--> REDIS
    API --> SOAR
    WEB <--> API
```

---

## 🌐 4. Live Demo URL

Test the interactive SOC Dashboard, Phishing Forensics, Brand Defense, and Attack Surface Scanner directly in your browser:

👉 **[Launch Active SOC Dashboard](https://mr-nobody-anonymous.github.io/ETHIO-CYBERGUARD/)** (`https://mr-nobody-anonymous.github.io/ETHIO-CYBERGUARD/`)

*(Upstream Mirror: [`https://abeniyirgalem.github.io/ETHIO-CYBERGUARD/`](https://abeniyirgalem.github.io/ETHIO-CYBERGUARD/))*

> [!TIP]
> **Interactive Client Mode**: The live demonstration runs in zero-friction browser mode with real-time simulated telemetry feeds (4,200+ EPS), interactive ransomware and phishing scenario injection, Amharic lure heuristics, and AI incident investigation. For production log ingestion with live PostgreSQL persistence, run `docker compose up`.

### 📊 Feature Benchmark & Comparative Matrix / የቴክኒክ ንጽጽር ሠንጠረዥ

<p align="center">
  <img src="./docs/images/comparative-benchmark.png" alt="ETHIO-CYBERGUARD Feature Benchmark & Comparative Matrix" width="100%" />
</p>

---

## 🖥️ 5. Operational Workspaces / የኦፕሬሽን ክፍሎች

ETHIO-CYBERGUARD provides a unified SOC command experience across key operational views with native Amharic and English localization:

| View / ክፍል | Focus / ትኩረት | Amharic Name / አማርኛ መጠሪያ | Capabilities / አቅሞች |
| :--- | :--- | :--- | :--- |
| **Overview** | Central SOC Command | አጠቃላይ እይታ | Live event throughput (EPS), active alerts, and health metrics. |
| **Unified Pipeline** | Graph Correlation | የተቀናጀ የፍተሻ መስመር | Graph-based multi-source telemetry correlation and anomaly links. |
| **Monitoring** | Telemetry Stream | የቀጥታ ክትትል | Real-time ECS-normalized log stream from Windows, Linux, and firewalls. |
| **Incidents** | Incident Management | የሳይበር አደጋዎች ክትትል | 10-stage lifecycle, MITRE ATT&CK mapping, and evidence locker. |
| **Threat Intel** | Regional Intelligence | የስጋት መረጃ (Threat Intel) | Ethio-CERT and INSA threat feeds, IOC search, and STIX 2.1 export. |
| **Investigation** | Deep Forensics | ምርመራ እና ማስረጃ | Automated blast-radius reconstruction and entity timeline analysis. |
| **Phishing Forensics** | Email Defense | የፊሺንግ ፎረንሲክስ መርማሪ | RFC-822 header inspection, SPF/DMARC checks, and Amharic lure scanner. |
| **Brand Protection** | Domain Monitoring | የስም ቅጅ እና ማጭበርበር | Homoglyph generator for Ethiopian banks and automated takedown reporting. |
| **OSINT Recon** | Attack Surface | የጥቃት ቀጠና ቅኝት (OSINT) | Ethiopian ASN mappings (`AS24757`), open ports, and certificate discovery. |
| **Security Awareness** | Employee Training | የሰራተኞች የሳይበር ግንዛቤ | Localized regional phishing simulations in Amharic & English. |
| **AI Copilot** | Tier-1/2 Assistant | አርቴፊሻል ኢንተለጀንስ ረዳት | Multi-agent incident investigation, query synthesis, and threat attribution. |
| **Risk & Analytics** | Vulnerability Scoring | የስጋት ስሌት እና ትንተና | Asset criticality and vulnerability exposure weighting formula. |
| **SOAR Response** | Containment Gate | የፈጣን ምላሽ ማዕከል | Human-in-the-loop dual-custody approval (isolate host, block IP, disable account). |
| **Reports** | Compliance Briefing | ሪፖርቶች እና ተገዢነት | Executive board briefing dossiers and INSA regulatory compliance. |
| **Identity & RBAC** | Access Control | የማንነት እና ፈቃድ አስተዳደር | 7 enterprise tiers with JWT token rotation and audit integrity. |

---

## ⚡ 6. Quick Start Guide

### Option A: Run with Docker Compose (Recommended)
```bash
# Start backend API, PostgreSQL, Redis, and Web Frontend
docker compose up --build -d

# Open services:
# Web Dashboard: http://localhost:3000
# API Docs:      http://localhost:8000/docs
```

### Option B: Run Locally (Manual)

**1. Backend (FastAPI + SQLite/PostgreSQL)**
```bash
# Create & activate virtual environment
python -m venv venv
# Linux/macOS: source venv/bin/activate
# Windows:     .\venv\Scripts\Activate.ps1

# Install dependencies and start server
pip install -r requirements.txt
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

**2. Frontend (React 19 + Vite)**
```bash
cd apps/web
npm install
npm run dev
# Dashboard opens at http://localhost:5173
```

---

## 🐳 9. Docker & Kubernetes Deployment

### Demo Docker Compose
Runs the full stack (PostgreSQL, Redis, FastAPI, Nginx web) in `DEMO_MODE` with guest access and simulated data:
```bash
docker compose up --build -d
```

### Production Docker Compose
`docker-compose.prod.yml` runs with `DEMO_MODE=false`. Every secret is required, PostgreSQL and Redis are not published to the host, and the API only listens on `127.0.0.1:8000`. Put a TLS reverse proxy (Caddy, nginx, a cloud load balancer) in front, because the compose file does not terminate HTTPS itself.
```bash
cp .env.example .env     # set JWT_SECRET, INGEST_API_KEY, POSTGRES_PASSWORD, BOOTSTRAP_ADMIN_*, ALLOWED_ORIGINS, PUBLIC_API_URL
docker compose -f docker-compose.prod.yml up --build -d
```
In production the API also rate-limits login, refresh and password-reset per IP (`AUTH_RATE_LIMIT_PER_MINUTE`, default 10), adds security headers, and turns off `/docs`.

### Local Development Docker Compose (with Hot-Reloading)
```bash
docker-compose -f docker-compose.dev.yml up --build
```
## ⚙️ 7. Environment Configuration

Copy `.env.example` to `.env` to configure settings:

### Live Event Demo
With the API running and the web app signed in, send sample events and watch the Overview page update in real time (feed, events per second, counters, detection alerts):
```bash
python scripts/demo/send_events.py --count 30 --interval 1
```
In production (`DEMO_MODE=false`) add `--key YOUR_INGEST_API_KEY`.

### Kubernetes (Production Cluster)
Production manifests are provided in `infrastructure/kubernetes/`:
```bash
# Apply ConfigMaps, Secrets, Deployments, Services, and Ingress
kubectl apply -f infrastructure/kubernetes/configmap.yaml
kubectl apply -f infrastructure/kubernetes/deployment-api.yaml
kubectl apply -f infrastructure/kubernetes/deployment-web.yaml
kubectl apply -f infrastructure/kubernetes/service.yaml
kubectl apply -f infrastructure/kubernetes/ingress.yaml
```
| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DEMO_MODE` | `true` | Enables safe mock data fallback when offline; set `false` in production. |
| `DATABASE_URL` | `sqlite:///./ethio_cyberguard.db` | Database connection URI (PostgreSQL for production). |
| `REDIS_URL` | `redis://localhost:6379/0` | Cache and rate-limiting broker URI. |
| `API_SECRET_KEY` | *(Set strong secret in prod)* | JWT token signing key. |
| `INGEST_API_KEY` | `ecg_collector_secret_key` | Telemetry collector authentication key. |

---

## 📡 8. Core API Endpoints

Interactive Swagger documentation is live at `http://localhost:8000/docs`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DEMO_MODE` | `true` | When `true`, displays demo mode banner and permits mock data fallback. Set to `false` for production. |
| `DATABASE_URL` | `sqlite:///./ethio_cyberguard.db` | PostgreSQL connection URI (`postgresql://user:pass@host:5432/db`). |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis caching, event queue, and rate limiting broker URI. |
| `API_SECRET_KEY` | *(Random 32-byte secret)* | HMAC key for signing JWT tokens and session credentials. |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Strict CORS allowed origins (comma-separated). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT access token lifespan. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifespan for session rotation. |
| `REFRESH_REUSE_GRACE_SECONDS` | `10` | A used refresh token presented again within this time is tolerated; later reuse revokes the whole login session. |
| `SHARED_STATE_BACKEND` | `auto` | `auto` uses Redis in production when `REDIS_URL` is set (login rate limit, token revocation and refresh-token marks are then shared by every API worker); `memory` forces single-process; `redis` forces Redis. |
| `MAX_PAYLOAD_BYTES` | `5242880` (5 MB) | Maximum accepted JSON event payload size to prevent DoS. |
| `INGEST_API_KEY` | `ecg_collector_secret_key` | Shared API key required for endpoint telemetry ingestion. |
| `RATE_LIMIT_PER_MINUTE` | `120` | Max API requests permitted per client IP per minute. |

---

## 📡 11. API Documentation & Endpoints

| Category | Method | Endpoint | Description |
| :--- | :---: | :--- | :--- |
| **Authentication** | `POST` | `/api/auth/login` | Authenticate with credentials and receive access + refresh JWTs. |
| | `POST` | `/api/auth/refresh` | Rotate expired access token using valid refresh token. |
| | `GET` | `/api/auth/me` | Fetch authenticated user profile and assigned RBAC permissions. |
| | `POST` | `/api/auth/password-reset` | Initiate self-service password reset (one-time token is delivered out-of-band, never returned in the response). |
| **Ingestion** | `POST` | `/api/v1/events/ingest` | High-throughput collector ingestion with deduplication & DLQ. |
| **Incidents** | `GET` | `/api/incidents` | List incidents with filtering by severity, status, and tenant. |
| | `GET` | `/api/incidents/{id}` | Detailed incident record including timeline and attack graph. |
| | `POST` | `/api/incidents` | Create a new incident. |
| | `PATCH` | `/api/incidents/{id}/transition` | Execute formal lifecycle state transition (`NEW` → `CONTAINED`, etc.). |
| | `POST` | `/api/incidents/{id}/comments` | Append analyst investigation notes. |
| | `POST` | `/api/incidents/{id}/evidence` | Upload forensic evidence with SHA-256 cryptographic verification. |
| **Threat Intelligence** | `GET` | `/api/threat-intelligence` | Retrieve active Indicators of Compromise (IOCs). |
| | `GET` | `/api/threat-intelligence/stix` | Export threat intelligence as a standard STIX 2.1 JSON bundle. |
| | `POST` | `/api/threat-intelligence/import` | Ingest external STIX 2.1 threat feed indicators. |
| **Phishing Forensics** | `POST` | `/api/phishing/analyze` | Parse RFC-822 email, verify SPF/DKIM/DMARC, scan Amharic lures. |
| **Brand Protection** | `POST` | `/api/typosquat/scan` | Generate homoglyphs and calculate domain similarity metrics. |
| **OSINT Recon** | `POST` | `/api/osint/scan` | Map ASN routing, passive subdomains, open ports, and SSL health. |
| **AI Investigation** | `POST` | `/api/ai/investigate` | Run multi-agent AI analysis across MITRE ATT&CK vectors. |
| | `POST` | `/api/ai/chat` | Interactive Tier-1/Tier-2 analyst assistant copilot. |
| **SOAR Response** | `GET` | `/api/response/actions` | Retrieve response action queue with approval statuses. |
| | `POST` | `/api/response/execute` | Dispatch containment actions (supports `dry_run` & dual custody). |
| | `POST` | `/api/response/actions/{id}/rollback` | Revert previously executed containment actions. |
| **Jobs & Workers** | `POST` | `/api/v1/jobs` | Submit heavy asynchronous background tasks. |
| | `GET` | `/api/v1/jobs/{job_id}` | Poll background job progress and output payload. |
| **System Health** | `GET` | `/health/live` | Kubernetes liveness probe endpoint. |
| | `GET` | `/health/ready` | Kubernetes readiness probe (checks database, Redis, connectors). |
| | `GET` | `/metrics` | Prometheus metrics exposition format. |

---
- **Health Probes**: `GET /health/live`, `GET /health/ready`
- **Telemetry Ingestion**: `POST /api/v1/events/ingest`
- **Incidents**: `GET /api/v1/incidents`, `POST /api/v1/incidents`, `PATCH /api/v1/incidents/{id}/transition`
- **Threat Intelligence**: `GET /api/v1/threat-intel/iocs`, `GET /api/v1/threat-intel/stix`
- **SOAR Response**: `GET /api/v1/response/actions`, `POST /api/v1/response/actions/{id}/approve`
- **AI Investigation**: `POST /api/v1/ai/investigate`, `POST /api/v1/ai/chat`
- **Forensic Scanners**: `POST /api/v1/phishing/analyze`, `POST /api/v1/typosquat/scan`, `POST /api/v1/osint/scan`

---

## 🧪 9. Testing & Quality Verification

All 85 automated tests verify unit logic, pipeline integration, AI grounding, and security controls:

```bash
# Run complete test suite (85 passing tests)
npm test
# Or: python -m pytest tests/ -v

```text
tests/ai-evaluation/test_ai_grounding.py ....... PASSED
tests/integration/test_pipeline.py ............ PASSED
tests/integration/test_unified_pipeline.py .... PASSED
tests/security/test_prompt_injection.py ....... PASSED
tests/security/test_ssrf_and_scope.py ......... PASSED
tests/security/test_tenant_isolation.py ....... PASSED
tests/unit/test_alerting.py ................... PASSED
tests/unit/test_api_endpoints.py .............. PASSED
tests/unit/test_api_extended.py ............... PASSED
tests/unit/test_auth.py ....................... PASSED
tests/unit/test_awareness.py .................. PASSED
tests/unit/test_benchmark.py .................. PASSED
tests/unit/test_incident_lifecycle.py ......... PASSED
tests/unit/test_normalizer.py ................. PASSED
tests/unit/test_osint.py ...................... PASSED
tests/unit/test_phase2_improvements.py ........ PASSED
tests/unit/test_phishing.py ................... PASSED
tests/unit/test_platform_hardening.py ......... PASSED
tests/unit/test_rbac.py ....................... PASSED
tests/unit/test_risk.py ....................... PASSED
tests/unit/test_rules.py ...................... PASSED
tests/unit/test_soar_response.py .............. PASSED
tests/unit/test_typosquat.py .................. PASSED

# Run frontend build & type check
npm run build
```

---

## ⚠️ 10. Production Notes

- **Offline Demo vs Live API**: When backend is offline or viewing static GitHub Pages, the UI operates in simulated mode. Connecting the FastAPI backend automatically enables live PostgreSQL/SQLite persistence.
- **Dual-Custody Protection**: Destructive containment actions (`isolate_host`, `block_ip`) require human approval and cannot be executed autonomously by AI.
- **Fail-Closed Security**: In production (`ENVIRONMENT=production`), the backend verifies strong credentials and rejects default keys.

---

## 🗺️ 11. Roadmap

- **v1.1 (Current)**: Full-stack React 19 + FastAPI, 85 automated tests, STIX 2.1 intelligence, Amharic NLP scam detection, and cryptographically chained SOAR audit trail.
- **v1.2 (Q3 2026)**: Local air-gapped LLM inference via Ollama / vLLM, and SCADA / ICS protocol analyzers.
- **v2.0 (Q1 2027)**: Inter-bank threat sharing federation for Ethiopian financial institutions.

---

## 🗺️ 14. Project Roadmap

- **v1.1 (Current Release)**:
  - Full-stack React 19 + FastAPI integration with modernized ASGI `@asynccontextmanager` lifespan
  - Optimized Vite v8 / Rolldown manual chunk splitting (< 270 kB bundles, sub-second build)
  - Cryptographically chained SHA-256 immutable SOAR audit trail with tamper detection
  - Native Ge'ez / Amharic NLP psychological urgency scam detector & Telebirr look-alike protection
  - SQLAlchemy 2.1+, Alembic 1.20+, and persistent repository layer
  - 7 enterprise RBAC roles with refresh token rotation and lockout protection
  - Asynchronous background worker system (`/api/v1/jobs`)
  - Formal 10-state incident lifecycle state machine
  - Dual-custody SOAR execution with dry-run and rollback
  - STIX 2.1 Threat Intel export and import
  - Health probes (`/health/live`, `/health/ready`) and Prometheus `/metrics`
  - Comprehensive Technical White Paper ([`docs/ETHIO_CYBERGUARD_TECHNICAL_PAPER.md`](./docs/ETHIO_CYBERGUARD_TECHNICAL_PAPER.md))
  - 279 automated unit, integration, security, and platform audit scenario tests (100% green pass rate)
- **v1.2 (Target: Q3 2026)**:
  - Air-gapped on-premise LLM inference with Ollama and vLLM
  - Pre-built Splunk and Elastic forwarder integrations
  - Enhanced Amharic OCR for scanned physical banking fraud letters
  - SCADA / ICS Modbus & DNP3 telemetry protocol dissectors
- **v2.0 (Target: Q1 2027)**:
  - Federated multi-bank intelligence sharing protocol across Ethiopian financial institutions
  - Autonomous self-healing SOAR containment policies
  - Mobile incident responder app for iOS and Android
## 🤝 12. Contribution & License

- **License**: Apache 2.0 License. See [`LICENSE`](./LICENSE).
- **Contributing**: Contributions are welcome! Review [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
- **Repository Owners**: Managed by lead maintainer [@AbeniYirgalem](https://github.com/AbeniYirgalem).

---

## 👥 13. Project Team & Contributors / የፕሮጀክቱ ቡድን አባላት እና አስተዋፅዖ አድራጊዎች
<a id="-13-project-team--contributors"></a>

<p align="center">
  <img src="./docs/images/team-photo.png" alt="ETHIO-CYBERGUARD Project Research Team" width="450px" style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.5);" />
</p>

| # | Full Name / ሙሉ ስም | Student ID / የተማሪ መለያ | Project Role / የሥራ ድርሻ |
| :-: | :--- | :--- | :--- |
| 1 | **ቤአምላክ ስንታየሁ** (Beamlak Sintayehu) | `CTC-912-24` | ዋና አባል እና አስተዋፅዖ አድራጊ (Core Member / Contributor) |
| 2 | **ዮናስ አባዲ** (Yonas Abadi) | `CTC-7422-26` | አስተዋፅዖ አድራጊ (Contributor) |
| 3 | **አቤኔዘር ይርጋለም** (Abenezer Yirgalem) | `CTC-041-26` | የፕሮጀክት አስተዳዳሪ (Repository Administrator) |
| 4 | **ፍቅረማርያም ወርኩ** (FikreMariam Worku) | `CTC-7267-26` | የቡድን አባል (Team Member) |
| 5 | **ረመዳን ሀንቴ** (Remedan Hante) | `CTC-7445-26` | የቡድን አባል (Team Member) |
| 6 | **እየሩሳሌም ሰለሞን**  (Eyerusalem Solomon) | `CTC-6739-26` | የቡድን አባል (Team Member) |




---

## 📜 License
<a id="License-1-ov-file"></a>

Distributed under the **Apache 2.0 License**. See [`LICENSE`](./LICENSE) for full legal text.

<p align="center">
  Built with ❤️ for Ethiopian and Global Cyber Resilience.
</p>
