# 🚀 ETHIO-CYBERGUARD Production Deployment Guide

**Version**: 1.1.0  
**Environments**: Docker Compose, Kubernetes, Bare Metal, Air-Gapped SOC Enclaves  

---

## 1. Quickstart with Docker Compose

Deploy the complete stack (PostgreSQL 16, Redis 7, Central API, AI Engine, and React 19 SOC Web Dashboard) using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD.git
cd ETHIO-CYBERGUARD

# Configure environment variables
cp .env.example .env

# Build and launch all services in detached mode
docker-compose up -d --build
```

Access the deployed services:
- **SOC Web Dashboard**: `http://localhost:3000`
- **Central API & Docs**: `http://localhost:8000/docs`
- **PostgreSQL Database**: `localhost:5432`
- **Syslog Listener**: `UDP port 5140`
- **Prometheus Metrics**: `http://localhost:8000/metrics`

---

## 2. Manual Local Development

### 2.1 Backend API
```bash
# From repository root
python -m venv venv

# On Windows PowerShell:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r apps/api/requirements.txt
pip install -r requirements-dev.txt

# Run FastAPI backend with ASGI lifespan context manager
python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2.2 Frontend SOC Dashboard
```bash
# In a separate terminal
cd apps/web
npm install
npm run dev
```
Open `http://localhost:5173` to explore the interactive SOC interface.

---

## 3. Kubernetes Deployment & Health Probes

ETHIO-CYBERGUARD includes native Kubernetes health endpoints:
- **Liveness Probe**: `GET /health/live` (confirms FastAPI process responsiveness)
- **Readiness Probe**: `GET /health/ready` (confirms database connectivity, queue buffer health, and connector states)
- **Metrics Scraping**: `GET /metrics` (Prometheus exposition format)

### Example Kubernetes Deployment Snippet
```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 15
```

---

## 4. Production Hardening Checklist
- [ ] Configure TLS certificates via Nginx or Traefik reverse proxy (TLS 1.3 enforced).
- [ ] Rotate database passwords and set strong `JWT_SECRET` in `.env`.
- [ ] Enable MFA for all `SUPER_ADMIN` and `SOC_MANAGER` accounts.
- [ ] Configure persistent volume mounts for `/var/lib/postgresql/data`.
- [ ] Establish automated hourly database backups.
- [ ] Enable Syslog TLS (RFC 5425) for encrypted log transport across WAN links.
- [ ] Verify circuit breaker cooldown parameters for external firewalls and EDR agents.

---

## 5. Live GitHub Pages Deployment (1-Time Setup for Repository Owner)

The frontend SOC Dashboard is automatically built and committed to the `gh-pages` branch on every push by the `.github/workflows/deploy-pages.yml` GitHub Action.

Because GitHub requires repository Owner/Admin permissions to activate GitHub Pages the very first time:
1. Open the repository settings: [ETHIO-CYBERGUARD Settings > Pages](https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD/settings/pages)
2. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`
   - **Branch**: Select `gh-pages` and folder `/(root)`
3. Click **Save**.
4. The live site will immediately be served at:
   👉 **`https://AbeniYirgalem.github.io/ETHIO-CYBERGUARD/`**
