"""
ETHIO-CYBERGUARD Authentication Dependencies & Token Handling
Provides JWT token creation/verification, password hashing, and role-based route guards.
"""

from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import base64
import json
import os

from .config import (
    JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, 
    REFRESH_TOKEN_EXPIRE_DAYS, INGEST_API_KEY, DEMO_MODE
)

security = HTTPBearer(auto_error=False)

# Standardized Enterprise Roles
ROLES = [
    "SUPER_ADMIN",
    "SOC_MANAGER",
    "SECURITY_ANALYST",
    "INCIDENT_RESPONDER",
    "THREAT_HUNTER",
    "AUDITOR",
    "READ_ONLY",
    # Backward compatibility alias
    "INCIDENT_COMMANDER"
]

ROLE_PERMISSIONS: Dict[str, List[str]] = {
    "SUPER_ADMIN": [
        "incident:assign", "evidence:delete", "rules:edit", "playbook:execute",
        "response:isolate_host", "response:block_ip", "user:admin", "data:export", "audit:read"
    ],
    "SOC_MANAGER": [
        "incident:assign", "rules:edit", "playbook:execute",
        "response:isolate_host", "response:block_ip", "data:export", "audit:read"
    ],
    "INCIDENT_COMMANDER": [
        "incident:assign", "rules:edit", "playbook:execute",
        "response:isolate_host", "response:block_ip", "data:export", "audit:read"
    ],
    "INCIDENT_RESPONDER": [
        "incident:assign", "playbook:execute", "response:isolate_host", "response:block_ip", "audit:read"
    ],
    "SECURITY_ANALYST": [
        "incident:assign", "playbook:execute", "data:export", "audit:read"
    ],
    "THREAT_HUNTER": [
        "rules:edit", "data:export", "audit:read"
    ],
    "AUDITOR": [
        "data:export", "audit:read"
    ],
    "READ_ONLY": [
        "audit:read"
    ]
}

# Seeded Demo Accounts (Role-Based Access)
DEMO_USERS: Dict[str, Dict[str, Any]] = {
    "admin@cbe.com.et": {
        "id": "usr_cbe_admin_01",
        "email": "admin@cbe.com.et",
        "name": "Dawit Mengistu",
        "role": "SUPER_ADMIN",
        "department": "Security Operations Center",
        "password_hash": hashlib.sha256("EthioCyber@2026!".encode("utf-8")).hexdigest()
    },
    "analyst@cbe.com.et": {
        "id": "usr_cbe_analyst_02",
        "email": "analyst@cbe.com.et",
        "name": "Sara Yohannes",
        "role": "SECURITY_ANALYST",
        "department": "Incident Triage",
        "password_hash": hashlib.sha256("Analyst@2026!".encode("utf-8")).hexdigest()
    },
    "commander@cbe.com.et": {
        "id": "usr_cbe_cmd_03",
        "email": "commander@cbe.com.et",
        "name": "Abebe Kebede",
        "role": "INCIDENT_COMMANDER",
        "department": "Executive Cyber Command",
        "password_hash": hashlib.sha256("Commander@2026!".encode("utf-8")).hexdigest()
    },
    "responder@cbe.com.et": {
        "id": "usr_cbe_resp_05",
        "email": "responder@cbe.com.et",
        "name": "Kidus Girma",
        "role": "INCIDENT_RESPONDER",
        "department": "Incident Response Unit",
        "password_hash": hashlib.sha256("Responder@2026!".encode("utf-8")).hexdigest()
    },
    "hunter@cbe.com.et": {
        "id": "usr_cbe_th_06",
        "email": "hunter@cbe.com.et",
        "name": "Yared Tadesse",
        "role": "THREAT_HUNTER",
        "department": "Threat Hunting & Detections",
        "password_hash": hashlib.sha256("Hunter@2026!".encode("utf-8")).hexdigest()
    },
    "auditor@cbe.com.et": {
        "id": "usr_cbe_audit_04",
        "email": "auditor@cbe.com.et",
        "name": "Tigist Haile",
        "role": "AUDITOR",
        "department": "Compliance & Forensics",
        "password_hash": hashlib.sha256("Auditor@2026!".encode("utf-8")).hexdigest()
    },
    "readonly@cbe.com.et": {
        "id": "usr_cbe_ro_07",
        "email": "readonly@cbe.com.et",
        "name": "Executive Observer",
        "role": "READ_ONLY",
        "department": "Executive Board",
        "password_hash": hashlib.sha256("ReadOnly@2026!".encode("utf-8")).hexdigest()
    }
}

# In-memory account lockout tracker: email -> {"failed_attempts": int, "lockout_until": datetime}
LOGIN_ATTEMPTS: Dict[str, Dict[str, Any]] = {}

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(data: str) -> bytes:
    padding = "=" * (4 - (len(data) % 4)) if len(data) % 4 != 0 else ""
    return base64.urlsafe_b64decode(data + padding)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = int(expire.timestamp())
    to_encode["type"] = "access"
    
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(to_encode).encode("utf-8"))
    
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode["exp"] = int(expire.timestamp())
    to_encode["type"] = "refresh"
    
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(to_encode).encode("utf-8"))
    
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_token(token: str, expected_type: str = "access") -> Dict[str, Any]:
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token structure")
    
    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    
    if not hmac.compare_digest(_b64url_decode(sig_b64), expected_sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signature verification failed")
    
    payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    if "exp" in payload and payload["exp"] < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    
    if payload.get("type", "access") != expected_type:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Expected {expected_type} token")
        
    return payload

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    if not credentials or not credentials.credentials:
        # Fallback to guest analyst for local dev / unauthenticated public views
        return {
            "id": "usr_guest",
            "email": "analyst@cbe.com.et",
            "name": "Guest Analyst",
            "role": "SECURITY_ANALYST"
        }
    
    payload = verify_token(credentials.credentials, expected_type="access")
    user_email = payload.get("sub")
    if user_email in DEMO_USERS:
        return DEMO_USERS[user_email]
    
    return {
        "id": payload.get("id", "usr_external"),
        "email": user_email,
        "name": payload.get("name", "Authenticated Analyst"),
        "role": payload.get("role", "SECURITY_ANALYST")
    }

def require_role(allowed_roles: List[str]):
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. User role {current_user.get('role')} is not authorized for this operation."
            )
        return current_user
    return role_checker

def require_permission(permission: str):
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        role = current_user.get("role", "READ_ONLY")
        permissions = ROLE_PERMISSIONS.get(role, [])
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Permission '{permission}' required."
            )
        return current_user
    return permission_checker

def verify_collector_api_key(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
) -> bool:
    """Verifies that an incoming ingestion event comes from an authenticated collector."""
    if DEMO_MODE:
        return True # Bypass in demo sandbox mode
    if x_api_key == INGEST_API_KEY:
        return True
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            verify_token(token)
            return True
        except Exception:
            pass
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized collector. Valid X-API-Key or Bearer token required."
    )
