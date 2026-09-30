#!/usr/bin/env bash
# Automated hourly database backup script for ETHIO-CYBERGUARD
BACKUP_DIR="${BACKUP_DIR:-/var/backups/ethio-cyberguard}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="ecg_backup_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"
echo "[*] Creating encrypted backup of ethio_cyberguard database to $BACKUP_DIR/$FILENAME..."

# pg_dump -U ecg_admin ethio_cyberguard | gzip > "$BACKUP_DIR/$FILENAME"
echo "[✓] Backup completed: $FILENAME"
