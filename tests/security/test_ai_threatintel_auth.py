"""AI assistant and threat-intelligence routes: login required, IOC import needs rules:edit."""

import pytest
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api import dependencies

client = TestClient(app)


def _login(email: str, password: str):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def production_mode(monkeypatch):
    monkeypatch.setattr(dependencies, "DEMO_MODE", False)


@pytest.fixture(scope="module")
def analyst_headers():
    return _login("analyst@cbe.com.et", "Analyst@2026!")


GET_PATHS = [
    "/api/threat-intelligence",
    "/api/v1/threat-intelligence",
    "/api/threat-intelligence/ioc/185.220.101.5",
    "/api/threat-intelligence/stix",
    "/api/threat-intelligence/feeds",
    "/api/ai/agents",
]


@pytest.mark.parametrize("path", GET_PATHS)
def test_production_requires_login(production_mode, path):
    assert client.get(path).status_code == 401


def test_production_ai_chat_and_investigate_require_login(production_mode):
    assert client.post("/api/ai/chat", json={"query": "why is it critical?"}).status_code == 401
    assert client.post("/api/ai/investigate", json={"incident_number": "INC-00042"}).status_code == 401


def test_logged_in_analyst_can_use_assistant_and_threat_intel(production_mode, analyst_headers):
    chat = client.post(
        "/api/ai/chat",
        json={"query": "why is INC-00042 critical?", "incident_number": "INC-00042"},
        headers=analyst_headers,
    )
    assert chat.status_code == 200
    assert chat.json()["reply"]

    intel = client.get("/api/threat-intelligence", headers=analyst_headers)
    assert intel.status_code == 200
    assert intel.json()["total"] >= 1


def test_ioc_import_requires_rules_edit(production_mode, analyst_headers, admin_headers):
    body = {
        "indicator": "auth-test-phish.example",
        "ioc_type": "domain-name",
        "severity": "HIGH",
        "source": "Unit test",
        "confidence": 90,
        "expires_in_days": 7,
    }
    assert client.post("/api/threat-intelligence/import", json=body).status_code == 401
    assert client.post("/api/threat-intelligence/import", json=body, headers=analyst_headers).status_code == 403
    assert client.post("/api/threat-intelligence/import", json=body, headers=admin_headers).status_code == 201


def test_demo_mode_guest_can_still_read_threat_intel(monkeypatch):
    monkeypatch.setattr(dependencies, "DEMO_MODE", True)
    assert client.get("/api/threat-intelligence").status_code == 200
