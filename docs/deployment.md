# 🚀 ETHIO-CYBERGUARD Production Deployment Guide

## 1. Quickstart with Docker Compose

Deploy the entire stack (PostgreSQL, Redis, Central API, AI Engine, and Web SOC Dashboard) using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD.git
cd ETHIO-CYBERGUARD

# Configure environment variables
cp .env.example .env

# Build and launch all services
docker-compose up -d --build
```

Access the services:
- **SOC Web Dashboard**: `http://localhost:3000`
- **Central API & Docs**: `http://localhost:8000/docs`
- **PostgreSQL Database**: `localhost:5432`
- **Syslog Listener**: `UDP port 5140`

---

## 2. Manual Local Development

### Backend & API
```bash
cd apps/api
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend SOC Dashboard
```bash
cd apps/web
npm install
npm run dev
```
Open `http://localhost:5173` to explore the interactive SOC interface.

---

## 3. Production Hardening Checklist
- [ ] Configure TLS certificates via Nginx or Traefik reverse proxy.
- [ ] Rotate database passwords and set strong `JWT_SECRET`.
- [ ] Enable MFA for all `SUPER_ADMIN` and `SOC_MANAGER` accounts.
- [ ] Configure persistent volume mounts for `/var/lib/postgresql/data`.
- [ ] Establish automated hourly database backups.
- [ ] Enable Syslog TLS (RFC 5425) for encrypted log transport across WAN links.

---

## 4. Live GitHub Pages Deployment (1-Time Setup for Repository Owner)

The frontend SOC Dashboard is automatically built and committed to the `gh-pages` branch on every push by the `.github/workflows/deploy-pages.yml` GitHub Action.

Because GitHub requires repository Owner/Admin permissions to activate GitHub Pages the very first time:
1. Open the repository settings: [ETHIO-CYBERGUARD Settings > Pages](https://github.com/AbeniYirgalem/ETHIO-CYBERGUARD/settings/pages)
2. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`
   - **Branch**: Select `gh-pages` and folder `/(root)`
3. Click **Save**.
4. The live site will immediately be served at:
   👉 **`https://AbeniYirgalem.github.io/ETHIO-CYBERGUARD/`**
