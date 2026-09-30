import pytest
import sys
import os

# Add root directory to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.ingestion.normalizer import EventNormalizer

def test_event_normalizer_basic():
    normalizer = EventNormalizer()
    raw = {
        "event_uid": "test_001",
        "timestamp": "2026-09-30T10:00:00Z",
        "source": { "hostname": "SERVER-04", "ip": "10.10.1.24" },
        "event_type": "process_execution",
        "severity": "CRITICAL",
        "user": "administrator",
        "process": { "name": "powershell.exe", "command_line": "powershell.exe -enc AAA" }
    }

    norm = normalizer.normalize(raw)
    assert norm["event_id"] == "test_001"
    assert norm["severity"] == "CRITICAL"
    assert norm["enrichment"]["is_internal_network"] is True
    assert norm["source"]["hostname"] == "SERVER-04"

def test_event_normalizer_geo_enrichment():
    normalizer = EventNormalizer()
    raw = {
        "event_type": "network_connection",
        "network": { "destination_ip": "197.156.70.1" }
    }
    norm = normalizer.normalize(raw)
    assert norm["enrichment"]["geo_location"]["country"] == "Ethiopia"
    assert norm["enrichment"]["geo_location"]["city"] == "Addis Ababa"
