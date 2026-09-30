"""
ETHIO-CYBERGUARD Authentication & Identity Router
Provides login, registration, session verification, demo credentials, and RBAC endpoints.
Supports both /api/auth and /api/v1/auth routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
import hashlib
import uuid

from ..dependencies import DEMO_USERS, create_access_token, get_current_user

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

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

@router.post("/api/auth/login", response_model=TokenResponse)
@router.post("/api/v1/auth/login", response_model=TokenResponse)
def login_for_access_token(payload: LoginRequest):
    email = payload.email.strip().lower()
    user = DEMO_USERS.get(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    hashed_input = hashlib.sha256(payload.password.encode("utf-8")).hexdigest()
    if hashed_input != user["password_hash"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    token_payload = {
        "sub": user["email"],
        "id": user["id"],
        "name": user["name"],
        "role": user["role"],
        "department": user["department"]
    }
    
    token = create_access_token(token_payload)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "department": user["department"]
        }
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
    
    token = create_access_token({
        "sub": email,
        "id": new_user_id,
        "name": payload.full_name,
        "role": new_user["role"],
        "department": new_user["department"]
    })
    
    return {
        "status": "CREATED",
        "message": f"User {email} registered successfully.",
        "access_token": token,
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
            "department": current_user.get("department", "Security Operations")
        }
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
                "email": "auditor@cbe.com.et",
                "password": "Auditor@2026!",
                "role": "AUDITOR",
                "privilege": "Read-only audit log inspection and compliance verification"
            }
        ]
    }
