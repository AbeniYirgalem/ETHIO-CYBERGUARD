"""
ETHIO-CYBERGUARD Incident Lifecycle & Forensics Chain of Custody Engine
Implements strict state transition management:
NEW -> TRIAGED -> INVESTIGATING -> CONTAINED -> ERADICATED -> RECOVERED -> CLOSED
Tracks evidence objects, cryptographic hashes, forensic timeline, and post-incident reporting.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import hashlib
import uuid

VALID_LIFECYCLE_STATES = [
    "NEW",
    "TRIAGED",
    "INVESTIGATING",
    "CONTAINED",
    "ERADICATED",
    "RECOVERED",
    "CLOSED"
]

class ForensicsEvidence:
    """
    Immutable forensic evidence item with cryptographic verification hash.
    """
    def __init__(self, evidence_type: str, description: str, raw_content: str, collected_by: str):
        self.evidence_id = f"EV-{uuid.uuid4().hex[:8].upper()}"
        self.evidence_type = evidence_type # e.g., 'pcap', 'memory_dump', 'email_rfc822', 'auth_log'
        self.description = description
        self.collected_by = collected_by
        self.collected_at = datetime.now(timezone.utc).isoformat()
        self.sha256 = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "evidence_id": self.evidence_id,
            "type": self.evidence_type,
            "description": self.description,
            "collected_by": self.collected_by,
            "collected_at": self.collected_at,
            "sha256": self.sha256
        }


class IncidentLifecycleManager:
    """
    Manages state progression, evidence logging, and post-incident audits.
    """

    def __init__(self, incident_id: str, title: str, severity: str = "HIGH"):
        self.incident_id = incident_id
        self.title = title
        self.severity = severity
        self.state = "NEW"
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at
        self.assignee: Optional[str] = None
        self.timeline: List[Dict[str, Any]] = []
        self.evidence_items: List[ForensicsEvidence] = []
        self.closed_reason: Optional[str] = None

        self._record_transition("INITIALIZED", "Incident created by correlation pipeline")

    def _record_transition(self, action: str, details: str, actor: str = "SYSTEM"):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "state": self.state,
            "actor": actor,
            "details": details
        }
        self.timeline.append(entry)
        self.updated_at = entry["timestamp"]

    def transition_to(self, new_state: str, actor: str, notes: str = "") -> bool:
        new_state = new_state.upper()
        if new_state not in VALID_LIFECYCLE_STATES:
            raise ValueError(f"Invalid lifecycle state: {new_state}. Must be one of {VALID_LIFECYCLE_STATES}")

        current_idx = VALID_LIFECYCLE_STATES.index(self.state)
        target_idx = VALID_LIFECYCLE_STATES.index(new_state)

        # Allow orderly forward movement or reopen from closed
        if target_idx <= current_idx and not (self.state == "CLOSED" and new_state == "INVESTIGATING"):
            if target_idx != current_idx:
                raise ValueError(f"Cannot transition backwards from {self.state} to {new_state}")

        old_state = self.state
        self.state = new_state
        self._record_transition(f"TRANSITION_{old_state}_TO_{new_state}", notes or f"Moved from {old_state} to {new_state}", actor)
        return True

    def assign_analyst(self, analyst_id: str, assigned_by: str = "SUPERVISOR"):
        self.assignee = analyst_id
        self._record_transition("ASSIGN_ANALYST", f"Assigned to analyst {analyst_id}", assigned_by)

    def attach_evidence(self, evidence_type: str, description: str, raw_content: str, collected_by: str) -> ForensicsEvidence:
        ev = ForensicsEvidence(evidence_type, description, raw_content, collected_by)
        self.evidence_items.append(ev)
        self._record_transition("ATTACH_EVIDENCE", f"Attached evidence {ev.evidence_id} (SHA256: {ev.sha256[:12]}...)", collected_by)
        return ev

    def generate_post_incident_report(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "title": self.title,
            "severity": self.severity,
            "final_state": self.state,
            "created_at": self.created_at,
            "closed_at": self.updated_at if self.state == "CLOSED" else None,
            "total_timeline_events": len(self.timeline),
            "evidence_count": len(self.evidence_items),
            "evidence_hashes": [e.sha256 for e in self.evidence_items],
            "timeline": self.timeline
        }
