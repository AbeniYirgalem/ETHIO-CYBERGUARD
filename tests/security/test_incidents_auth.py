"""Incident routes: reads need a login, writes need incident:assign (production mode)."""

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
def readonly_headers():
    return _login("readonly@cbe.com.et", "ReadOnly@2026!")


READ_PATHS = [
    "/api/incidents",
    "/api/v1/incidents",
    "/api/incidents/INC-00042",
    "/api/incidents/INC-00042/comments",
    "/api/incidents/INC-00042/timeline",
]


@pytest.mark.parametrize("path", READ_PATHS)
def test_production_reads_require_login(production_mode, path):
    assert client.get(path).status_code == 401


def test_production_login_can_read_incidents(production_mode, admin_headers):
    resp = client.get("/api/incidents", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


def test_production_writes_require_login(production_mode):
    resp = client.post("/api/incidents/INC-00042/comments", json={"content": "x"})
    assert resp.status_code == 401
    resp = client.patch("/api/incidents/INC-00042", json={"summary": "x"})
    assert resp.status_code == 401


def test_read_only_user_can_read_but_not_write(production_mode, readonly_headers):
    assert client.get("/api/incidents", headers=readonly_headers).status_code == 200

    resp = client.post(
        "/api/incidents/INC-00042/comments",
        json={"content": "should be refused"},
        headers=readonly_headers,
    )
    assert resp.status_code == 403

    resp = client.patch(
        "/api/incidents/INC-00042",
        json={"summary": "tampered"},
        headers=readonly_headers,
    )
    assert resp.status_code == 403


def test_analyst_can_comment_in_production(production_mode):
    headers = _login("analyst@cbe.com.et", "Analyst@2026!")
    resp = client.post(
        "/api/incidents/INC-00042/comments",
        json={"content": "Reviewed by analyst"},
        headers=headers,
    )
    assert resp.status_code == 201


def test_demo_mode_guest_can_still_browse_incidents(monkeypatch):
    monkeypatch.setattr(dependencies, "DEMO_MODE", True)
    assert client.get("/api/incidents").status_code == 200
