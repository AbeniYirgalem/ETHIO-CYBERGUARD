<div align="center">

# 🛡️ ETHIO-CYBERGUARD

```text
                        ______________  __________ 
                       / ____/_  __/ / / /  _/ __ \
                      / __/   / / / /_/ // // / / /
                     / /___  / / / __  // // /_/ / 
                    /_____/ /_/ /_/ /_/___/\____/  

        ________  ______  __________  ________  _____    ____  ____ 
       / ____/\ \/ / __ )/ ____/ __ \/ ____/ / / /   |  / __ \/ __ \
      / /      \  / __  / __/ / /_/ / / __/ / / / /| | / /_/ / / / /
     / /___    / / /_/ / /___/ _, _/ /_/ / /_/ / ___ |/ _, _/ /_/ / 
     \____/   /_/_____/_____/_/ |_|\____/\____/_/  |_/_/ |_/_____/  
```

<p align="center">
  <strong>Next-Generation AI-Powered SIEM, Threat Intelligence & Human Defense Platform</strong>
  <br />
  <em>Tailored for Corporate, Banking, Higher Education, and Critical Infrastructure Defense with Native Ethiopian Threat Context.</em>
</p>

<p align="center">
  <a href="https://AbeniYirgalem.github.io/ETHIO-CYBERGUARD/"><img src="https://img.shields.io/badge/Live_Demo-GitHub_Pages-00D9FF?style=for-the-badge&logo=github&logoColor=black" alt="Live Demo" /></a>
  <img src="https://img.shields.io/badge/Multi--Agent_AI-7_Agents-FF1744?style=for-the-badge&logo=openai" alt="Multi-Agent AI" />
  <img src="https://img.shields.io/badge/Throughput-51k+_EPS-00D9FF?style=for-the-badge&logo=speedtest" alt="51k+ EPS" />
  <img src="https://img.shields.io/badge/Frontend-React_19_+_Tailwind-22C55E?style=for-the-badge&logo=react" alt="React 19" />
  <img src="https://img.shields.io/badge/Backend-FastAPI_Python_3.10+-F59E0B?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Tests-54%2F54_Passing-22C55E?style=for-the-badge&logo=pytest" alt="Pytest" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue?style=for-the-badge" alt="License" /></a>
</p>

</div>

---

## 📋 Table of Contents

1. [Project Overview](#-1-project-overview)
2. [Main Features](#-2-main-features)
3. [System Architecture](#-3-system-architecture)
4. [Live Demo URL](#-4-live-demo-url)
5. [Screenshots & UI Views](#-5-screenshots--ui-views)
6. [Installation & Prerequisites](#-6-installation--prerequisites)
7. [Backend Setup (FastAPI + SQLAlchemy)](#-7-backend-setup)
8. [Frontend Setup (React 19 + Vite)](#-8-frontend-setup)
9. [Docker & Kubernetes Deployment](#-9-docker--kubernetes-deployment)
10. [Environment Variables Reference](#-10-environment-variables-reference)
11. [API Documentation & Endpoints](#-11-api-documentation--endpoints)
12. [Testing & Verification](#-12-testing--verification)
13. [Production Limitations](#-13-production-limitations)
14. [Project Roadmap](#-14-project-roadmap)
15. [Contribution & Governance](#-15-contribution--governance)

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

👉 **[https://AbeniYirgalem.github.io/ETHIO-CYBERGUARD/](https://AbeniYirgalem.github.io/ETHIO-CYBERGUARD/)**

> [!NOTE]
> **Demo Sandbox Mode**: The GitHub Pages build runs in client-side Demo Mode with high-fidelity simulated telemetry feeds (4,200+ EPS), interactive scenario injection, and zero-latency client forensics. For production telemetry with live PostgreSQL persistence and syslog daemon, run the full container stack.

---

## 🖥️ 5. Screenshots & UI Views

The platform includes 10 dedicated operational workspaces:

| View Component | Purpose | Key Capabilities |
| :--- | :--- | :--- |
| **`OverviewView.tsx`** | Central SOC Command | Live event throughput counter, MTTD/MTTR KPIs, active threat alerts, and system health status. |
| **`IncidentsView.tsx`** | Incident Management | Formal lifecycle state machine (`NEW` to `CLOSED`), interactive MITRE attack graph, evidence locker, and audit trail. |
| **`PhishingAnalyzerView.tsx`** | Email Forensics | Raw RFC-822 header parser, SPF/DKIM/DMARC validator, URL extractor, and Amharic lure classifier. |
| **`TyposquatView.tsx`** | Brand Protection | openSquat-based homoglyph generator for Ethiopian banks, visual similarity scoring, and 1-click registrar takedown. |
| **`OSINTReconView.tsx`** | External Attack Surface | Passive DNS recon, ASN mapper (`AS24757`, `AS329340`), exposed ports (3389, 445, 8080), and SSL certificate tracking. |
| **`AwarenessSimulatorView.tsx`** | Human Defense Training | Localized Ethiopian phishing simulations, departmental vulnerability matrix, and micro-learning modules. |
| **`AssistantView.tsx`** | Multi-Agent AI Copilot | Direct interface with the 7 security agents for contextual investigation, query parsing, and report drafting. |
| **`ResponseView.tsx`** | SOAR Response Center | Human-in-the-loop action approval (host isolation, IP egress drop, account disablement) with dry-run and rollback. |
| **`ScenarioSimulator.tsx`** | Red-Team Drills | Interactive drilldown injector to simulate ransomware outbreaks, data exfiltration, or BEC attacks in real time. |
| **`PublicLandingPage.tsx`** | Public Portal View | Public-facing security status overview, incident reporting gateway, and awareness knowledge base. |

---

## ⚡ 6. Installation & Prerequisites

### Minimum Hardware Requirements
- **Development**: 4 CPU cores, 8 GB RAM, 20 GB free disk space.
- **Production SOC**: 16+ CPU cores, 32 GB RAM, NVMe SSD storage (see [Performance Benchmark Methodology](docs/benchmark.md)).

### Software Prerequisites
- **Python**: 3.10 or higher
- **Node.js**: 20.x or higher & `npm` 10.x
- **Docker & Docker Compose**: v2.20+ (for containerized deployments)
- **PostgreSQL**: 16.x (if running outside Docker)

---

## 🔌 7. Backend Setup

```bash
# 1. Clone the repository
git clone https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD.git
cd ETHIO-CYBERGUARD

# 2. Create and activate a Python virtual environment
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# 3. Install backend dependencies
pip install -r apps/api/requirements.txt

# 4. Configure environment variables
cp .env.example .env

# 5. Run database migrations (or SQLite fallback will initialize automatically)
alembic upgrade head

# 6. Start the FastAPI development server
uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.  
Interactive Swagger OpenAPI documentation is live at `http://localhost:8000/docs`.

---

## 💻 8. Frontend Setup

```bash
# 1. Navigate to the web application directory
cd apps/web

# 2. Install Node.js dependencies
npm install

# 3. Start Vite development server
npm run dev

# 4. Build production static bundle
npm run build
```

The web dashboard will be accessible at `http://localhost:5173`.

---

## 🐳 9. Docker & Kubernetes Deployment

### Production Docker Compose
Run the complete production multi-container stack (PostgreSQL, Redis, FastAPI, Nginx Web Frontend):
```bash
docker-compose up --build -d
```

### Local Development Docker Compose (with Hot-Reloading)
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Automated Testing Container
```bash
docker-compose -f docker-compose.test.yml run --rm test-runner
```

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

---

## ⚙️ 10. Environment Variables Reference

Configure these in `.env` or your Kubernetes ConfigMaps / Secrets:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DEMO_MODE` | `true` | When `true`, displays demo mode banner and permits mock data fallback. Set to `false` for production. |
| `DATABASE_URL` | `sqlite:///./ethio_cyberguard.db` | PostgreSQL connection URI (`postgresql://user:pass@host:5432/db`). |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis caching, event queue, and rate limiting broker URI. |
| `API_SECRET_KEY` | *(Random 32-byte secret)* | HMAC key for signing JWT tokens and session credentials. |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Strict CORS allowed origins (comma-separated). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT access token lifespan. |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifespan for session rotation. |
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
| | `POST` | `/api/auth/password-reset` | Initiate secure self-service password reset. |
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

## 🧪 12. Testing & Verification

The test suite covers unit logic, pipeline integration, AI grounding, security defenses, and authentication:

```bash
# Run the complete Pytest suite
python -m pytest tests/ -v
```

```text
tests/ai-evaluation/test_ai_grounding.py ....... PASSED
tests/integration/test_pipeline.py ............ PASSED
tests/integration/test_unified_pipeline.py .... PASSED
tests/security/test_prompt_injection.py ....... PASSED
tests/unit/test_alerting.py ................... PASSED
tests/unit/test_api_endpoints.py .............. PASSED
tests/unit/test_auth.py ....................... PASSED
tests/unit/test_awareness.py .................. PASSED
tests/unit/test_benchmark.py .................. PASSED
tests/unit/test_incident_lifecycle.py ......... PASSED
tests/unit/test_normalizer.py ................. PASSED
tests/unit/test_osint.py ...................... PASSED
tests/unit/test_phase2_improvements.py ........ PASSED
tests/unit/test_phishing.py ................... PASSED
tests/unit/test_rbac.py ....................... PASSED
tests/unit/test_risk.py ....................... PASSED
tests/unit/test_rules.py ...................... PASSED
tests/unit/test_typosquat.py .................. PASSED

============================= 54 passed in 1.12s =============================
```

To test the frontend build and TypeScript compliance:
```bash
npm --prefix apps/web run build
```

---

## ⚠️ 13. Production Limitations

While ETHIO-CYBERGUARD provides production-grade components, operators deploying in critical enterprise environments should consider:
- **Sandbox Mode vs Real Ingestion**: In the standalone client demo on GitHub Pages, events are generated dynamically in the browser. In production, configure collectors (`collectors/endpoint/`) to stream real events to `/api/v1/events/ingest`.
- **Database Scaling**: The default fallback uses SQLite for single-node prototypes. For high-volume production deployments exceeding 10,000 EPS, deploy PostgreSQL 16+ on dedicated NVMe storage with partitioned event tables.
- **External Connector Credentials**: EDR and Firewall integrations (`services/connectors/`) are designed with circuit breakers and fallback simulators. Operators must supply valid vendor API keys (Fortinet, Palo Alto, CrowdStrike, SentinelOne) in production environment secrets.
- **AI Model Latency**: Cloud LLM inference latency depends on external API response times. For air-gapped critical infrastructure, host a quantized local LLM (e.g., Llama 3 8B or Mistral 7B) on premise.

---

## 🗺️ 14. Project Roadmap

- **v1.1 (Current Release)**:
  - Full-stack React 19 + FastAPI integration
  - SQLAlchemy models, Alembic migrations, and persistent repository layer
  - 7 enterprise RBAC roles with refresh token rotation and lockout protection
  - Asynchronous background worker system (`/api/v1/jobs`)
  - Formal 10-state incident lifecycle state machine
  - Dual-custody SOAR execution with dry-run and rollback
  - STIX 2.1 Threat Intel export and import
  - Health probes (`/health/live`, `/health/ready`) and Prometheus `/metrics`
- **v1.2 (Target: Q3 2026)**:
  - Air-gapped on-premise LLM inference with Ollama and vLLM
  - Pre-built Splunk and Elastic forwarder integrations
  - Enhanced Amharic OCR for scanned physical banking fraud letters
  - SCADA / ICS Modbus & DNP3 telemetry protocol dissectors
- **v2.0 (Target: Q1 2027)**:
  - Federated multi-bank intelligence sharing protocol across Ethiopian financial institutions
  - Autonomous self-healing SOAR containment policies
  - Mobile incident responder app for iOS and Android

---

## 🤝 15. Contribution & Governance
<a id="contributing-ov-file"></a>
<a id="coc-ov-file"></a>
<a id="security-ov-file"></a>

Contributions from security analysts, developers, and researchers are warmly welcomed!

- **Code of Conduct**: Please adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).
- **Contributing Guide**: Review [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming conventions, PR guidelines, and code style.
- **Repository Owners**: Managed by lead maintainer [@AbeniYirgalem](https://github.com/AbeniYirgalem) (see [.github/CODEOWNERS](.github/CODEOWNERS)).
- **Security Disclosures**: Please report sensitive vulnerabilities directly to the maintainers as detailed in [SECURITY.md](SECURITY.md).
- **Citation**: If you reference this work in research or technical whitepapers, see [`CITATION.cff`](./CITATION.cff).

---

## 📜 License
<a id="License-1-ov-file"></a>

Distributed under the **Apache 2.0 License**. See [`LICENSE`](./LICENSE) for full legal text.

<p align="center">
  Built with ❤️ for Ethiopian and Global Cyber Resilience.
</p>
