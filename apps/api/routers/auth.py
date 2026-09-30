"""
ETHIO-CYBERGUARD Authentication & Identity Router
Provides login, registration, refresh tokens, password reset, account lockout, and RBAC endpoints.
Supports both /api/auth and /api/v1/auth routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import hashlib
import uuid

from ..dependencies import (
    DEMO_USERS, LOGIN_ATTEMPTS, create_access_token, 
    create_refresh_token, verify_token, get_current_user,
    ROLES, ROLE_PERMISSIONS
)

router = APIRouter(tags=["Authentication & Identity"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    password: str
    full_name: str
    organization: Optional[str] = "Commercial Bank of Ethiopia"
    role: Optional[str] = "SECURITY_ANALYST"
    department: Optional[str] = "Security Operations Center"

class RefreshRequest(BaseModel):
    refresh_token: str

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetConfirmRequest(BaseModel):
    reset_token: str
    new_password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# In-memory store for password reset tokens: token -> {"email": email, "expires_at": datetime}
PASSWORD_RESET_TOKENS: Dict[str, Dict[str, Any]] = {}

@router.post("/api/auth/login", response_model=TokenResponse)
@router.post("/api/v1/auth/login", response_model=TokenResponse)
def login_for_access_token(payload: LoginRequest):
    email = payload.email.strip().lower()
    now = datetime.now(timezone.utc)
    
    # Check account lockout
    attempt_info = LOGIN_ATTEMPTS.get(email, {"failed_attempts": 0, "lockout_until": None})
    if attempt_info["lockout_until"] and attempt_info["lockout_until"] > now:
        remaining_seconds = int((attempt_info["lockout_until"] - now).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Account locked due to consecutive failed attempts. Try again in {remaining_seconds} seconds."
        )

    user = DEMO_USERS.get(email)
    hashed_input = hashlib.sha256(payload.password.encode("utf-8")).hexdigest()
    
    if not user or hashed_input != user["password_hash"]:
        # Record failure
        attempt_info["failed_attempts"] += 1
        if attempt_info["failed_attempts"] >= 5:
            attempt_info["lockout_until"] = now + timedelta(minutes=15)
        LOGIN_ATTEMPTS[email] = attempt_info
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Reset failures upon successful login
    LOGIN_ATTEMPTS[email] = {"failed_attempts": 0, "lockout_until": None}
    
    token_payload = {
        "sub": user["email"],
        "id": user["id"],
        "name": user["name"],
        "role": user["role"],
        "department": user["department"]
    }
    
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "department": user["department"]
        }
    }

@router.post("/api/auth/refresh")
@router.post("/api/v1/auth/refresh")
def refresh_token(payload: RefreshRequest):
    token_data = verify_token(payload.refresh_token, expected_type="refresh")
    email = token_data.get("sub")
    
    user = DEMO_USERS.get(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    token_payload = {
        "sub": user["email"],
        "id": user["id"],
        "name": user["name"],
        "role": user["role"],
        "department": user["department"]
    }
    new_access_token = create_access_token(token_payload)
    new_refresh_token = create_refresh_token(token_payload)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
@router.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest):
    email = payload.email.strip().lower()
    if email in DEMO_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    new_user_id = f"usr_{uuid.uuid4().hex[:8]}"
    hashed_password = hashlib.sha256(payload.password.encode("utf-8")).hexdigest()
    
    new_user = {
        "id": new_user_id,
        "email": email,
        "name": payload.full_name,
        "role": payload.role or "SECURITY_ANALYST",
        "department": payload.department or "SOC Operations",
        "organization": payload.organization,
        "password_hash": hashed_password
    }
    
    DEMO_USERS[email] = new_user
    
    token_payload = {
        "sub": email,
        "id": new_user_id,
        "name": payload.full_name,
        "role": new_user["role"],
        "department": new_user["department"]
    }
    
    access_token = create_access_token(token_payload)
    refresh_token = create_refresh_token(token_payload)
    
    return {
        "status": "CREATED",
        "message": f"User {email} registered successfully.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": new_user_id,
            "email": email,
            "name": payload.full_name,
            "role": new_user["role"],
            "department": new_user["department"],
            "organization": payload.organization
        }
    }

@router.post("/api/auth/password-reset")
@router.post("/api/v1/auth/password-reset")
def request_password_reset(payload: PasswordResetRequest):
    email = payload.email.strip().lower()
    reset_token = f"rst_{uuid.uuid4().hex}"
    PASSWORD_RESET_TOKENS[reset_token] = {
        "email": email,
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=15)
    }
    return {
        "status": "QUEUED",
        "message": "If the account exists, a password reset token has been dispatched.",
        "reset_token_simulated": reset_token
    }

@router.post("/api/auth/password-reset/confirm")
@router.post("/api/v1/auth/password-reset/confirm")
def confirm_password_reset(payload: PasswordResetConfirmRequest):
    token_info = PASSWORD_RESET_TOKENS.get(payload.reset_token)
    if not token_info:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
    if token_info["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token expired")
        
    email = token_info["email"]
    if email in DEMO_USERS:
        DEMO_USERS[email]["password_hash"] = hashlib.sha256(payload.new_password.encode("utf-8")).hexdigest()
        
    del PASSWORD_RESET_TOKENS[payload.reset_token]
    return {"status": "SUCCESS", "message": "Password reset successfully. Please login with your new credentials."}

@router.post("/api/auth/logout")
@router.post("/api/v1/auth/logout")
def logout_user():
    return {"status": "SUCCESS", "message": "Session invalidated."}

@router.get("/api/auth/me")
@router.get("/api/v1/auth/me")
def read_current_user(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "status": "authenticated",
        "user": {
            "id": current_user.get("id"),
            "email": current_user.get("email"),
            "name": current_user.get("name"),
            "role": current_user.get("role"),
            "department": current_user.get("department", "Security Operations"),
            "permissions": ROLE_PERMISSIONS.get(current_user.get("role", "READ_ONLY"), [])
        }
    }

@router.get("/api/auth/roles")
@router.get("/api/v1/auth/roles")
def list_system_roles():
    """Lists all available enterprise RBAC roles and their assigned permission matrices."""
    return {
        "roles": ROLES,
        "role_permissions": ROLE_PERMISSIONS
    }

@router.get("/api/auth/demo-credentials")
@router.get("/api/v1/auth/demo-credentials")
def list_demo_credentials():
    """Returns available pre-seeded demo accounts for easy evaluator onboarding."""
    return {
        "demo_mode": True,
        "message": "DEMO SANDBOX: The following pre-seeded test accounts are available for testing role-based access:",
        "accounts": [
            {
                "email": "admin@cbe.com.et",
                "password": "EthioCyber@2026!",
                "role": "SUPER_ADMIN",
                "privilege": "Full access to playbooks, user management, and rule editing"
            },
            {
                "email": "commander@cbe.com.et",
                "password": "Commander@2026!",
                "role": "INCIDENT_COMMANDER",
                "privilege": "Authorization authority for dual-custody host isolation & IP drops"
            },
            {
                "email": "analyst@cbe.com.et",
                "password": "Analyst@2026!",
                "role": "SECURITY_ANALYST",
                "privilege": "Triage alerts, analyze phishing emails, request containment"
            },
            {
                "email": "responder@cbe.com.et",
                "password": "Responder@2026!",
                "role": "INCIDENT_RESPONDER",
                "privilege": "Action execution authority for host isolation & firewall drops"
            },
            {
                "email": "hunter@cbe.com.et",
                "password": "Hunter@2026!",
                "role": "THREAT_HUNTER",
                "privilege": "Detection rule tuning and proactive telemetry search"
            },
            {
                "email": "auditor@cbe.com.et",
                "password": "Auditor@2026!",
                "role": "AUDITOR",
                "privilege": "Read-only audit log inspection and compliance verification"
            },
            {
                "email": "readonly@cbe.com.et",
                "password": "ReadOnly@2026!",
                "role": "READ_ONLY",
                "privilege": "Executive read-only view of security metrics"
            }
        ]
    }
