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
import binascii
import json
import os

from .config import (
    JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, 
    REFRESH_TOKEN_EXPIRE_DAYS, INGEST_API_KEY, DEMO_MODE,
    BOOTSTRAP_ADMIN_EMAIL, BOOTSTRAP_ADMIN_PASSWORD
)
from services.security.passwords import hash_password

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
        "response:isolate_host", "response:block_ip", "response:approve",
        "user:admin", "data:export", "audit:read"
    ],
    "SOC_MANAGER": [
        "incident:assign", "rules:edit", "playbook:execute",
        "response:isolate_host", "response:block_ip", "response:approve",
        "data:export", "audit:read"
    ],
    "INCIDENT_COMMANDER": [
        "incident:assign", "rules:edit", "playbook:execute",
        "response:isolate_host", "response:block_ip", "response:approve",
        "data:export", "audit:read"
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

# Seeded demo accounts. Hashes are precomputed (salted PBKDF2-SHA256, 100k rounds) so
# importing this module is fast; the demo passwords are public in the README by design.
# These accounts exist ONLY when DEMO_MODE=true. Generate real hashes with:
#   python -m scripts.hash_password
_DEMO_ACCOUNTS = [
    ("admin@cbe.com.et", "usr_cbe_admin_01", "Dawit Mengistu", "SUPER_ADMIN", "Security Operations Center",
     "pbkdf2_sha256$100000$vHmcV8qK+kfrVNVgAqMw3w$WnSvjPr4Hgs31woMFAQ43jkuvDiJw/KnGTTU3kle0EI"),
    ("analyst@cbe.com.et", "usr_cbe_analyst_02", "Sara Yohannes", "SECURITY_ANALYST", "Incident Triage",
     "pbkdf2_sha256$100000$p7qtZXV0nHwgVeUfOalNVA$zdn6Duydctxse4A7Ch5cABmY6rPsp0EqGqVWNrNRroI"),
    ("commander@cbe.com.et", "usr_cbe_cmd_03", "Abebe Kebede", "INCIDENT_COMMANDER", "Executive Cyber Command",
     "pbkdf2_sha256$100000$byaoCOG8mqh06w+ooWXDLw$8x5ZXLkgLuss0LJyIGDdNz6tgai1fm8rv386Aa9Dxw4"),
    ("responder@cbe.com.et", "usr_cbe_resp_05", "Kidus Girma", "INCIDENT_RESPONDER", "Incident Response Unit",
     "pbkdf2_sha256$100000$ApDmV8dgi09s3KeksLSWuA$iXc5ZSQ3FFIkKywhtXqdQvh06ExyxzXZ+6uCwwO0R0Q"),
    ("hunter@cbe.com.et", "usr_cbe_th_06", "Yared Tadesse", "THREAT_HUNTER", "Threat Hunting & Detections",
     "pbkdf2_sha256$100000$yrEsvrpApVzi9Eorj2sh6A$ShidqO6bs6Hlfd8wQmlloIumoSnHrdRKVwtuMmbOCCA"),
    ("auditor@cbe.com.et", "usr_cbe_audit_04", "Tigist Haile", "AUDITOR", "Compliance & Forensics",
     "pbkdf2_sha256$100000$nrwIHo9LgqksHWXIMIzJWw$yYTflWlM4ZlgjqRur++E24/lmMNS9KiM+9xQpVMGOCs"),
    ("readonly@cbe.com.et", "usr_cbe_ro_07", "Executive Observer", "READ_ONLY", "Executive Board",
     "pbkdf2_sha256$100000$2ok9xqirNQoOrH3HJsof7w$Uh/vuWww2sQRNkj5vI4eundRqvPWCaO4nnTLMr6SM+A"),
]


def _build_user_directory(demo_mode: bool, bootstrap_email: str, bootstrap_password: str) -> Dict[str, Dict[str, Any]]:
    """Demo accounts only in demo mode; the bootstrap admin (if configured) in any mode."""
    users: Dict[str, Dict[str, Any]] = {}
    if demo_mode:
        for email, user_id, name, role, department, password_hash in _DEMO_ACCOUNTS:
            users[email] = {
                "id": user_id, "email": email, "name": name, "role": role,
                "department": department, "password_hash": password_hash,
            }
    if bootstrap_email and bootstrap_password:
        users[bootstrap_email] = {
            "id": "usr_bootstrap_admin",
            "email": bootstrap_email,
            "name": "Platform Administrator",
            "role": "SUPER_ADMIN",
            "department": "Security Operations Center",
            "password_hash": hash_password(bootstrap_password),
        }
    return users


DEMO_USERS: Dict[str, Dict[str, Any]] = _build_user_directory(
    DEMO_MODE, BOOTSTRAP_ADMIN_EMAIL, BOOTSTRAP_ADMIN_PASSWORD
)

# In-memory account lockout tracker: email -> {"failed_attempts": int, "lockout_until": datetime}
LOGIN_ATTEMPTS: Dict[str, Dict[str, Any]] = {}

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def _b64url_decode(data: str) -> bytes:
    """Decode a base64url JWT segment, rejecting invalid characters."""
    if not isinstance(data, str) or not data:
        raise ValueError("Empty JWT segment")
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.b64decode(data + padding, altchars=b"-_", validate=True)

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
    """Validate JWT structure, algorithm, signature, expiry, and token type.

    Invalid or malformed client tokens consistently produce HTTP 401 instead
    of leaking parsing exceptions as server errors.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not isinstance(token, str):
        raise unauthorized

    parts = token.split(".")
    if len(parts) != 3 or any(not part for part in parts):
        raise unauthorized

    header_b64, payload_b64, sig_b64 = parts
    try:
        header = json.loads(_b64url_decode(header_b64).decode("utf-8"))
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        supplied_signature = _b64url_decode(sig_b64)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError, binascii.Error):
        raise unauthorized

    # This implementation signs with HMAC-SHA256; never trust the token's
    # unverified algorithm field to choose a verification method.
    if not isinstance(header, dict) or header.get("alg") != JWT_ALGORITHM:
        raise unauthorized
    if header.get("typ", "JWT") != "JWT" or not isinstance(payload, dict):
        raise unauthorized

    signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
    expected_signature = hmac.new(
        JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    if not hmac.compare_digest(supplied_signature, expected_signature):
        raise unauthorized

    # Tokens minted by this application always contain exp. Reject tokens
    # without it or with an unexpected type rather than accepting them forever.
    expires_at = payload.get("exp")
    if isinstance(expires_at, bool) or not isinstance(expires_at, (int, float)):
        raise unauthorized
    if expires_at <= datetime.now(timezone.utc).timestamp():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type", "access") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Expected {expected_type} token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    if not credentials or not credentials.credentials:
        if not DEMO_MODE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # Demo sandbox only: unauthenticated visitors act as a low-privilege guest analyst
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
