<div align="center">

# 🛡️ ETHIO-CYBERGUARD
### Autonomous AI-Powered Security Operations Center & Critical Infrastructure Threat Intelligence

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
  <em>Defending Ethiopian Banking, Telecommunications, Government & Critical Infrastructure Networks.</em>
</p>

<p align="center">
  <a href="https://abeniyirgalem.github.io/ETHIO-CYBERGUARD/"><img src="https://img.shields.io/badge/⚡_Live_SOC_Demo-Active_Online-00D9FF?style=for-the-badge&logo=github&logoColor=black" alt="Live Demo" /></a>
  <img src="https://img.shields.io/badge/Defense_Status-DEFCON_2-FF1744?style=for-the-badge" alt="DEFCON 2" />
  <img src="https://img.shields.io/badge/AI_Engine-7_Specialized_Agents-9333EA?style=for-the-badge&logo=openai" alt="7 AI Agents" />
  <img src="https://img.shields.io/badge/Throughput-51,000+_EPS-00D9FF?style=for-the-badge&logo=speedtest" alt="51k+ EPS" />
  <img src="https://img.shields.io/badge/Automated_Tests-279%2F279_Passing-22C55E?style=for-the-badge&logo=pytest" alt="279/279 Passing" />
  <img src="https://img.shields.io/badge/Frontend-React_19_+_Tailwind-22C55E?style=for-the-badge&logo=react" alt="React 19" />
  <img src="https://img.shields.io/badge/Backend-FastAPI_Python_3.10+-F59E0B?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache_2.0-blue?style=for-the-badge" alt="License" /></a>
</p>

<p align="center">
  <a href="https://abeniyirgalem.github.io/ETHIO-CYBERGUARD/">
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
- **Multilingual NLP**: Scans lures, fraud keywords, and credential harvesting in both **English and Amharic languages**.
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

👉 **[Launch Active SOC Dashboard](https://abeniyirgalem.github.io/ETHIO-CYBERGUARD/)** (`https://abeniyirgalem.github.io/ETHIO-CYBERGUARD/`)

*(Deployment Mirror: [`https://mr-nobody-anonymous.github.io/ETHIO-CYBERGUARD/`](https://mr-nobody-anonymous.github.io/ETHIO-CYBERGUARD/))*

> [!TIP]
> **Interactive Client Mode**: The live demonstration runs in zero-friction browser mode with real-time simulated telemetry feeds (4,200+ EPS), interactive ransomware and phishing scenario injection, localized lure heuristics, and AI incident investigation. For production log ingestion with live PostgreSQL persistence, run `docker compose up`.

### 📊 Feature Benchmark & Comparative Matrix

<p align="center">
  <img src="./docs/images/comparative-benchmark.png" alt="ETHIO-CYBERGUARD Feature Benchmark & Comparative Matrix" width="100%" />
</p>

---

## 🖥️ 5. Operational Workspaces

ETHIO-CYBERGUARD provides a unified SOC command experience across key operational workspaces:

| Workspace | Operational Focus | Primary Function | Core Capabilities |
| :--- | :--- | :--- | :--- |
| **Overview** | Central SOC Command | Executive Dashboard | Live event throughput (EPS), active alerts, and system health metrics. |
| **Unified Pipeline** | Graph Correlation | Ingestion & Graph | Graph-based multi-source telemetry correlation and anomaly links. |
| **Monitoring** | Telemetry Stream | Real-Time Telemetry | Real-time ECS-normalized log stream from Windows, Linux, and firewalls. |
| **Incidents** | Incident Management | Triage & Lifecycle | 10-stage lifecycle, MITRE ATT&CK mapping, and evidence locker. |
| **Threat Intel** | Regional Intelligence | Feeds & IOCs | Ethio-CERT and INSA threat feeds, IOC search, and STIX 2.1 export. |
| **Investigation** | Deep Forensics | Root Cause Triage | Automated blast-radius reconstruction and entity timeline analysis. |
| **Phishing Forensics** | Email Defense | Inbound MTA Parser | RFC-822 header inspection, SPF/DMARC checks, and localized lure scanner. |
| **Brand Protection** | Domain Monitoring | Typosquat Radar | Homoglyph generator for Ethiopian banks and automated takedown reporting. |
| **OSINT Recon** | Attack Surface | Perimeter Radar | Ethiopian ASN mappings (`AS24757`), open ports, and certificate discovery. |
| **Security Awareness** | Employee Training | Simulation Suite | Localized regional phishing simulations and security awareness reporting. |
| **AI Copilot** | Tier-1/2 Assistant | Multi-Agent Copilot | Multi-agent incident investigation, query synthesis, and threat attribution. |
| **Risk & Analytics** | Vulnerability Scoring | Risk Engine | Asset criticality and vulnerability exposure weighting formula. |
| **SOAR Response** | Containment Gate | Mitigation Center | Human-in-the-loop dual-custody approval (isolate host, block IP, disable account). |
| **Reports** | Compliance Briefing | Board Reports | Executive board briefing dossiers and INSA regulatory compliance. |
| **Identity & RBAC** | Access Control | Security Admin | 7 enterprise tiers with JWT token rotation and audit integrity. |

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

## ⚙️ 7. Environment Configuration

Copy `.env.example` to `.env` to configure settings:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DEMO_MODE` | `true` | Enables safe mock data fallback when offline; set `false` for strict production. |
| `DATABASE_URL` | `sqlite:///./ethio_cyberguard.db` | Database connection URI (`postgresql://user:pass@host:5432/db` in production). |
| `REDIS_URL` | `redis://localhost:6379/0` | Cache, event queue, and rate limiting broker URI. |
| `API_SECRET_KEY` | *(Set 32-byte secret)* | HMAC key for signing JWT tokens and session credentials. |
| `INGEST_API_KEY` | `ecg_collector_secret_key` | Collector authentication key for log telemetry ingestion. |
| `ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Strict CORS allowed origins. |

---

## 📡 8. Core API Endpoints

Interactive Swagger documentation is live at `http://localhost:8000/docs`:

| Category | Method | Endpoint | Description |
| :--- | :---: | :--- | :--- |
| **Authentication** | `POST` | `/api/auth/login` | Authenticate with credentials and receive access + refresh JWTs. |
| | `GET` | `/api/auth/me` | Fetch authenticated user profile and assigned RBAC permissions. |
| **Ingestion** | `POST` | `/api/v1/events/ingest` | High-throughput collector ingestion with deduplication. |
| **Incidents** | `GET` | `/api/incidents` | List incidents with filtering by severity, status, and tenant. |
| | `PATCH` | `/api/incidents/{id}/transition` | Execute formal 10-state lifecycle transition. |
| **Threat Intel** | `GET` | `/api/threat-intelligence` | Retrieve active Indicators of Compromise (IOCs). |
| | `GET` | `/api/threat-intelligence/stix` | Export threat intelligence as a standard STIX 2.1 JSON bundle. |
| **Forensics** | `POST` | `/api/phishing/analyze` | Parse RFC-822 email, verify SPF/DKIM/DMARC, scan regional lures. |
| | `POST` | `/api/typosquat/scan` | Generate homoglyphs and calculate domain similarity metrics. |
| | `POST` | `/api/osint/scan` | Map Ethiopian ASN routing (`AS24757`), open ports, and SSL health. |
| **AI Copilot** | `POST` | `/api/ai/investigate` | Run multi-agent AI analysis across MITRE ATT&CK vectors. |
| | `POST` | `/api/ai/chat` | Interactive Tier-1/Tier-2 analyst assistant copilot. |
| **SOAR Response** | `GET` | `/api/response/actions` | Retrieve response action queue with approval statuses. |
| | `POST` | `/api/response/execute` | Dispatch containment actions (dual-custody approval enforced). |
| **System Health** | `GET` | `/health/live` | Kubernetes liveness probe endpoint. |
| | `GET` | `/health/ready` | Readiness probe (verifies database and connector status). |

---

## 🧪 9. Testing & Quality Verification

All 279 automated tests verify unit logic, pipeline integration, AI grounding, and security controls:

```bash
# Run backend test suite (279 passing tests, 100% green pass rate)
python -m pytest tests/ -v

# Verify frontend build & TypeScript compilation
npm --prefix apps/web run build
```

---

## ⚠️ 10. Production Notes

- **Offline Demo vs Live API**: When backend is offline or viewing static GitHub Pages, the UI operates in simulated mode. Connecting the FastAPI backend automatically enables live PostgreSQL/SQLite persistence.
- **Dual-Custody Protection**: Destructive containment actions (`isolate_host`, `block_ip`, `disable_user`) require human approval and cannot be executed autonomously by AI.
- **Fail-Closed Security**: In production (`ENVIRONMENT=production`), the backend verifies strong credentials, enforces IP rate-limiting, and rejects default keys.

---

## 🗺️ 11. Roadmap

- **v1.1 (Current Release)**: Full-stack React 19 + FastAPI, 279 automated tests, STIX 2.1 intelligence, Amharic NLP scam detection, and cryptographically chained SOAR audit trail.
- **v1.2 (Target: Q3 2026)**: Local air-gapped LLM inference via Ollama / vLLM, and SCADA / ICS protocol analyzers.
- **v2.0 (Target: Q1 2027)**: Inter-bank threat sharing federation for Ethiopian financial institutions.

---

## 🤝 12. Contribution & License

- **License**: Apache 2.0 License. See [`LICENSE`](./LICENSE).
- **Contributing**: Contributions are welcome! Review [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
- **Principal Lead Architect & Core Maintainer**: [@Mr-Nobody-Anonymous](https://github.com/Mr-Nobody-Anonymous) — Core platform architecture, SIEM detection rules, SOAR engine, automated test suite, and frontend engineering.
- **Repository Administrator & Co-Lead**: [@AbeniYirgalem](https://github.com/AbeniYirgalem) — Project management, documentation, and upstream repository administration.

---

## 👥 13. Project Team & Contributors
<a id="-13-project-team--contributors"></a>

| # | Full Name | Student ID | Project Role |
| :-: | :--- | :--- | :--- |
| 1 | **Beamlak Sintayehu** ([@Mr-Nobody-Anonymous](https://github.com/Mr-Nobody-Anonymous)) | `CTC-912-24` | Principal Lead Architect & Core Maintainer |
| 2 | **Yonas Abadi** | `CTC-7422-26` | Contributor |
| 3 | **Abenezer Yirgalem** ([@AbeniYirgalem](https://github.com/AbeniYirgalem)) | `CTC-041-26` | Repository Administrator & Co-Lead |
| 4 | **FikreMariam Worku** | `CTC-7267-26` | Team Member |
| 5 | **Remedan Hante** | `CTC-7445-26` | Team Member |
| 6 | **Eyerusalem Solomon** | `CTC-6739-26` | Team Member |

---

## 📜 License
<a id="License-1-ov-file"></a>

Distributed under the **Apache 2.0 License**. See [`LICENSE`](./LICENSE) for full legal text.

<p align="center">
  Built with ❤️ for Ethiopian and Global Cyber Resilience.
</p>
