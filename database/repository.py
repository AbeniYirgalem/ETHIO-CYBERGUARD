"""
Repository Data Access Layer for ETHIO-CYBERGUARD
Handles all transactional database CRUD operations with multi-tenancy and audit integrity.
"""

import hashlib
import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from database.models import (
    User, Organization, Incident, IncidentHistory, IncidentTask,
    Alert, Event, Asset, DetectionRule, PlaybookExecution,
    ThreatIntelligence, Comment, Evidence, AuditLog
)
from database.connection import hash_password, verify_password

def utcnow():
    return datetime.now(timezone.utc)

class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def list(self, organization_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50) -> List[Incident]:
        query = self.db.query(Incident)
        if organization_id:
            query = query.filter(Incident.organization_id == organization_id)
        if status:
            query = query.filter(Incident.status == status)
        return query.order_by(Incident.created_at.desc()).limit(limit).all()

    def get(self, incident_id: str) -> Optional[Incident]:
        return self.db.query(Incident).filter(
            (Incident.id == incident_id) | (Incident.incident_number == incident_id)
        ).first()

    def create(self, **kwargs) -> Incident:
        incident = Incident(**kwargs)
        if not incident.incident_number:
            count = self.db.query(Incident).count() + 1
            incident.incident_number = f"INC-{count:05d}"
        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def transition_status(self, incident_id: str, new_status: str, changed_by: str, reason: Optional[str] = None) -> Optional[Incident]:
        incident = self.get(incident_id)
        if not incident:
            return None
        
        prev_status = incident.status
        incident.status = new_status
        incident.updated_at = utcnow()
        if new_status == "CLOSED":
            incident.closed_at = utcnow()

        history_entry = IncidentHistory(
            incident_id=incident.id,
            previous_status=prev_status,
            new_status=new_status,
            changed_by=changed_by,
            reason=reason or f"Status changed from {prev_status} to {new_status}"
        )
        self.db.add(history_entry)
        self.db.commit()
        self.db.refresh(incident)
        return incident

    def add_comment(self, incident_id: str, author_name: str, content: str, user_id: Optional[str] = None) -> Comment:
        comment = Comment(
            incident_id=incident_id,
            user_id=user_id,
            author_name=author_name,
            content=content
        )
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def add_task(self, incident_id: str, title: str, description: Optional[str] = None) -> IncidentTask:
        task = IncidentTask(
            incident_id=incident_id,
            title=title,
            description=description
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def add_evidence(self, incident_id: str, name: str, evidence_type: str, raw_bytes: bytes, uploaded_by: str) -> Evidence:
        sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
        evidence = Evidence(
            incident_id=incident_id,
            evidence_name=name,
            evidence_type=evidence_type,
            sha256_hash=sha256_hash,
            size_bytes=len(raw_bytes),
            uploaded_by=uploaded_by
        )
        self.db.add(evidence)
        self.db.commit()
        self.db.refresh(evidence)
        return evidence

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email.lower()).first()

    def create(self, email: str, password: str, full_name: str, role: str, organization_id: Optional[str] = None) -> User:
        user = User(
            email=email.lower(),
            hashed_password=hash_password(password),
            full_name=full_name,
            role=role,
            organization_id=organization_id,
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def record_login_failure(self, email: str) -> Optional[User]:
        user = self.get_by_email(email)
        if not user:
            return None
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.is_locked = True
            user.lockout_until = utcnow() + timedelta(minutes=15)
        self.db.commit()
        self.db.refresh(user)
        return user

    def reset_login_failures(self, email: str):
        user = self.get_by_email(email)
        if user:
            user.failed_login_attempts = 0
            user.is_locked = False
            user.lockout_until = None
            self.db.commit()

class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def log(self, user_email: str, action: str, resource_type: str, resource_id: Optional[str] = None, details: Optional[Dict] = None, ip_address: Optional[str] = None, user_id: Optional[str] = None) -> AuditLog:
        last_log = self.db.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
        prev_hash = last_log.current_hash if last_log else "0000000000000000000000000000000000000000000000000000000000000000"

        ts = utcnow().isoformat()
        payload = f"{prev_hash}|{ts}|{user_email}|{action}|{resource_type}|{resource_id}|{json.dumps(details or {})}"
        current_hash = hashlib.sha256(payload.encode()).hexdigest()

        entry = AuditLog(
            user_id=user_id,
            user_email=user_email,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            prev_hash=prev_hash,
            current_hash=current_hash
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

class EventRepository:
    def __init__(self, db: Session):
        self.db = db

    def is_duplicate(self, raw_hash: str) -> bool:
        return self.db.query(Event).filter(Event.raw_event_hash == raw_hash).first() is not None

    def store_event(self, event_id: str, timestamp: datetime, event_type: str, source_ip: str, destination_ip: str, raw_event_str: str, host_name: Optional[str] = None, ecs_category: Optional[str] = None, org_id: Optional[str] = None) -> Optional[Event]:
        raw_hash = hashlib.sha256(raw_event_str.encode()).hexdigest()
        if self.is_duplicate(raw_hash):
            return None # Idempotent drop

        event = Event(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            source_ip=source_ip,
            destination_ip=destination_ip,
            host_name=host_name,
            ecs_category=ecs_category,
            raw_event_hash=raw_hash,
            organization_id=org_id
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event
