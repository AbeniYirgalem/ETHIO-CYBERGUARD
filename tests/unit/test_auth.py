import pytest
from apps.api.dependencies import (
    DEMO_USERS, 
    create_access_token, 
    verify_token, 
    require_role
)
from apps.api.routers.auth import login_for_access_token, LoginRequest
from fastapi import HTTPException

def test_token_creation_and_verification():
    user = DEMO_USERS["admin@cbe.com.et"]
    token = create_access_token({
        "sub": user["email"],
        "id": user["id"],
        "role": user["role"]
    })
    assert isinstance(token, str)
    assert len(token.split(".")) == 3

    payload = verify_token(token)
    assert payload["sub"] == "admin@cbe.com.et"
    assert payload["role"] == "SUPER_ADMIN"

def test_login_success():
    req = LoginRequest(email="analyst@cbe.com.et", password="Analyst@2026!")
    res = login_for_access_token(req)
    assert "access_token" in res
    assert res["user"]["email"] == "analyst@cbe.com.et"
    assert res["user"]["role"] == "SECURITY_ANALYST"

def test_login_invalid_password():
    req = LoginRequest(email="admin@cbe.com.et", password="WrongPassword123!")
    with pytest.raises(HTTPException) as exc:
        login_for_access_token(req)
    assert exc.value.status_code == 401

def test_role_checker_enforcement():
    checker = require_role(["SUPER_ADMIN", "INCIDENT_COMMANDER"])
    
    # Authorized user passes
    admin_user = {"email": "admin@cbe.com.et", "role": "SUPER_ADMIN"}
    assert checker(admin_user) == admin_user

    # Unauthorized role raises 403
    analyst_user = {"email": "analyst@cbe.com.et", "role": "SECURITY_ANALYST"}
    with pytest.raises(HTTPException) as exc:
        checker(analyst_user)
    assert exc.value.status_code == 403
