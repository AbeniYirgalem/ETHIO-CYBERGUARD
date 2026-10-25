"""
ETHIO-CYBERGUARD Authentication Router
Provides login, admin-only user creation, refresh tokens, password reset, account lockout, and RBAC endpoints.
Supports both /api/auth and /api/v1/auth routes.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import hashlib
import logging
import re
import secrets
import uuid

from ..config import DEMO_MODE, PASSWORD_RESET_ENABLED, REFRESH_REUSE_GRACE_SECONDS
from ..dependencies import (
    DEMO_USERS, LOGIN_ATTEMPTS, create_access_token,
    create_refresh_token, verify_token, get_current_user, require_permission,
    revoke_token_payload, revoke_family, consume_refresh_token, persist_users, security,
    ROLES, ROLE_PERMISSIONS
)
from services.security.passwords import hash_password, verify_password, validate_password_policy

logger = logging.getLogger("ecg.auth")

router = APIRouter(tags=["Authentication & Identity"])

_EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]+\.[^@\s]+$")
_RESET_TTL = timedelta(minutes=15)
_MAX_LIVE_RESET_TOKENS_PER_EMAIL = 3
_dummy_hash: Optional[str] = None


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

class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

# Password reset tokens are stored only as SHA-256 digests: digest -> {"email", "expires_at"}
PASSWORD_RESET_TOKENS: Dict[str, Dict[str, Any]] = {}


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _deliver_reset_token(email: str, token: str) -> None:
    """Deliver a reset token out-of-band. Until an SMTP/SMS channel is connected this writes
    to the server log (operators only). The token is NEVER returned in the API response."""
    logger.warning("Password reset requested for %s. One-time token (valid 15 min): %s", email, token)


def _burn_time_for_unknown_user(password: str) -> None:
    """Spend comparable CPU time for unknown accounts so timing does not reveal valid emails."""
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = hash_password("not-a-real-account-password")
    verify_password(password, _dummy_hash)


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
    if user is None:
        _burn_time_for_unknown_user(payload.password)
        credentials_ok = False
    else:
        credentials_ok = verify_password(payload.password, user.get("password_hash"))

    if not credentials_ok:
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
        "department": user["department"],
        "tv": user.get("token_version", 0),
        "fid": uuid.uuid4().hex,  # login session family, used for refresh-token rotation
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
    """Exchange a refresh token for a new pair. Refresh tokens are single-use (rotation)."""
    token_data = verify_token(payload.refresh_token, expected_type="refresh")
    email = token_data.get("sub")

    user = DEMO_USERS.get(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if int(token_data.get("tv", 0) or 0) != int(user.get("token_version", 0) or 0):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is no longer valid. Please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Rotation: the presented token is now spent. Replaying it after the grace window means it
    # was copied, so the whole login session (every token in its family) is revoked.
    if consume_refresh_token(token_data) == "reuse":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token reuse detected. Token has been revoked; please sign in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_payload = {
        "sub": user["email"],
        "id": user["id"],
        "name": user["name"],
        "role": user["role"],
        "department": user["department"],
        "tv": user.get("token_version", 0),
        # Tokens issued before rotation existed have no family: start one now.
        "fid": token_data.get("fid") or uuid.uuid4().hex,
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
def register_user(
    payload: RegisterRequest,
    _admin: Dict[str, Any] = Depends(require_permission("user:admin")),
):
    """Create a user account. Administrators only: self-registration is not offered because a
    public sign-up that accepts a role would let anyone mint an administrator."""
    email = payload.email.strip().lower()
    if not _EMAIL_RE.match(email) or len(email) > 254:
        raise HTTPException(status_code=422, detail="A valid email address is required.")
    full_name = (payload.full_name or "").strip()
    if not full_name or len(full_name) > 100:
        raise HTTPException(status_code=422, detail="Full name must contain 1 to 100 characters.")
    role = payload.role or "SECURITY_ANALYST"
    if role not in ROLES:
        raise HTTPException(status_code=422, detail=f"Unknown role. Choose one of: {', '.join(ROLES)}.")
    problems = validate_password_policy(payload.password)
    if problems:
        raise HTTPException(status_code=422, detail=" ".join(problems))
    if email in DEMO_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    new_user = {
        "id": f"usr_{uuid.uuid4().hex[:8]}",
        "email": email,
        "name": full_name,
        "role": role,
        "department": (payload.department or "SOC Operations")[:100],
        "organization": (payload.organization or "")[:100],
        "password_hash": hash_password(payload.password),
    }
    DEMO_USERS[email] = new_user
    persist_users()

    return {
        "status": "CREATED",
        "message": f"User {email} created.",
        "user": {
            "id": new_user["id"],
            "email": email,
            "name": full_name,
            "role": role,
            "department": new_user["department"],
            "organization": new_user["organization"],
        }
    }

@router.post("/api/auth/password-reset")
@router.post("/api/v1/auth/password-reset")
def request_password_reset(payload: PasswordResetRequest):
    """Always answers the same way so the endpoint cannot be used to discover accounts.
    The one-time token is delivered out-of-band and is never part of the response."""
    email = payload.email.strip().lower()
    now = datetime.now(timezone.utc)

    if PASSWORD_RESET_ENABLED and email in DEMO_USERS:
        # Forget expired tokens and cap how many can be live for one account
        for key in [k for k, v in PASSWORD_RESET_TOKENS.items() if v["expires_at"] < now]:
            del PASSWORD_RESET_TOKENS[key]
        live = sorted(
            (k for k, v in PASSWORD_RESET_TOKENS.items() if v["email"] == email),
            key=lambda k: PASSWORD_RESET_TOKENS[k]["expires_at"],
        )
        for key in live[: max(0, len(live) - _MAX_LIVE_RESET_TOKENS_PER_EMAIL + 1)]:
            del PASSWORD_RESET_TOKENS[key]

        token = f"rst_{secrets.token_urlsafe(32)}"
        PASSWORD_RESET_TOKENS[_digest(token)] = {"email": email, "expires_at": now + _RESET_TTL}
        _deliver_reset_token(email, token)

    return {
        "status": "QUEUED",
        "message": "If the account exists, a password reset token has been dispatched."
    }

@router.post("/api/auth/password-reset/confirm")
@router.post("/api/v1/auth/password-reset/confirm")
def confirm_password_reset(payload: PasswordResetConfirmRequest):
    invalid = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    token_info = PASSWORD_RESET_TOKENS.get(_digest(payload.reset_token or ""))
    if not token_info or token_info["expires_at"] < datetime.now(timezone.utc):
        raise invalid

    problems = validate_password_policy(payload.new_password)
    if problems:
        raise HTTPException(status_code=422, detail=" ".join(problems))

    email = token_info["email"]
    user = DEMO_USERS.get(email)
    if user is None:
        raise invalid
    user["password_hash"] = hash_password(payload.new_password)
    # Retire every session issued before the reset (access and refresh tokens carry the old version)
    user["token_version"] = int(user.get("token_version", 0) or 0) + 1
    persist_users()

    # The token is single-use; revoke every other pending token and clear any lockout
    for key in [k for k, v in PASSWORD_RESET_TOKENS.items() if v["email"] == email]:
        del PASSWORD_RESET_TOKENS[key]
    LOGIN_ATTEMPTS.pop(email, None)
    return {"status": "SUCCESS", "message": "Password reset successfully. Please login with your new credentials."}

@router.post("/api/auth/logout")
@router.post("/api/v1/auth/logout")
def logout_user(
    payload: Optional[LogoutRequest] = None,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
):
    """Revoke the presented access token and, if supplied, the refresh token.

    Idempotent: expired, malformed or already-revoked tokens are ignored, so signing out
    never fails because a session had already ended."""
    candidates = (
        (credentials.credentials if credentials else None, "access"),
        (payload.refresh_token if payload else None, "refresh"),
    )
    verified = []
    for token, kind in candidates:
        if not token:
            continue
        try:
            verified.append(verify_token(token, expected_type=kind))
        except HTTPException:
            continue
    # Revoke each token first, then end the login family; doing it in this order keeps the count
    # honest (a revoked family would otherwise make the second token look already invalid).
    revoked = sum(1 for data in verified if revoke_token_payload(data))
    # Ending the family also kills earlier-rotated tokens of this login.
    for data in verified:
        revoke_family(data)
    return {"status": "SUCCESS", "message": "Session invalidated.", "revoked_tokens": revoked}

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
    """Returns available pre-seeded demo accounts for easy evaluator onboarding (demo mode only)."""
    if not DEMO_MODE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
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
