import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.ingestion.normalizer import EventNormalizer
from services.detection.engine import DetectionEngine
from services.correlation.correlator import CorrelationEngine
from services.ai.orchestrator import MultiAgentOrchestrator

def test_full_incident_pipeline():
    normalizer = EventNormalizer()
    detection = DetectionEngine()
    correlator = CorrelationEngine()
    orchestrator = MultiAgentOrchestrator()

    # 1. Ingest Raw Event
    raw = {
        "event_uid": "int_test_01",
        "timestamp": "2026-09-30T10:42:21Z",
        "source": { "hostname": "SERVER-04", "ip": "10.10.1.24" },
        "event_type": "process_execution",
        "user": "administrator",
        "process": { "name": "powershell.exe", "command_line": "powershell.exe -enc SQBFAFgA" },
        "network": { "destination_ip": "185.220.101.5" }
    }
    normalized = normalizer.normalize(raw)
    assert normalized["event_id"] == "int_test_01"

    # 2. Detect Alerts
    alerts = detection.evaluate_event(normalized)
    assert len(alerts) >= 2 # PowerShell rule + Threat Intel match

    # 3. Correlate Incident
    incident = correlator.correlate_alerts(alerts, asset_name="SERVER-04")
    assert incident["severity"] == "CRITICAL"
    assert incident["risk_score"] >= 90
    assert len(incident["timeline"]) >= 7
    assert len(incident["attack_graph"]["nodes"]) >= 5

    # 4. Run Multi-Agent AI Investigation
    investigation = orchestrator.run_investigation_pipeline(incident, [normalized])
    assert investigation["agents_executed"] == 7
    assert investigation["pipeline_results"]["investigation"]["findings"]["what_happened"] is not None
