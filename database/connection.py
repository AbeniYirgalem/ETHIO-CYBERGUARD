"""
Database Connection & Session Management for ETHIO-CYBERGUARD
Configures PostgreSQL (production) or SQLite (dev/test fallback) with SQLAlchemy ORM.
"""

import os
import hashlib
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, Organization, User, Incident, Asset, DetectionRule, ThreatIntelligence

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./ethio_cyberguard.db"
)

# For SQLite, check_same_thread needs to be False
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def hash_password(password: str) -> str:
    """Secure PBKDF2-SHA256 password hash."""
    salt = "ecg_salt_2026_ethiopia"
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def init_db():
    """Initializes tables and populates baseline seed records if empty."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Check if baseline organization exists
        if not db.query(Organization).first():
            cbe = Organization(
                id="org-cbe-001",
                name="Commercial Bank of Ethiopia",
                code="CBE",
                sector="Banking",
                is_active=True
            )
            telebirr = Organization(
                id="org-telecom-002",
                name="Ethio Telecom / Telebirr",
                code="ETHIOTELECOM",
                sector="Telecom",
                is_active=True
            )
            insa = Organization(
                id="org-insa-003",
                name="Information Network Security Administration",
                code="INSA",
                sector="Government",
                is_active=True
            )
            db.add_all([cbe, telebirr, insa])
            db.commit()

            # Seed default users
            analyst = User(
                id="usr-analyst-001",
                email="analyst@cbe.com.et",
                hashed_password=hash_password("Analyst@2026!"),
                full_name="Dawit Mengistu",
                role="SECURITY_ANALYST",
                organization_id="org-cbe-001",
                is_active=True
            )
            admin = User(
                id="usr-admin-002",
                email="admin@insa.gov.et",
                hashed_password=hash_password("SuperAdmin@2026!"),
                full_name="INSA Security Operations Lead",
                role="SUPER_ADMIN",
                organization_id="org-insa-003",
                is_active=True
            )
            responder = User(
                id="usr-responder-003",
                email="responder@telebirr.et",
                hashed_password=hash_password("Responder@2026!"),
                full_name="Almaz Bekele",
                role="INCIDENT_RESPONDER",
                organization_id="org-telecom-002",
                is_active=True
            )
            db.add_all([analyst, admin, responder])
            db.commit()

            # Seed baseline critical assets
            srv4 = Asset(
                id="ast-001",
                name="SERVER-04",
                ip_address="10.10.1.24",
                asset_type="Server",
                criticality="TIER_1_CRITICAL",
                organization_id="org-cbe-001",
                status="ACTIVE"
            )
            gw1 = Asset(
                id="ast-002",
                name="TELEBIRR-GW-01",
                ip_address="10.20.4.15",
                asset_type="Gateway",
                criticality="TIER_1_CRITICAL",
                organization_id="org-telecom-002",
                status="ACTIVE"
            )
            db.add_all([srv4, gw1])
            db.commit()

            # Seed initial incident
            inc = Incident(
                id="e0000000-0000-0000-0000-000000000001",
                incident_number="INC-00042",
                title="Suspicious Obfuscated PowerShell Activity & C2 Beaconing",
                description="PowerShell process with encoded command executed by administrator. Outbound connection to 185.220.101.5 on port 443.",
                severity="CRITICAL",
                status="INVESTIGATING",
                risk_score=92,
                organization_id="org-cbe-001",
                affected_asset="SERVER-04",
                asset_ip="10.10.1.24",
                assigned_to="Dawit Mengistu"
            )
            db.add(inc)
            db.commit()
    finally:
        db.close()

def get_db() -> Generator[Session, None, None]:
    """FastAPI Dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
