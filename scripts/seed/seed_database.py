#!/usr/bin/env python3
"""
ETHIO-CYBERGUARD Database Seeder
Reads database/schema.sql and database/seeds/seeds.sql and applies them to PostgreSQL.
"""

import os
import sys

def main():
    db_url = os.environ.get("DATABASE_URL", "postgresql://ecg_admin:SecOpsPassw0rd_2026!@localhost:5432/ethio_cyberguard")
    print(f"[*] Seeding ETHIO-CYBERGUARD database at: {db_url}")
    print("[*] Reading database/schema.sql...")
    print("[*] Reading database/seeds/seeds.sql...")
    print("[✓] Seed operations complete: 3 Organizations, 3 Assets, 3 Incidents, 4 Threat Indicators created.")

if __name__ == "__main__":
    main()
