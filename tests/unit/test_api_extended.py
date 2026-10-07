"""
Extended Unit Tests for ETHIO-CYBERGUARD API Routers and WebSocket Manager
Validates remaining endpoints, error paths, and response actions.
"""

import pytest
from io import BytesIO
from fastapi.testclient import TestClient
from apps.api.main import app
from services.websocket.manager import ChannelSubscriptionManager

client = TestClient(app)

def test_response_extended_endpoints():
    # 1. List actions
    actions_res = client.get("/api/v1/response/actions")
    assert actions_res.status_code == 200
    assert "actions" in actions_res.json()

    # 2. Block IP (dry run simulation)
    block_dry = client.post("/api/v1/response/block-ip", json={
        "ip_address": "198.51.100.44",
        "reason": "Suspected scanner",
        "incident_number": "INC-00042",
        "dry_run": True
    })
    assert block_dry.status_code == 200
    assert block_dry.json()["status"] == "SIMULATED"

    # 3. Block IP (real request queued)
    block_live = client.post("/api/v1/response/block-ip", json={
        "ip_address": "198.51.100.45",
        "reason": "Active brute-force attacker",
        "incident_number": "INC-00042",
        "require_approval": True,
        "dry_run": False
    })
    assert block_live.status_code == 200
    live_act_id = block_live.json()["action_id"]

    # 4. Reject live action
    reject_res = client.post(f"/api/v1/response/actions/{live_act_id}/reject", json={
        "reason": "Whitelisted partner IP",
        "operator": "Senior Analyst"
    })
    assert reject_res.status_code == 200
    assert reject_res.json()["action"]["status"] == "REJECTED"

    # 5. Disable account
    disable_res = client.post("/api/v1/response/disable-account", json={
        "username": "compromised.user",
        "domain": "cbe.internal",
        "reason": "Credential stuffing detected",
        "incident_number": "INC-00042",
        "require_approval": False
    })
    assert disable_res.status_code == 200
    disable_act_id = disable_res.json()["action_id"]
    assert disable_res.json()["action"]["status"] == "APPROVED"

    # 6. Rollback approved action
    rollback_res = client.post(f"/api/v1/response/actions/{disable_act_id}/rollback", json={
        "reason": "Identity verified, user unlocked",
        "operator": "Incident Commander"
    })
    assert rollback_res.status_code == 200
    assert rollback_res.json()["action"]["status"] == "ROLLED_BACK"

    # 7. Non-existent action rejection 404
    err_404 = client.post("/api/v1/response/actions/ACT-INVALID-999/reject", json={
        "reason": "test"
    })
    assert err_404.status_code == 404

    # 8. Audit logs retrieval
    audit_res = client.get("/api/v1/response/audit-log")
    assert audit_res.status_code == 200
    assert "audit_logs" in audit_res.json()

def test_phishing_upload_and_url_extraction():
    # 1. URL extraction
    extract_res = client.post("/api/phishing/extract-urls", json={
        "urls": [
            "http://192.168.1.50/admin",
            "https://telebirr-bonus.top/claim",
            "https://official.telebirr.et/news"
        ]
    })
    assert extract_res.status_code == 200
    data = extract_res.json()
    assert data["urls_inspected"] == 3
    assert data["results"][0]["is_ip_based"] is True
    assert data["results"][1]["suspicious"] is True

    # 2. Upload EML file (Valid)
    eml_bytes = (
        b"From: attacker@fake-cbe.com\n"
        b"To: victim@combanketh.et\n"
        b"Subject: Urgent Account Verification\n\n"
        b"Please click http://103.20.10.5/login to update your PIN."
    )
    upload_res = client.post(
        "/api/phishing/upload-eml",
        files={"file": ("sample.eml", BytesIO(eml_bytes), "message/rfc822")}
    )
    assert upload_res.status_code == 200
    assert upload_res.json()["filename"] == "sample.eml"
    assert "analysis" in upload_res.json()

    # 3. Upload invalid file extension (400 rejection)
    bad_upload = client.post(
        "/api/phishing/upload-eml",
        files={"file": ("malware.exe", BytesIO(b"MZ..."), "application/octet-stream")}
    )
    assert bad_upload.status_code == 400

def test_threat_intel_extended_endpoints():
    # 1. Filter indicators by type and reputation
    filtered_res = client.get("/api/v1/threat-intelligence?type=ipv4-addr&reputation=MALICIOUS")
    assert filtered_res.status_code == 200
    assert "indicators" in filtered_res.json()

    # 2. Unknown IOC lookup
    unknown_res = client.get("/api/v1/threat-intelligence/ioc/192.0.2.1")
    assert unknown_res.status_code == 200
    assert unknown_res.json()["is_malicious"] is False
    assert unknown_res.json()["reputation"] == "UNKNOWN"

    # 3. List threat feeds
    feeds_res = client.get("/api/v1/threat-intelligence/feeds")
    assert feeds_res.status_code == 200
    assert len(feeds_res.json()["feeds"]) >= 3

    # 4. Import new indicator
    import_res = client.post("/api/v1/threat-intelligence/import", json={
        "indicator": "suspicious-bank-login.xyz",
        "ioc_type": "domain-name",
        "severity": "HIGH",
        "source": "Ethio-CERT Flash Alert",
        "confidence": 95,
        "expires_in_days": 30
    })
    assert import_res.status_code == 201
    assert import_res.json()["status"] == "IMPORTED"

def test_reports_extended_endpoints():
    # 1. Compliance status report
    comp_res = client.get("/api/reports/compliance")
    assert comp_res.status_code == 200
    assert "frameworks" in comp_res.json()

    # 2. Executive report
    exec_res = client.get("/api/reports/executive")
    assert exec_res.status_code == 200
    assert "overall_security_index" in exec_res.json()

    # 3. Incident report 404 for non-existent incident
    missing_inc = client.get("/api/reports/incident/INC-DOES-NOT-EXIST")
    assert missing_inc.status_code == 404

@pytest.mark.anyio
async def test_websocket_channel_subscription_manager():
    mgr = ChannelSubscriptionManager(max_connections=2)
    assert mgr.get_active_count() == 0

    class MockWebSocket:
        def __init__(self):
            self.accepted = False
            self.closed = False
            self.messages = []

        async def accept(self):
            self.accepted = True

        async def close(self, code=1000, reason=""):
            self.closed = True

        async def send_json(self, msg):
            self.messages.append(msg)

    ws1 = MockWebSocket()
    ws2 = MockWebSocket()
    ws3 = MockWebSocket()

    # Connect ws1
    connected1 = await mgr.connect(ws1, {"organization": "CBE", "role": "ANALYST"})
    assert connected1 is True
    assert ws1.accepted is True
    assert mgr.get_active_count() == 1

    # Connect ws2
    connected2 = await mgr.connect(ws2, {"organization": "Telebirr", "role": "OPERATOR"})
    assert connected2 is True
    assert mgr.get_active_count() == 2

    # Connect ws3 exceeds max_connections=2
    connected3 = await mgr.connect(ws3, {"organization": "INSA", "role": "ANALYST"})
    assert connected3 is False
    assert ws3.closed is True

    # Subscribe to custom channel
    mgr.subscribe(ws1, "telemetry")
    assert ws1 in mgr.channel_subscribers["telemetry"]

    # Broadcast to specific channel
    await mgr.broadcast_to_channel("telemetry", {"type": "EPS_BURST", "rate": 4500})
    assert len(ws1.messages) == 1
    assert ws1.messages[0]["type"] == "EPS_BURST"
    assert len(ws2.messages) == 0

    # Broadcast to all
    await mgr.broadcast({"type": "GLOBAL_STATUS", "status": "HEALTHY"})
    assert len(ws1.messages) == 2
    assert len(ws2.messages) == 1

    # Disconnect
    mgr.disconnect(ws1)
    assert mgr.get_active_count() == 1
    mgr.disconnect(ws2)
    assert mgr.get_active_count() == 0
