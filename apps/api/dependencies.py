import uuid
"""
ETHIO-CYBERGUARD Authentication Dependencies & Token Handling
Provides JWT token creation/verification, password hashing, token revocation, and role-based route guards.
Enforces fail-closed authentication in production environments.
"""

from fastapi import Depends, HTTPException, status, Header, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
import base64
import binascii
import json
import os
import threading
import uuid

from .config import (
    JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, 
    REFRESH_TOKEN_EXPIRE_DAYS, INGEST_API_KEY, DEMO_MODE,
    BOOTSTRAP_ADMIN_EMAIL, BOOTSTRAP_ADMIN_PASSWORD, REFRESH_REUSE_GRACE_SECONDS
)
from services.security.passwords import hash_password
from services.security.shared_state import get_shared_state
from database import state_store

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
# Seeded Demo Accounts (Role-Based Access)
DEMO_USERS: Dict[str, Dict[str, Any]] = {
    "admin@cbe.com.et": {
        "id": "usr_cbe_admin_01",
        "email": "admin@cbe.com.et",
        "name": "Dawit Mengistu",
        "role": "SUPER_ADMIN",
        "department": "Security Operations Center",
        "organization": "Commercial Bank of Ethiopia",
        "password_hash": hashlib.sha256("EthioCyber@2026!".encode("utf-8")).hexdigest()
    },
    "analyst@cbe.com.et": {
        "id": "usr_cbe_analyst_02",
        "email": "analyst@cbe.com.et",
        "name": "Sara Yohannes",
        "role": "SECURITY_ANALYST",
        "department": "Incident Triage",
        "organization": "Commercial Bank of Ethiopia",
        "password_hash": hashlib.sha256("Analyst@2026!".encode("utf-8")).hexdigest()
    },
    "commander@cbe.com.et": {
        "id": "usr_cbe_cmd_03",
        "email": "commander@cbe.com.et",
        "name": "Abebe Kebede",
        "role": "INCIDENT_COMMANDER",
        "department": "Executive Cyber Command",
        "organization": "Commercial Bank of Ethiopia",
        "password_hash": hashlib.sha256("Commander@2026!".encode("utf-8")).hexdigest()
    },
    "responder@cbe.com.et": {
        "id": "usr_cbe_resp_05",
        "email": "responder@cbe.com.et",
        "name": "Kidus Girma",
        "role": "INCIDENT_RESPONDER",
        "department": "Incident Response Unit",
        "organization": "Commercial Bank of Ethiopia",
        "password_hash": hashlib.sha256("Responder@2026!".encode("utf-8")).hexdigest()
    },
    "hunter@cbe.com.et": {
        "id": "usr_cbe_th_06",
        "email": "hunter@cbe.com.et",
        "name": "Yared Tadesse",
        "role": "THREAT_HUNTER",
        "department": "Threat Hunting & Detections",
        "organization": "Commercial Bank of Ethiopia",
        "password_hash": hashlib.sha256("Hunter@2026!".encode("utf-8")).hexdigest()
    },
    "auditor@cbe.com.et": {
        "id": "usr_cbe_audit_04",
        "email": "auditor@cbe.com.et",
        "name": "Tigist Haile",
        "role": "AUDITOR",
        "department": "Compliance & Forensics",
        "organization": "Commercial Bank of Ethiopia",
        "password_hash": hashlib.sha256("Auditor@2026!".encode("utf-8")).hexdigest()
    },
    "readonly@cbe.com.et": {
        "id": "usr_cbe_ro_07",
        "email": "readonly@cbe.com.et",
        "name": "Executive Observer",
        "role": "READ_ONLY",
        "department": "Executive Board",
        "organization": "Commercial Bank of Ethiopia",
        "password_hash": hashlib.sha256("ReadOnly@2026!".encode("utf-8")).hexdigest()
    }
}

# In-memory account lockout tracker: email -> {"failed_attempts": int, "lockout_until": datetime}
LOGIN_ATTEMPTS: Dict[str, Dict[str, Any]] = {}

# ---------------------------------------------------------------------------
# Session revocation (logout) and durable user accounts
# ---------------------------------------------------------------------------
# Every token carries a unique "jti". Logging out adds it to this list until the token's own
# expiry, so a stolen token stops working. The list is persisted so a restart cannot undo it.
REVOKED_TOKENS_STORE: List[Dict[str, Any]] = []   # [{"jti": str, "exp": float}]
_revoked_jtis: set = set()


def _prune_revoked() -> None:
    """Drop entries whose token has expired anyway and rebuild the lookup index."""
    now = datetime.now(timezone.utc).timestamp()
    REVOKED_TOKENS_STORE[:] = [e for e in REVOKED_TOKENS_STORE if float(e.get("exp", 0)) > now]
    _revoked_jtis.clear()
    _revoked_jtis.update(str(e["jti"]) for e in REVOKED_TOKENS_STORE if e.get("jti"))


def _ttl_until(exp: float) -> int:
    return max(1, int(exp - datetime.now(timezone.utc).timestamp()) + 1)


def is_token_revoked(payload: Dict[str, Any]) -> bool:
    jti = payload.get("jti")
    if not jti:
        return False
    if str(jti) in _revoked_jtis:
        return True
    # Another worker may have revoked it (only consulted when Redis is in use).
    shared = get_shared_state()
    return shared.distributed and shared.has_flag(f"jti:{jti}")


def revoke_token_payload(payload: Dict[str, Any]) -> bool:
    """Revoke an already-verified token payload. Returns True if it was newly revoked."""
    jti, exp = payload.get("jti"), payload.get("exp")
    if not jti or isinstance(exp, bool) or not isinstance(exp, (int, float)):
        return False
    if str(jti) in _revoked_jtis:
        return False
    REVOKED_TOKENS_STORE.append({"jti": str(jti), "exp": float(exp)})
    _prune_revoked()
    state_store.save("revoked_tokens")
    shared = get_shared_state()
    if shared.distributed:
        shared.set_flag(f"jti:{jti}", _ttl_until(float(exp)))
    return True


# ---------------------------------------------------------------------------
# Refresh-token rotation
# ---------------------------------------------------------------------------
# Every login starts a token "family" (claim "fid"). Each refresh issues a new refresh token in
# the same family and marks the old one as used. Presenting a used refresh token again means two
# parties hold it (a theft, or a replay): after a short grace window (two browser tabs refreshing
# at the same moment) the whole family is revoked, so the thief AND the victim must sign in again.
REFRESH_USED_STORE: List[Dict[str, Any]] = []       # [{"jti", "fid", "used_at", "exp"}]
REVOKED_FAMILIES_STORE: List[Dict[str, Any]] = []   # [{"fid", "exp"}]
_revoked_fids: set = set()
_used_refresh: Dict[str, float] = {}                 # jti -> used_at
_rotation_lock = threading.Lock()


def _prune_rotation() -> None:
    now = datetime.now(timezone.utc).timestamp()
    REFRESH_USED_STORE[:] = [e for e in REFRESH_USED_STORE if float(e.get("exp", 0)) > now]
    REVOKED_FAMILIES_STORE[:] = [e for e in REVOKED_FAMILIES_STORE if float(e.get("exp", 0)) > now]
    _used_refresh.clear()
    _used_refresh.update({str(e["jti"]): float(e.get("used_at", 0)) for e in REFRESH_USED_STORE if e.get("jti")})
    _revoked_fids.clear()
    _revoked_fids.update(str(e["fid"]) for e in REVOKED_FAMILIES_STORE if e.get("fid"))


def is_family_revoked(payload: Dict[str, Any]) -> bool:
    fid = payload.get("fid")
    if not fid:
        return False
    if str(fid) in _revoked_fids:
        return True
    shared = get_shared_state()
    return shared.distributed and shared.has_flag(f"fid:{fid}")


def revoke_family(payload: Dict[str, Any]) -> bool:
    """Revoke every token (access and refresh) that belongs to the payload's login family."""
    fid, exp = payload.get("fid"), payload.get("exp")
    if not fid or isinstance(exp, bool) or not isinstance(exp, (int, float)):
        return False
    with _rotation_lock:
        if str(fid) in _revoked_fids:
            return False
        # A family's longest-lived token is a refresh token, so keep the entry for the full refresh lifetime.
        keep_until = max(float(exp), datetime.now(timezone.utc).timestamp() + REFRESH_TOKEN_EXPIRE_DAYS * 86400)
        REVOKED_FAMILIES_STORE.append({"fid": str(fid), "exp": keep_until})
        _prune_rotation()
    state_store.save("revoked_families")
    shared = get_shared_state()
    if shared.distributed:
        shared.set_flag(f"fid:{fid}", _ttl_until(keep_until))
    return True


def consume_refresh_token(payload: Dict[str, Any], now: Optional[float] = None) -> str:
    """Mark a verified refresh token as used.

    Returns "ok" (first use), "grace" (second use inside the grace window: allowed) or
    "reuse" (used again after the window: the family has been revoked and the caller must reject).
    """
    jti, exp = payload.get("jti"), payload.get("exp")
    if not jti or isinstance(exp, bool) or not isinstance(exp, (int, float)):
        return "ok"
    current = datetime.now(timezone.utc).timestamp() if now is None else now
    shared = get_shared_state()
    used_at: Optional[float] = None  # None means "first use"
    if shared.distributed and not shared.set_once(f"used:{jti}", repr(current), _ttl_until(float(exp))):
        # Another request (possibly on another worker) already spent this token.
        try:
            used_at = float(shared.get_once(f"used:{jti}") or current)
        except ValueError:
            used_at = current
    with _rotation_lock:
        local_used_at = _used_refresh.get(str(jti))
        if used_at is None:
            used_at = local_used_at
        if local_used_at is None:
            REFRESH_USED_STORE.append(
                {"jti": str(jti), "fid": str(payload.get("fid") or ""), "used_at": current, "exp": float(exp)}
            )
            _prune_rotation()
    if local_used_at is None:
        state_store.save("refresh_used")
    if used_at is None:
        return "ok"
    if current - used_at <= REFRESH_REUSE_GRACE_SECONDS:
        return "grace"
    revoke_family(payload)
    return "reuse"


# User accounts live in DEMO_USERS (email -> user). They are saved after every change.
USERS_STORE: List[Dict[str, Any]] = []
_BOOTSTRAP_ADMIN_ID = "usr_bootstrap_admin"


def persist_users() -> None:
    state_store.save("users", list(DEMO_USERS.values()))


def restore_users(directory: Optional[Dict[str, Dict[str, Any]]] = None, demo_mode: Optional[bool] = None) -> int:
    """Merge saved users into the live directory. Returns how many were restored.

    * Default demo accounts are never resurrected from the database in production.
    * The bootstrap administrator always comes from the environment, never from the database.
    """
    target = DEMO_USERS if directory is None else directory
    demo = DEMO_MODE if demo_mode is None else demo_mode
    demo_ids = {account[1] for account in _DEMO_ACCOUNTS}
    restored = 0
    for user in USERS_STORE:
        email = str(user.get("email") or "").strip().lower()
        if not email or not user.get("password_hash"):
            continue
        if user.get("id") == _BOOTSTRAP_ADMIN_ID:
            continue
        if not demo and user.get("id") in demo_ids:
            continue
        target[email] = dict(user)
        restored += 1
    return restored


def _sync_revocations_to_shared() -> None:
    """Re-publish saved revocations to Redis (it may have been flushed or be brand new)."""
    shared = get_shared_state()
    if not shared.distributed:
        return
    for entry in REVOKED_TOKENS_STORE:
        shared.set_flag(f"jti:{entry['jti']}", _ttl_until(float(entry["exp"])))
    for entry in REVOKED_FAMILIES_STORE:
        shared.set_flag(f"fid:{entry['fid']}", _ttl_until(float(entry["exp"])))
    for entry in REFRESH_USED_STORE:
        shared.set_once(f"used:{entry['jti']}", repr(float(entry.get("used_at", 0))), _ttl_until(float(entry["exp"])))


def after_state_restore() -> None:
    """Called once at API startup, right after state_store.restore_all()."""
    restore_users()
    _prune_revoked()
    _prune_rotation()
    _sync_revocations_to_shared()


state_store.register("users", USERS_STORE)
state_store.register("revoked_tokens", REVOKED_TOKENS_STORE)
state_store.register("refresh_used", REFRESH_USED_STORE)
state_store.register("revoked_families", REVOKED_FAMILIES_STORE)
# In-memory Revoked Tokens Blacklist: set of SHA-256 hashes of revoked tokens
REVOKED_TOKENS: Set[str] = set()

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def revoke_token(token: str) -> None:
    """Adds a token's hash to the revocation blacklist."""
    if token:
        REVOKED_TOKENS.add(_hash_token(token))

def is_token_revoked(token: str) -> bool:
    """Checks if a token's hash is in the revocation blacklist."""
    return _hash_token(token) in REVOKED_TOKENS

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
    to_encode["jti"] = uuid.uuid4().hex
    
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
    to_encode["jti"] = uuid.uuid4().hex
    
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
    if is_token_revoked(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

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

    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    
    try:
        decoded_sig = _b64url_decode(sig_b64)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signature decoding failed")

    if not hmac.compare_digest(decoded_sig, expected_sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token signature verification failed")
    
    try:
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload JSON")

    if "exp" in payload and payload["exp"] < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    
    if payload.get("type", "access") != expected_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Expected {expected_type} token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if is_token_revoked(payload) or is_family_revoked(payload):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
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
        # In production mode, authentication is strictly required
        if not DEMO_MODE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required. Please provide a valid Bearer token.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        # Fallback to guest analyst ONLY in local demo sandbox mode
        return {
            "id": "usr_guest",
            "email": "analyst@cbe.com.et",
            "name": "Guest Analyst",
            "role": "SECURITY_ANALYST",
            "organization": "Commercial Bank of Ethiopia"
        }
    
    payload = verify_token(credentials.credentials, expected_type="access")
    user_email = payload.get("sub")
    known_user = DEMO_USERS.get(user_email)
    if known_user is not None:
        # A password reset bumps token_version, which retires every session issued before it.
        if int(payload.get("tv", 0) or 0) != int(known_user.get("token_version", 0) or 0):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session is no longer valid. Please sign in again.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return known_user

    if not DEMO_MODE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unknown account.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "id": payload.get("id", "usr_external"),
        "email": user_email,
        "name": payload.get("name", "Authenticated Analyst"),
        "role": payload.get("role", "SECURITY_ANALYST"),
        "organization": payload.get("organization", "Commercial Bank of Ethiopia")
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
    # In production, require either valid X-API-Key or valid Bearer token
    if x_api_key and x_api_key == INGEST_API_KEY:
        return True
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            verify_token(token)
            return True
        except Exception:
            pass
            
    # Demo sandbox fallback only if not in production and no credentials provided
    if DEMO_MODE and not x_api_key and not authorization:
        return True

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized collector. Valid X-API-Key or Bearer token required."
    )
