"""
SQLAlchemy ORM Models for ETHIO-CYBERGUARD
Production PostgreSQL Database Schema for Enterprise Multi-Tenant SOC Operations
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, Index, JSON, Enum
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

def generate_uuid():
    return str(uuid.uuid4())

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True, index=True)
    sector = Column(String(100), nullable=False) # Banking, Telecom, Government, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    users = relationship("User", back_populates="organization")
    incidents = relationship("Incident", back_populates="organization")
    assets = relationship("Asset", back_populates="organization")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="SECURITY_ANALYST", index=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_locked = Column(Boolean, default=False, nullable=False)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    lockout_until = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    organization = relationship("Organization", back_populates="users")
    comments = relationship("Comment", back_populates="user")

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_number = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False, default="MEDIUM", index=True) # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), nullable=False, default="NEW", index=True) # NEW, TRIAGED, ASSIGNED, INVESTIGATING, CONTAINMENT_PENDING, CONTAINED, ERADICATION, RECOVERY, CLOSED, REOPENED
    risk_score = Column(Integer, default=50, nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    affected_asset = Column(String(255), nullable=True)
    asset_ip = Column(String(45), nullable=True)
    assigned_to = Column(String(255), nullable=True)
    sla_deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    closed_at = Column(DateTime(timezone=True), nullable=True)

    organization = relationship("Organization", back_populates="incidents")
    alerts = relationship("Alert", back_populates="incident")
    comments = relationship("Comment", back_populates="incident")
    evidence = relationship("Evidence", back_populates="incident")
    tasks = relationship("IncidentTask", back_populates="incident")
    history = relationship("IncidentHistory", back_populates="incident")

class IncidentHistory(Base):
    __tablename__ = "incident_history"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False, index=True)
    previous_status = Column(String(50), nullable=True)
    new_status = Column(String(50), nullable=False)
    changed_by = Column(String(255), nullable=False)
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    incident = relationship("Incident", back_populates="history")

class IncidentTask(Base):
    __tablename__ = "incident_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_by = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    incident = relationship("Incident", back_populates="tasks")

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    alert_name = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    source = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    raw_payload = Column(JSON, nullable=True)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    incident = relationship("Incident", back_populates="alerts")

class Event(Base):
    __tablename__ = "events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    event_id = Column(String(100), nullable=False, unique=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    source_ip = Column(String(45), nullable=True, index=True)
    destination_ip = Column(String(45), nullable=True, index=True)
    host_name = Column(String(255), nullable=True)
    ecs_category = Column(String(100), nullable=True)
    raw_event_hash = Column(String(64), nullable=False, index=True) # SHA-256 for idempotency
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False) # Server, Workstation, Router, Firewall
    criticality = Column(String(20), nullable=False, default="MEDIUM") # LOW, MEDIUM, HIGH, TIER_1_CRITICAL
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True, index=True)
    status = Column(String(50), default="ACTIVE", nullable=False) # ACTIVE, ISOLATED, DECOMMISSIONED
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    organization = relationship("Organization", back_populates="assets")

class DetectionRule(Base):
    __tablename__ = "detection_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    rule_id = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default="production", nullable=False)
    confidence = Column(String(20), default="high", nullable=False)
    yaml_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

class PlaybookExecution(Base):
    __tablename__ = "playbook_executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    playbook_name = Column(String(255), nullable=False)
    action_type = Column(String(100), nullable=False)
    target = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False) # PENDING_APPROVAL, APPROVED, REJECTED, EXECUTED, FAILED, ROLLED_BACK
    requested_by = Column(String(255), nullable=False)
    approved_by = Column(String(255), nullable=True)
    dual_custody_verified = Column(Boolean, default=False, nullable=False)
    dry_run = Column(Boolean, default=False, nullable=False)
    execution_output = Column(JSON, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    indicator = Column(String(255), nullable=False, unique=True, index=True)
    ioc_type = Column(String(50), nullable=False, index=True) # ip, domain, url, hash
    threat_actor = Column(String(100), nullable=True)
    severity = Column(String(20), nullable=False)
    confidence = Column(Integer, default=85, nullable=False)
    source = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

class Comment(Base):
    __tablename__ = "comments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    author_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    incident = relationship("Incident", back_populates="comments")
    user = relationship("User", back_populates="comments")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    incident_id = Column(String(36), ForeignKey("incidents.id"), nullable=False, index=True)
    evidence_name = Column(String(255), nullable=False)
    evidence_type = Column(String(100), nullable=False)
    sha256_hash = Column(String(64), nullable=False, index=True) # Cryptographic proof
    size_bytes = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=True)
    uploaded_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    incident = relationship("Incident", back_populates="evidence")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    user_id = Column(String(36), nullable=True)
    user_email = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    prev_hash = Column(String(64), nullable=False)
    current_hash = Column(String(64), nullable=False, index=True)
