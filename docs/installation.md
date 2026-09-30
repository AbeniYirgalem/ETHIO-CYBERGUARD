# Installation & Deployment Guide

This guide walks you through setting up and running **ETHIO-CYBERGUARD** in local development, evaluation sandbox, or containerized production environments.

---

## 1. System Requirements

- **Operating System**: Linux (Ubuntu 22.04+ LTS, RHEL 9), macOS (Sonoma+), or Windows 10/11 with WSL2 / PowerShell 7+
- **Python**: 3.10 or higher
- **Node.js**: v18.0 or higher (v20+ recommended)
- **Memory**: Minimum 4 GB RAM (8 GB+ recommended for running live 50k+ EPS benchmarks)
- **Docker**: Docker Engine 24+ and Docker Compose v2 (optional for containerized deployment)

---

## 2. Quickstart Installation

### Clone the Repository
```bash
git clone https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD.git
cd ETHIO-CYBERGUARD
```

### Install Backend Dependencies
```bash
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\Activate.ps1

pip install -r apps/api/requirements.txt
pip install pytest pytest-cov
```

### Install Frontend Dependencies
```bash
cd apps/web
npm install
cd ../..
```

---

## 3. Running Development Services

### Start FastAPI Central Backend
```bash
python -m uvicorn apps.api.main:app --reload --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- WebSocket Stream: `ws://localhost:8000/ws/live-events`

### Start React SOC Web Console
```bash
cd apps/web
npm run dev
```
- Web Application: [http://localhost:5173](http://localhost:5173)

---

## 4. Running with Docker Compose

To launch the full stack (PostgreSQL, Redis, Backend API, and Web Console):
```bash
docker-compose up --build -d
```
Check health:
```bash
docker-compose ps
```

---

## 5. Running the Test Suite
```bash
python -m pytest tests/ -v
```
To run security and tenant isolation tests:
```bash
python -m pytest tests/security/ -v
```
