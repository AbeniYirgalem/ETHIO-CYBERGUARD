"""
Integration test for the Unified Security Pipeline & Common Security Graph
Verifies: Ingestion -> ECS Normalization -> SIGMA Rules -> Common Security Graph ->
Threat Intel -> 7 AI Agents -> Evidence Grounding -> SOAR Human Approval -> Audit.
"""

from services.pipeline.unified_engine import UnifiedPipelineEngine


def test_unified_pipeline_end_to_end_vertical_slice():
    pipeline = UnifiedPipelineEngine()

    sample_phish_raw = """From: "Telebirr Support" <support@telebirr-bonus.xyz>
To: dawit.mengistu@cbe.com.et
Reply-To: phisher-collector@gmail.com
Subject: URGENT: ቴሌብር 10,000 ብር የሽልማት አሸናፊ - አሁኑኑ ያረጋግጡ
Received-SPF: fail (domain telebirr-bonus.xyz does not match sender IP 196.188.99.12)
Authentication-Results: mx.ethiotelecom.et; spf=fail; dkim=fail; dmarc=fail

እንኳን ደስ አሎት! በብሔራዊ የዲጂታል ክፍያ ማበረታቻ ፕሮግራም የ10,000 ብር የቴሌብር ቦነስ አሸንፈዋል።
ሽልማቱን በቀጥታ ወደ አካውንትዎ ለማስገባት በ24 ሰዓት ውስጥ ይህን ይጫኑና የቴሌብር ፒን (PIN / OTP) ቁጥርዎን ያረጋግጡ፡
http://196.188.99.12/claim-prize/telebirr-login.php
"""

    result = pipeline.process_phishing_event_to_incident(
        raw_email=sample_phish_raw,
        recipient_user="dawit.mengistu@cbe.com.et",
        recipient_host="SERVER-04",
        recipient_ip="10.10.1.24"
    )

    # 1. Pipeline execution status
    assert result.status == "COMPLETED"
    assert result.pipeline_id.startswith("pipe_")

    # 2. Canonical ECS Event validation
    assert result.canonical_event["source"]["type"] == "email_gateway"
    assert result.canonical_event["event_type"] == "phishing_email_received"
    assert result.canonical_event["user"]["email"] == "dawit.mengistu@cbe.com.et"
    assert len(result.canonical_event["observables"]) >= 2

    # 3. Detection Engine & Alerts
    assert len(result.alerts_triggered) >= 1
    assert any("attack.initial_access" in a["tags"] for a in result.alerts_triggered)

    # 4. Common Security Graph
    assert len(result.security_graph["nodes"]) >= 4
    assert len(result.security_graph["edges"]) >= 3
    node_types = [n["type"] for n in result.security_graph["nodes"]]
    assert "Incident" in node_types
    assert "User" in node_types
    assert "Host" in node_types
    assert "Domain" in node_types

    # 5. Evidence Grounding
    assert len(result.evidence_trail) >= 3
    for ev in result.evidence_trail:
        assert ev["evidence_id"].startswith("EV-")
        assert ev["confidence"] > 0.8

    # 6. Multi-Agent AI Investigation
    assert "investigation" in result.ai_investigation
    assert "risk_assessment" in result.ai_investigation
    assert "reports" in result.ai_investigation

    # 7. Deterministic Risk Breakdown
    assert result.risk_breakdown["score"] >= 80
    assert len(result.risk_breakdown["factors"]) >= 3

    # 8. Human-Approved SOAR Containment Actions (Dual-Custody)
    assert len(result.soar_actions) >= 2
    for act in result.soar_actions:
        assert act["requires_approval"] is True
        assert act["status"] == "PENDING_APPROVAL"

    # 9. Audit Logging
    assert result.audit_record["incident_promoted"] == "INC-00042"
    assert len(result.audit_record["tamper_proof_checksum"]) == 64
