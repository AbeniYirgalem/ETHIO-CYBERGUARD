"""
ETHIO-CYBERGUARD Canonical Event Schema (Elastic Common Schema Subset)
Formal dictionary definitions and typed structures for normalized security events.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib


@dataclass
class Observable:
    type: str  # domain, ip, url, hash_sha256, user, email
    value: str
    role: Optional[str] = None  # sender_domain, c2_host, target_user


@dataclass
class CanonicalEvent:
    id: str
    timestamp: str
    tenant_id: str
    event_kind: str  # event, alert, metric
    event_category: List[str]  # email, endpoint, network, threat_intel, authentication
    event_type: List[str]  # phishing_email, process_creation, connection_attempt
    event_action: str
    event_outcome: str  # success, failure, unknown
    severity: str  # INFO, LOW, MEDIUM, HIGH, CRITICAL

    source_ip: Optional[str] = None
    source_port: Optional[int] = None
    destination_ip: Optional[str] = None
    destination_port: Optional[int] = None

    user_name: Optional[str] = None
    user_email: Optional[str] = None

    host_name: Optional[str] = None
    host_ip: Optional[str] = None

    url_full: Optional[str] = None
    dns_question_name: Optional[str] = None

    process_name: Optional[str] = None
    process_command_line: Optional[str] = None

    file_name: Optional[str] = None
    file_hash_sha256: Optional[str] = None

    observables: List[Dict[str, str]] = field(default_factory=list)
    raw_event_id: Optional[str] = None
    mode: str = "production"  # production vs simulation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "@timestamp": self.timestamp,
            "id": self.id,
            "tenant_id": self.tenant_id,
            "event": {
                "kind": self.event_kind,
                "category": self.event_category,
                "type": self.event_type,
                "action": self.event_action,
                "outcome": self.event_outcome,
                "severity": self.severity,
                "mode": self.mode
            },
            "source": {
                "ip": self.source_ip,
                "port": self.source_port
            },
            "destination": {
                "ip": self.destination_ip,
                "port": self.destination_port
            },
            "user": {
                "name": self.user_name,
                "email": self.user_email
            },
            "host": {
                "name": self.host_name,
                "ip": self.host_ip
            },
            "url": {
                "full": self.url_full
            },
            "dns": {
                "question": {"name": self.dns_question_name}
            },
            "process": {
                "name": self.process_name,
                "command_line": self.process_command_line
            },
            "file": {
                "name": self.file_name,
                "hash": {"sha256": self.file_hash_sha256}
            },
            "observables": self.observables,
            "raw_event_id": self.raw_event_id
        }
