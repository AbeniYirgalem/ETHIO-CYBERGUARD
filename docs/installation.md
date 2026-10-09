# 🛠️ Installation & Deployment Guide

**Version**: 1.1.0  
**Stack**: FastAPI (Python 3.10+), React 19, TypeScript, Vite 8, Tailwind CSS v4, PostgreSQL 16, Redis 7  
**Test Suite**: 75 Tests (100% Pass Rate)  

---

## 1. System Requirements

- **Operating System**: Linux (Ubuntu 22.04+ LTS, RHEL 9), macOS (Sonoma+), or Windows 10/11 (PowerShell 7+ or WSL2).
- **Python**: 3.10 or higher (`python --version`)
- **Node.js**: 20.0 or higher (`node --version`) with `npm` 10+
- **Memory**: Minimum 4 GB RAM (8 GB+ recommended for running high-throughput 50k+ EPS benchmarks)
- **Docker**: Docker Engine 24+ and Docker Compose v2 (recommended for containerized deployment)

---

## 2. Local Development Setup

### 2.1 Clone the Repository
```bash
git clone https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD.git
cd ETHIO-CYBERGUARD
```

### 2.2 Backend Environment & Dependencies
```bash
# Create and activate virtual environment
python -m venv venv

# On Linux/macOS:
source venv/bin/activate
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r apps/api/requirements.txt
pip install -r requirements-dev.txt
```

### 2.3 Frontend Environment & Build
```bash
# Navigate to web application directory
cd apps/web

# Install frontend dependencies
npm install

# Verify production build and chunk splitting
npm run build

# Return to root directory
cd ../..
```

---

## 3. Running Development Services

### 3.1 Start FastAPI Central Backend
```bash
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```
- **API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON Spec**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)
- **Live SOC WebSocket**: `ws://localhost:8000/ws/live-events`
- **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)

### 3.2 Start React SOC HUD Web Console
In a separate terminal:
```bash
cd apps/web
npm run dev
```
- **Web Application URL**: [http://localhost:5173](http://localhost:5173)

---

## 4. Full-Stack Docker Deployment

To launch all services (PostgreSQL 16, Redis, Backend API, and React Frontend) with Docker Compose:
```bash
# Build and run all containers in detached mode
docker-compose up --build -d

# Check service health
docker-compose ps
```

Services will be accessible at:
- **Web Dashboard**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000`
- **Syslog Collector**: `UDP port 5140`

---

## 5. Verification & Test Suite Execution

ETHIO-CYBERGUARD includes 75 automated unit, integration, and security tests. Run the complete test suite to verify system integrity:

```bash
# Run entire test suite (75 tests)
python -m pytest tests/ -v

# Run targeted test suites
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v
python -m pytest tests/security/ -v

# Run frontend linting and type checks
npm --prefix apps/web run lint
npm --prefix apps/web run build
```
