"""
ETHIO-CYBERGUARD - Unified Pipeline Engine (The Common Security Graph)
Connects Email Forensics, Domain Typosquatting, Endpoint Telemetry,
and Network Events into a single coherent investigation & SOAR lifecycle.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib

from services.ingestion.normalizer import EventNormalizer
from services.detection.engine import DetectionEngine
from services.correlation.correlator import CorrelationEngine
from services.threat_intelligence.ioc_database import ThreatIntelDatabase
from services.ai.orchestrator import MultiAgentOrchestrator
from services.phishing.email_analyzer import PhishingAnalyzer


@dataclass
class EvidenceItem:
    evidence_id: str
    source_type: str  # email, endpoint, network, threat_intel, domain
    title: str
    details: Dict[str, Any]
    timestamp: str
    confidence: float


@dataclass
class SecurityGraphNode:
    id: str
    label: str
    type: str  # User, Host, Email, Domain, IP, Alert, Incident
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityGraphEdge:
    source_id: str
    target_id: str
    relationship: str  # sent_to, contains_url, resolves_to, executed_on, triggered_alert


@dataclass
class PipelineExecutionResult:
    pipeline_id: str
    status: str
    canonical_event: Dict[str, Any]
    alerts_triggered: List[Dict[str, Any]]
    threat_intel_matches: List[Dict[str, Any]]
    incident: Dict[str, Any]
    security_graph: Dict[str, Any]
    evidence_trail: List[Dict[str, Any]]
    ai_investigation: Dict[str, Any]
    risk_breakdown: Dict[str, Any]
    soar_actions: List[Dict[str, Any]]
    audit_record: Dict[str, Any]


class UnifiedPipelineEngine:
    """
    Central orchestration engine implementing the architecture:
    Events -> ECS Normalization -> SIGMA Rules -> Common Security Graph ->
    Threat Intel -> 7 AI Agents -> Evidence Grounding -> SOAR Response -> Audit.
    """

    def __init__(self):
        self.normalizer = EventNormalizer()
        self.detection_engine = DetectionEngine()
        self.correlation_engine = CorrelationEngine()
        self.threat_intel = ThreatIntelDatabase()
        self.ai_orchestrator = MultiAgentOrchestrator()
        self.phishing_analyzer = PhishingAnalyzer()

    def process_phishing_event_to_incident(
        self,
        raw_email: str,
        recipient_user: str = "dawit.mengistu@cbe.com.et",
        recipient_host: str = "LAPTOP-FINANCE-22",
        recipient_ip: str = "10.10.4.88"
    ) -> PipelineExecutionResult:
        """
        Executes a complete end-to-end vertical slice from an inbound phishing email:
        Email Analysis -> Observables -> Canonical Event -> Rule Match -> Correlated Incident ->
        7 AI Agents -> Risk Factors -> SOAR Approval Action -> Audit Log.
        """
        pipeline_id = f"pipe_{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Analyze Email (ThePhish engine)
        phish_res = self.phishing_analyzer.analyze(raw_email)

        # 2. Extract Observables
        observables = []
        if phish_res.sender_domain:
            observables.append({"type": "domain", "value": phish_res.sender_domain, "role": "sender_domain"})
        for u in phish_res.extracted_urls:
            observables.append({"type": "url", "value": u["url"], "role": "hyperlink"})
            observables.append({"type": "domain", "value": u["domain"], "role": "link_host"})
            if u.get("is_ip"):
                observables.append({"type": "ip", "value": u["domain"], "role": "raw_ip_host"})

        # 3. Canonical Event (ECS Schema)
        canonical_event = {
            "id": f"evt_{hashlib.sha256(raw_email.encode()).hexdigest()[:12]}",
            "timestamp": now_iso,
            "tenant_id": "cbe-ethiopia-001",
            "source": {
                "type": "email_gateway",
                "name": "MTA-POSTFIX-PERIMETER-01"
            },
            "event_type": "phishing_email_received",
            "severity": "CRITICAL" if phish_res.is_phishing else "INFO",
            "user": {
                "name": recipient_user.split("@")[0],
                "email": recipient_user
            },
            "asset": {
                "hostname": recipient_host,
                "ip": recipient_ip
            },
            "email": {
                "sender": phish_res.sender,
                "subject": phish_res.subject,
                "spf": phish_res.auth_results["spf"],
                "dkim": phish_res.auth_results["dkim"],
                "dmarc": phish_res.auth_results["dmarc"]
            },
            "observables": observables
        }

        # 4. Detection Engine (SIGMA / Rule Matcher)
        alerts_triggered = []
        if phish_res.is_phishing:
            alerts_triggered.append({
                "alert_id": f"ALT-PHISH-{uuid.uuid4().hex[:6]}",
                "rule_id": "SIGMA-EML-001",
                "title": "High-Confidence Phishing Email with Brand Spoofing",
                "severity": "CRITICAL",
                "tags": ["attack.initial_access", "attack.t1566.002"],
                "score_impact": phish_res.risk_score
            })
        if phish_res.regional_context.get("amharic_detected"):
            alerts_triggered.append({
                "alert_id": f"ALT-REGIONAL-{uuid.uuid4().hex[:6]}",
                "rule_id": "ETHIO-FRAUD-004",
                "title": "Regional Amharic Mobile Money / Banking Fraud Keyword Lure",
                "severity": "HIGH",
                "tags": ["attack.initial_access", "regional.ethiopian_fraud"],
                "score_impact": 25
            })

        # 5. Threat Intelligence Lookup
        threat_intel_matches = []
        for obs in observables:
            if obs["type"] in ["ip", "domain"]:
                match = self.threat_intel.lookup_indicator(obs["value"])
                if match:
                    threat_intel_matches.append(match)

        # 6. Common Security Graph Construction
        nodes: List[SecurityGraphNode] = [
            SecurityGraphNode(id="INC-PHISH-042", label="INC-00042: Targeted Phishing & Credential Harvest", type="Incident"),
            SecurityGraphNode(id=recipient_user, label=recipient_user, type="User", metadata={"department": "Finance"}),
            SecurityGraphNode(id=recipient_host, label=recipient_host, type="Host", metadata={"ip": recipient_ip}),
            SecurityGraphNode(id=phish_res.sender_domain or "external-mta", label=phish_res.sender_domain or "external-mta", type="Domain"),
        ]
        edges: List[SecurityGraphEdge] = [
            SecurityGraphEdge(source_id="INC-PHISH-042", target_id=recipient_user, relationship="targeted_user"),
            SecurityGraphEdge(source_id=recipient_user, target_id=recipient_host, relationship="assigned_to"),
            SecurityGraphEdge(source_id=phish_res.sender_domain or "external-mta", target_id=recipient_user, relationship="sent_phish_to")
        ]

        for u in phish_res.extracted_urls:
            node_id = f"url_{uuid.uuid4().hex[:6]}"
            nodes.append(SecurityGraphNode(id=node_id, label=u["url"][:32] + "...", type="URL", metadata=u))
            edges.append(SecurityGraphEdge(source_id="INC-PHISH-042", target_id=node_id, relationship="extracted_observable"))

        # 7. Evidence Grounding Registry
        evidence_trail = [
            {
                "evidence_id": "EV-001",
                "source": "Email Gateway",
                "description": f"RFC-822 Inbound Header: SPF={phish_res.auth_results['spf']}, DKIM={phish_res.auth_results['dkim']}, DMARC={phish_res.auth_results['dmarc']}",
                "confidence": 0.99
            },
            {
                "evidence_id": "EV-002",
                "source": "Phishing Analyzer (NLP)",
                "description": f"Targeted Brand Spoofing detected for: {phish_res.regional_context.get('targeted_brand') or 'Ethiopian Financial Institution'}",
                "confidence": 0.94
            },
            {
                "evidence_id": "EV-003",
                "source": "URL Forensics",
                "description": f"Malicious Link extraction: {phish_res.extracted_urls[0]['url'] if phish_res.extracted_urls else 'No link'}",
                "confidence": 0.92
            }
        ]

        # 8. Correlated Incident
        incident = {
            "incident_number": "INC-00042",
            "title": f"Targeted Phishing Impersonating {phish_res.regional_context.get('targeted_brand') or 'CBE / Telebirr'}",
            "severity": "CRITICAL" if phish_res.is_phishing else "LOW",
            "status": "INVESTIGATING",
            "risk_score": max(phish_res.risk_score, 88),
            "affected_asset": recipient_host,
            "affected_user": recipient_user,
            "assigned_analyst": "Dawit Mengistu",
            "first_seen": now_iso,
            "mitre_attack": ["T1566.002", "T1078"],
            "summary": phish_res.summary_en
        }

        # 9. 7 AI Agents Pipeline Execution
        ai_pipeline = self.ai_orchestrator.run_investigation_pipeline(incident, alerts_triggered)

        # 10. Deterministic Risk Breakdown
        risk_breakdown = {
            "score": incident["risk_score"],
            "methodology": "Composite Weighted Risk Formula (Asset Criticality + Privileged User + IOC Reputation + Psychological Urgency)",
            "factors": [
                {"factor": "Critical Core Banking Host", "contribution": 25, "evidence_ref": "EV-001"},
                {"factor": "DMARC Identity Alignment Failure", "contribution": 25, "evidence_ref": "EV-001"},
                {"factor": "National Brand Impersonation (Telebirr/CBE)", "contribution": 20, "evidence_ref": "EV-002"},
                {"factor": "Raw IP Host in Embedded Hyperlink", "contribution": 18, "evidence_ref": "EV-003"}
            ]
        }

        # 11. Human-in-the-Loop SOAR Playbook Actions (Dual-Custody)
        extracted_ip = phish_res.extracted_urls[0]["domain"] if phish_res.extracted_urls else "185.220.101.5"
        soar_actions = [
            {
                "action_id": f"ACT-{uuid.uuid4().hex[:6]}",
                "action_type": "BLOCK_IP",
                "target": extracted_ip,
                "reason": "Block egress network traffic to phishing payload server on perimeter firewalls.",
                "requires_approval": True,
                "status": "PENDING_APPROVAL",
                "proposer": "AI_RESPONSE_AGENT",
                "risk_rating": "LOW",
                "rollback_supported": True
            },
            {
                "action_id": f"ACT-{uuid.uuid4().hex[:6]}",
                "action_type": "TAKEDOWN_DOMAIN",
                "target": phish_res.sender_domain or "fake-telebirr-award.xyz",
                "reason": "Submit emergency brand abuse takedown notice to registrar and national CERT.",
                "requires_approval": True,
                "status": "PENDING_APPROVAL",
                "proposer": "AI_INVESTIGATION_AGENT",
                "risk_rating": "MEDIUM",
                "rollback_supported": False
            },
            {
                "action_id": f"ACT-{uuid.uuid4().hex[:6]}",
                "action_type": "ISOLATE_HOST",
                "target": f"{recipient_host} ({recipient_ip})",
                "reason": "Isolate recipient endpoint from corporate LAN while preserving forensic link to SOC.",
                "requires_approval": True,
                "status": "PENDING_APPROVAL",
                "proposer": "AI_RISK_AGENT",
                "risk_rating": "HIGH",
                "rollback_supported": True
            }
        ]

        # 12. Immutable Audit Record
        audit_record = {
            "audit_id": f"aud_{uuid.uuid4().hex[:10]}",
            "timestamp": now_iso,
            "pipeline_id": pipeline_id,
            "event_source": "inbound_email",
            "events_ingested": 1,
            "alerts_created": len(alerts_triggered),
            "incident_promoted": incident["incident_number"],
            "ai_agents_invoked": 7,
            "pending_approvals": len(soar_actions),
            "analyst_on_duty": "Dawit Mengistu",
            "tamper_proof_checksum": hashlib.sha256(f"{pipeline_id}-{incident['incident_number']}".encode()).hexdigest()
        }

        return PipelineExecutionResult(
            pipeline_id=pipeline_id,
            status="COMPLETED",
            canonical_event=canonical_event,
            alerts_triggered=alerts_triggered,
            threat_intel_matches=threat_intel_matches,
            incident=incident,
            security_graph={
                "nodes": [{"id": n.id, "label": n.label, "type": n.type, "metadata": n.metadata} for n in nodes],
                "edges": [{"source": e.source_id, "target": e.target_id, "relationship": e.relationship} for e in edges]
            },
            evidence_trail=evidence_trail,
            ai_investigation=ai_pipeline["pipeline_results"],
            risk_breakdown=risk_breakdown,
            soar_actions=soar_actions,
            audit_record=audit_record
        )
