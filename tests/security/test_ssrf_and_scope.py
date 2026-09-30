"""
Security Tests: SSRF Prevention and Scope Restrictions on Recon Tools
"""

import pytest
from fastapi import HTTPException
from apps.api.routers.osint import validate_target_scope

def test_ssrf_disallowed_targets():
    dangerous_targets = [
        "localhost", "127.0.0.1", "0.0.0.0", "169.254.169.254",
        "10.10.1.5", "172.16.0.1", "192.168.1.1"
    ]

    for target in dangerous_targets:
        with pytest.raises(HTTPException) as excinfo:
            validate_target_scope(target)
        assert excinfo.value.status_code == 400
        assert "private or reserved" in excinfo.value.detail

def test_ssrf_allowed_targets():
    # Valid external targets should not raise an exception
    validate_target_scope("ethiotelecom.et")
    validate_target_scope("combanketh.et")
    validate_target_scope("telebirr.et")
