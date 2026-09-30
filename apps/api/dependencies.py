"""
ETHIO-CYBERGUARD Authentication Dependencies & Token Handling
Provides JWT token creation/verification, password hashing, and role-based route guards.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import base64
import json

from .config import JWT_SECRET, JWT_ALGORITHM

security = HTTPBearer(auto_error=False)

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
    "auditor@cbe.com.et": {
        "id": "usr_cbe_audit_04",
        "email": "auditor@cbe.com.et",
        "name": "Tigist Haile",
        "role": "AUDITOR",
        "department": "Compliance & Forensics",
        "password_hash": hashlib.sha256("Auditor@2026!".encode("utf-8")).hexdigest()
    }
}

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(data: str) -> bytes:
    padding = "=" * (4 - (len(data) % 4)) if len(data) % 4 != 0 else ""
    return base64.urlsafe_b64decode(data + padding)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=1))
    to_encode["exp"] = int(expire.timestamp())
    
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    header_b64 = _b64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(to_encode).encode("utf-8"))
    
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    
    return f"{header_b64}.{payload_b64}.{sig_b64}"

def verify_token(token: str) -> Dict[str, Any]:
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
    
    payload = verify_token(credentials.credentials)
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
