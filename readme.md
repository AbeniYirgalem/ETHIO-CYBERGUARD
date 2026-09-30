# 🛡️ ETHIO-CYBERGUARD

<p align="center">
  <strong>AI-Assisted Cybersecurity Platform for Threat Detection, Investigation, and Incident Response</strong>
  <br />
  <em>Centralized Security Operations Center (SOC) & SIEM tailored for educational, financial, enterprise, and governmental institutions.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-ETHIO--CYBERGUARD-00D9FF?style=for-the-badge&logo=shield" alt="Platform" />
  <img src="https://img.shields.io/badge/Architecture-Multi--Agent_AI-FF1744?style=for-the-badge" alt="Multi-Agent AI" />
  <img src="https://img.shields.io/badge/Frontend-React_19_+_Tailwind_v4-22C55E?style=for-the-badge&logo=react" alt="React 19" />
  <img src="https://img.shields.io/badge/Backend-FastAPI_REST-F59E0B?style=for-the-badge&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Database-PostgreSQL_+_Timescale-336791?style=for-the-badge&logo=postgresql" alt="PostgreSQL" />
</p>

---

## 🎯 1. System Vision & Architecture

ETHIO-CYBERGUARD is a next-generation SOC/SIEM platform engineered to provide accessible, high-performance security monitoring, event normalization, threat detection, multi-agent AI investigation, and **human-approved response**.

```
                    ┌─────────────────────────────┐
                    │       Security Sources      │
                    │                             │
                    │ • Windows endpoints         │
                    │ • Linux servers             │
                    │ • Network devices (Routers) │
                    │ • Firewalls                 │
                    │ • Core Banking Applications │
                    │ • Cloud services             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │      DATA COLLECTION         │
                    │                             │
                    │ Agents / Syslog / APIs      │
                    │ Filebeat / OpenTelemetry     │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │    INGESTION & NORMALIZATION│
                    │                             │
                    │ Parse → Validate → Normalize│
                    │ Enrich → Store               │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
          ┌──────────────────┐          ┌──────────────────┐
          │ Detection Engine │          │ Threat Intel     │
          │                  │          │                  │
          │ Rules            │          │ IPs              │
          │ Signatures       │          │ Domains          │
          │ Behavioral       │          │ Hashes           │
          │ Anomaly          │          │ CVEs             │
          └────────┬─────────┘          └────────┬─────────┘
                   │                             │
                   └──────────────┬──────────────┘
                                  ▼
                    ┌─────────────────────────────┐
                    │      CORRELATION ENGINE     │
                    │                             │
                    │ Events → Alerts → Incidents │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │       AI ANALYSIS LAYER     │
                    │                             │
                    │ Event Analysis Agent        │
                    │ Threat Intel Agent          │
                    │ Correlation Agent           │
                    │ Investigation Agent         │
                    │ Risk Agent                  │
                    │ Report Agent                │
                    │ Security Assistant          │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │       SOC DASHBOARD         │
                    │                             │
                    │ Alerts / Incidents / Risks  │
                    │ Investigations / Reports    │
                    │ AI Assistant / Analytics    │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │       RESPONSE CENTER       │
                    │                             │
                    │ Recommendations             │
                    │ Human approval              │
                    │ Response execution           │
                    │ Audit trail                 │
                    └─────────────────────────────┘
```

---

## 🤖 2. Multi-Agent AI Architecture

The platform integrates seven dedicated AI agents coordinated through a central investigation orchestrator. Every agent operates on structured telemetry schemas and is strictly grounded in observed evidence.

| # | Agent Name | Primary Responsibility | Input Telemetry | Primary Output Artifact |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **🔎 Security Event Analysis Agent** | Analyzes discrete events for malicious behaviors, LotL scripts, and evasion | Event JSON (process, command line, user) | Suspiciousness rating, confidence, MITRE ATT&CK techniques |
| **2** | **🧠 Threat Intelligence Agent** | Correlates observed IOCs with known threat actors and regional campaigns | IPs, domains, SHA-256 hashes, URLs | Reputation score, actor attribution, Ethio-CERT match |
| **3** | **🔗 Incident Correlation Agent** | Synthesizes disconnected alerts into a unified attack lifecycle | Rolling alert cluster across assets | Cyber Kill Chain progression, attack graph topology |
| **4** | **🔬 Investigation Agent** | Performs Tier-3 digital forensics and answers core SOC queries | Full incident dossier & evidence | What happened, start time, compromised systems, next steps |
| **5** | **⚠️ Risk Assessment Agent** | Quantifies transparent, multi-dimensional risk scores (0-100) | Asset criticality, threat level, blast radius | Overall score, Impact, Likelihood, Exposure, Confidence |
| **6** | **📝 Security Report Agent** | Automatically authors technical forensic and executive briefings | Multi-agent findings & timeline | Markdown technical dossiers and CISO executive briefs |
| **7** | **💬 Security Assistant** | Conversational SOC copilot grounded strictly in verified evidence | Analyst queries + Incident telemetry | Grounded responses with telemetry source citations |

---

## 🔒 3. Human-in-the-Loop Response Architecture

In alignment with strict cybersecurity safety standards, **ETHIO-CYBERGUARD never allows AI agents or LLMs to autonomously execute destructive containment actions**.

```
AI Recommendation (e.g. "Isolate SERVER-04", "Block IP 185.220.101.5")
       ↓
Analyst Reviews Evidence & Blast Radius
       ↓
┌───────────────┐
│ APPROVE       │
│ or            │
│ REJECT        │
└───────┬───────┘
        ↓
Response Engine
        ↓
Execution via Firewall / Endpoint Agent
        ↓
Immutable Cryptographic Audit Log
```

---

## 📁 4. Repository Structure

```
ETHIO-CYBERGUARD/
│
├── apps/
│   ├── web/                     # SOC Dashboard (React 19, TypeScript, Tailwind v4, Lucide)
│   └── api/                     # Central REST & WebSocket API (FastAPI, Pydantic v2)
│
├── services/
│   ├── ingestion/               # Event normalizer conforming to standard ECS
│   ├── detection-engine/        # SIGMA rule evaluator & behavioral anomaly engine
│   ├── correlation-engine/      # Incident graph builder & chronological timeline
│   └── ai/                      # 7 AI Agents + Orchestrator
│       ├── event_agent.py
│       ├── threat_agent.py
│       ├── correlation_agent.py
│       ├── investigation_agent.py
│       ├── risk_agent.py
│       ├── report_agent.py
│       ├── assistant_agent.py
│       └── orchestrator.py
│
├── database/
│   ├── schema.sql               # PostgreSQL core DDL (20+ entities, indexes, ENUMs)
│   └── seeds/seeds.sql          # Ethiopian SOC realistic seed data (CBE, Ethio Telecom, AAU)
│
├── collectors/
│   ├── endpoint/                # Windows (PowerShell) & Linux endpoint collectors
│   ├── syslog/                  # UDP RFC 5424 Syslog receiver
│   └── network/                 # Passive network flow and DNS sniffer
│
├── infrastructure/
│   └── docker/                  # Dockerfiles for API and Web services
│
├── docs/
│   ├── architecture.md          # Complete pipeline and system architecture
│   ├── ai-architecture.md       # 7-agent specifications and safety guardrails
│   ├── api.md                   # REST API documentation and endpoints
│   ├── database.md              # Database schema & Mermaid ERD
│   ├── security.md              # RBAC matrix and platform security guidelines
│   └── deployment.md            # Production deployment and hardening guide
│
├── docker-compose.yml           # Full stack deployment (Web, API, Postgres, Redis)
├── .env.example                 # Environment configuration template
└── README.md                    # Project documentation
```

---

## ⚡ 5. Quickstart Guide

### Option A: Docker Compose (Recommended)
```bash
# Clone the repository
git clone https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD.git
cd ETHIO-CYBERGUARD

# Copy environment variables
cp .env.example .env

# Launch all services
docker-compose up -d --build
```
- **Web SOC Dashboard**: [http://localhost:3000](http://localhost:3000)
- **Central API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

### Option B: Local Development

#### 1. Backend Service
```bash
cd apps/api
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 2. Frontend Web Dashboard
```bash
cd apps/web
npm install
npm run dev
```

---

## 🌍 6. Ethiopian Cybersecurity Context

ETHIO-CYBERGUARD is designed to address the specific challenges of organizations operating in Ethiopia and developing technology ecosystems:
- **Ethio Telecom Infrastructure Integration**: Native support for Ethiopian IP subnets (`197.156.0.0/16`, `213.55.0.0/16`).
- **Critical National Infrastructure Scenarios**: Preconfigured templates for Commercial Bank of Ethiopia (CBE) core banking ledgers, SWIFT nodes, and university campus networks.
- **Regulatory Alignment**: Designed for direct reporting and compliance integration with the **Information Network Security Agency (INSA)** and **Ethio-CERT**.

---

## 📄 7. License
Licensed under the Apache 2.0 License. Designed for education, research, and national cyber defense.
