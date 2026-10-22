"""
Pytest Central Configuration & Fixtures for ETHIO-CYBERGUARD Test Suite
"""

import pytest
from typing import Dict, Any

@pytest.fixture
def mock_analyst_user() -> Dict[str, Any]:
    return {
        "id": "usr_test_analyst_01",
        "email": "analyst@cbe.com.et",
        "name": "Sara Yohannes",
        "role": "SECURITY_ANALYST",
        "org_id": "org_cbe_01",
        "organization": "Commercial Bank of Ethiopia"
    }

@pytest.fixture
def mock_commander_user() -> Dict[str, Any]:
    return {
        "id": "usr_test_cmd_02",
        "email": "commander@cbe.com.et",
        "name": "Dawit Mengistu",
        "role": "INCIDENT_COMMANDER",
        "org_id": "org_cbe_01",
        "organization": "Commercial Bank of Ethiopia"
    }

@pytest.fixture
def sample_telebirr_phish() -> str:
    return (
        "From: \"Telebirr Bonus\" <support@telebirr-bonus.xyz>\n"
        "To: victim@cbe.com.et\n"
        "Subject: እንኳን ደስ አሎት! የ10,000 ብር የቴሌብር ቦነስ አሸንፈዋል\n"
        "Received-SPF: fail\n"
        "Authentication-Results: spf=fail; dkim=fail; dmarc=fail\n\n"
        "ሽልማቱን ለመውሰድ የቴሌብር ፒን ቁጥርዎን በ http://196.188.99.12/claim ያረጋግጡ።"
    )

@pytest.fixture
def sample_benign_email() -> str:
    return (
        "From: \"IT Support\" <support@cbe.com.et>\n"
        "To: employee@cbe.com.et\n"
        "Subject: Monthly Security Awareness Newsletter - October 2026\n"
        "Received-SPF: pass\n"
        "Authentication-Results: spf=pass; dkim=pass; dmarc=pass\n\n"
        "Dear Team, please review the cybersecurity best practices for this month."
    )

@pytest.fixture
def sample_ecs_powershell_event() -> Dict[str, Any]:
    return {
        "event_id": "evt_sample_ps_001",
        "timestamp": "2026-09-30 10:42:00+03:00",
        "source": {"hostname": "SERVER-04", "ip": "10.10.1.24"},
        "event_type": "process_execution",
        "severity": "CRITICAL",
        "user": "administrator",
        "process": {
            "name": "powershell.exe",
            "command_line": "powershell.exe -NoP -NonI -W Hidden -Enc SQBFAFgA"
        }
    }


# ---------------------------------------------------------------------------
# Authenticated API headers (SOAR routes reject the unauthenticated guest user)
# ---------------------------------------------------------------------------

def _login_headers(email: str, password: str) -> Dict[str, str]:
    from fastapi.testclient import TestClient
    from apps.api.main import app

    resp = TestClient(app).post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Demo login failed for {email}: {resp.text}"
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture(scope="session")
def admin_headers() -> Dict[str, str]:
    """Bearer headers for SUPER_ADMIN (all permissions)."""
    return _login_headers("admin@cbe.com.et", "EthioCyber@2026!")


@pytest.fixture(scope="session")
def commander_headers() -> Dict[str, str]:
    """Bearer headers for INCIDENT_COMMANDER (isolate, block, approve)."""
    return _login_headers("commander@cbe.com.et", "Commander@2026!")


@pytest.fixture(scope="session")
def responder_headers() -> Dict[str, str]:
    """Bearer headers for INCIDENT_RESPONDER (can request actions, cannot approve)."""
    return _login_headers("responder@cbe.com.et", "Responder@2026!")
