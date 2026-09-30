import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.detection.engine import DetectionEngine

def test_powershell_obfuscation_rule():
    engine = DetectionEngine()
    event = {
        "event_id": "evt_test_ps",
        "source": { "hostname": "SERVER-04" },
        "process": {
            "name": "powershell.exe",
            "command_line": "powershell.exe -NoP -W Hidden -Enc SQBFAFgA"
        }
    }
    alerts = engine.evaluate_event(event)
    assert len(alerts) > 0
    ps_alert = next((a for a in alerts if "PowerShell" in a["title"]), None)
    assert ps_alert is not None
    assert ps_alert["severity"] == "CRITICAL"
    assert ps_alert["mitre_technique"] == "T1059.001 - PowerShell"

def test_threat_intel_match_rule():
    engine = DetectionEngine()
    event = {
        "event_id": "evt_test_ti",
        "source": { "hostname": "SERVER-04" },
        "network": { "destination_ip": "185.220.101.5" }
    }
    alerts = engine.evaluate_event(event)
    ti_alert = next((a for a in alerts if "Threat_Intel_IP_Match" in a["rule_name"]), None)
    assert ti_alert is not None
    assert ti_alert["confidence"] >= 95
