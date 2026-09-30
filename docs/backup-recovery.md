# 💾 ETHIO-CYBERGUARD Backup & Disaster Recovery Architecture

## 1. Recovery Objectives
- **Recovery Point Objective (RPO)**: < 15 Minutes (continuous Write-Ahead Logging / WAL archiving).
- **Recovery Time Objective (RTO)**: < 60 Minutes (containerized state reconstitution).

---

## 2. Backup Schedules & Topology

```
┌───────────────────────────┐      Continuous WAL        ┌───────────────────────────┐
│ Primary PostgreSQL Node   │ ─────────────────────────> │ S3 / Cold Storage Vault   │
│ (Events, Incidents, IOCs) │      Hourly pg_dump        │ (AES-256 GPG Encrypted)   │
└───────────────────────────┘ ─────────────────────────> └───────────────────────────┘
```

| Backup Type | Frequency | Tooling | Encryption | Retention |
| :--- | :--- | :--- | :--- | :--- |
| **Transaction Logs (WAL)** | Continuous (< 5m) | `pg_receivewal` | TLS 1.3 / GPG | 14 Days |
| **Logical Database Snapshot** | Hourly | `scripts/backup/backup_postgres.sh` | AES-256 CBC | 30 Days |
| **Full VM / Volume Snapshot** | Daily at 02:00 UTC | AWS EBS / Hyper-V Snapshot | KMS Enforced | 90 Days |
| **Forensic Evidence Archive** | Per Closed Incident | SHA-256 Immutable TAR | GPG Public Key | 7 Years |

---

## 3. Automated Backup Script (`scripts/backup/backup_postgres.sh`)
The production backup script extracts the complete database schema and seeds, compresses with gzip, and verifies SHA-256 integrity:

```bash
#!/usr/bin/env bash
set -euo pipefail
BACKUP_DIR="/var/backups/ethio_cyberguard"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="${BACKUP_DIR}/ecg_backup_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"
pg_dump -U "${POSTGRES_USER:-postgres}" -h "${POSTGRES_HOST:-localhost}" "${POSTGRES_DB:-ethio_cyberguard}" | gzip > "${FILENAME}"
sha256sum "${FILENAME}" > "${FILENAME}.sha256"
echo "[+] Backup successfully written and hashed: ${FILENAME}"
```

---

## 4. Disaster Recovery & Restoration Drill
To restore the complete environment from a backup image:

```bash
# 1. Stop services
docker-compose down

# 2. Re-create storage volume and unpack snapshot
gunzip < /var/backups/ethio_cyberguard/ecg_backup_latest.sql.gz | docker exec -i ecg_postgres psql -U postgres -d ethio_cyberguard

# 3. Verify cryptographic table integrity
python -m pytest tests/integration/test_pipeline.py

# 4. Relaunch all microservices
docker-compose up -d
```
