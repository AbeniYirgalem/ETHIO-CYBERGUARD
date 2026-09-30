"""
Unit Tests for ETHIO-CYBERGUARD Modular API Endpoints
Verifies that all required /api/ endpoints respond with proper schema, status codes, and security.
"""

import pytest
pytest.importorskip("httpx")

from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_auth_login_and_register():
    # Login with valid demo credentials
    resp = client.post("/api/auth/login", json={
        "email": "analyst@cbe.com.et",
        "password": "Analyst@2026!"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["role"] == "SECURITY_ANALYST"

    # Register new user
    reg_resp = client.post("/api/auth/register", json={
        "email": "newanalyst@telebirr.et",
        "password": "SecurePassword@2026!",
        "full_name": "Almaz Bekele",
        "organization": "Ethio Telecom",
        "role": "SECURITY_ANALYST"
    })
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert reg_data["user"]["email"] == "newanalyst@telebirr.et"

def test_incidents_endpoints():
    # List incidents
    resp = client.get("/api/incidents")
    assert resp.status_code == 200
    data = resp.json()
    assert "incidents" in data
    assert len(data["incidents"]) >= 3

    # Query specific incident
    inc_id = data["incidents"][0]["incident_number"]
    detail_resp = client.get(f"/api/incidents/{inc_id}")
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert "incident" in detail_data
    assert "timeline" in detail_data
    assert "attack_graph" in detail_data

def test_phishing_analyze_endpoint():
    phishing_email = (
        "From: support@telebirr-bonus.xyz\n"
        "To: victim@cbe.com.et\n"
        "Subject: የቴሌብር 10,000 ብር ቦነስ ያረጋግጡ\n\n"
        "የቴሌብር ፒን ቁጥርዎን በ http://196.188.99.12/claim በማስገባት ሽልማቱን ያረጋግጡ።"
    )
    resp = client.post("/api/phishing/analyze", json={
        "raw_content": phishing_email
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_phishing"] is True
    assert data["risk_score"] > 80

def test_osint_scan_endpoint():
    resp = client.post("/api/osint/scan", json={
        "target": "ethiotelecom.et",
        "authorized": True
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["target"] == "ethiotelecom.et"
    assert "asn_info" in data
    assert "subdomains_discovered" in data
    assert "exposed_ports" in data

    # SSRF protection test
    ssrf_resp = client.post("/api/osint/scan", json={
        "target": "127.0.0.1",
        "authorized": True
    })
    assert ssrf_resp.status_code == 400

def test_typosquat_scan_endpoint():
    resp = client.post("/api/typosquat/scan", json={
        "target": "telebirr.et",
        "limit": 10
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "results" in data
    assert len(data["results"]) > 0

def test_threat_intel_ioc_endpoint():
    # Known malicious C2
    resp = client.get("/api/threat-intelligence/ioc/185.220.101.5")
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_malicious"] is True
    assert data["data"]["threat_actor"] == "APT-CobaltStrike-Cluster"

def test_ai_investigate_and_chat():
    inv_resp = client.post("/api/ai/investigate", json={
        "incident_number": "INC-00042"
    })
    assert inv_resp.status_code == 200
    inv_data = inv_resp.json()
    assert inv_data["orchestrator_status"] == "COMPLETED"
    assert inv_data["agents_executed"] == 7

    chat_resp = client.post("/api/ai/chat", json={
        "query": "Why was INC-00042 classified as critical?",
        "incident_number": "INC-00042"
    })
    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    assert "citations" in chat_data
    assert len(chat_data["citations"]) > 0

def test_dashboard_stats_endpoint():
    resp = client.get("/api/dashboard/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "metrics" in data
    assert data["metrics"]["events_per_second"] > 0
    assert "sector_profiles" in data

def test_response_endpoints():
    iso_resp = client.post("/api/response/isolate-host", json={
        "hostname": "SERVER-04",
        "reason": "Active C2 beaconing observed",
        "incident_number": "INC-00042"
    })
    assert iso_resp.status_code == 200
    act_id = iso_resp.json()["action_id"]

    # Approve action
    app_resp = client.post(f"/api/response/actions/{act_id}/approve", json={
        "reason": "Analyst verified Beacon signature"
    })
    assert app_resp.status_code == 200
    assert app_resp.json()["action"]["status"] == "APPROVED"

def test_reports_endpoints():
    rep_resp = client.get("/api/reports/incident/INC-00042")
    assert rep_resp.status_code == 200
    data = rep_resp.json()
    assert data["report_id"] == "REP-INC-00042"
    assert "compliance_alignment" in data

    csv_resp = client.get("/api/reports/incident/INC-00042?format=csv")
    assert csv_resp.status_code == 200
    assert "text/csv" in csv_resp.headers["content-type"]
