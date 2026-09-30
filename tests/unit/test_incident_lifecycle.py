import pytest
from services.incident.lifecycle import IncidentLifecycleManager

def test_incident_lifecycle_progression():
    mgr = IncidentLifecycleManager("INC-00099", "Lateral Movement on Core Banking", "CRITICAL")
    assert mgr.state == "NEW"

    mgr.assign_analyst("SEC-ETH-04", assigned_by="SUPERVISOR-01")
    assert mgr.assignee == "SEC-ETH-04"

    # Forward lifecycle transitions
    assert mgr.transition_to("TRIAGED", actor="SEC-ETH-04")
    assert mgr.transition_to("INVESTIGATING", actor="SEC-ETH-04")
    assert mgr.transition_to("CONTAINED", actor="SEC-ETH-04")
    assert mgr.transition_to("ERADICATED", actor="SEC-ETH-04")
    assert mgr.transition_to("RECOVERED", actor="SEC-ETH-04")
    assert mgr.transition_to("CLOSED", actor="SEC-ETH-04")
    assert mgr.state == "CLOSED"

    # Attempting invalid backwards transition should raise ValueError
    with pytest.raises(ValueError):
        mgr.transition_to("TRIAGED", actor="SEC-ETH-04")

def test_forensic_evidence_custody():
    mgr = IncidentLifecycleManager("INC-00100", "Cobalt Strike Memory Injection", "CRITICAL")
    
    raw_packet = "SYN/ACK from 185.220.101.5:443 to 10.10.1.24 payload=0x4d5a9000"
    ev = mgr.attach_evidence("pcap", "C2 Beacon Network Trace", raw_packet, collected_by="SEC-ETH-04")

    assert ev.evidence_id.startswith("EV-")
    assert len(ev.sha256) == 64
    assert len(mgr.evidence_items) == 1

    report = mgr.generate_post_incident_report()
    assert report["incident_id"] == "INC-00100"
    assert report["evidence_count"] == 1
    assert ev.sha256 in report["evidence_hashes"]
