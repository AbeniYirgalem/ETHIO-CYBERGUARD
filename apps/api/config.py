"""
ETHIO-CYBERGUARD API Configuration & Settings
Environment-aware settings for Security Operations Center and AI Platform.
Enforces strict fail-closed security invariants for production deployments.
"""

import os
from typing import List, Optional

from services.security.passwords import validate_password_policy

# Environment: "development", "test", or "production"
ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").strip().lower()

# Mode Separation
# DEMO_MODE=true  -> simulated data, guest access and demo collector bypass allowed.
# DEMO_MODE=false -> production: every sensitive route needs a real login and
#                    the app refuses to start with default/weak secrets.
DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")
_demo_env = os.getenv("DEMO_MODE")
if ENVIRONMENT == "production":
    # In production, DEMO_MODE defaults to false and cannot be true
    DEMO_MODE: bool = False if _demo_env is None else (_demo_env.lower() in ("true", "1", "yes"))
else:
    # In development/testing, DEMO_MODE defaults to true
    DEMO_MODE: bool = True if _demo_env is None else (_demo_env.lower() in ("true", "1", "yes"))

# Database & Cache
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ethio_cyberguard.db")
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Security & Tokens
_DEFAULT_JWT_SECRET = "ethio-cyberguard-production-hmac-sha256-key-9281923"
_DEFAULT_INGEST_API_KEY = "ecg-collector-secure-api-key-2026"

# JWT_SECRET is preferred; API_SECRET_KEY (used by docker-compose / .env.example)
# is accepted as an alias so the deployed secret is actually applied.
JWT_SECRET: str = os.getenv("JWT_SECRET") or os.getenv("API_SECRET_KEY") or _DEFAULT_JWT_SECRET
JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
# Refresh tokens are single-use. A token presented a second time within this many seconds is
# tolerated (two tabs refreshing at once); after that, reuse revokes the whole login session.
REFRESH_REUSE_GRACE_SECONDS: int = int(os.getenv("REFRESH_REUSE_GRACE_SECONDS", "10"))

# Bootstrap administrator (production). In DEMO_MODE=false the built-in demo accounts do
# not exist, so this account is the only way to sign in until more users are created.
BOOTSTRAP_ADMIN_EMAIL: str = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
BOOTSTRAP_ADMIN_PASSWORD: str = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")

# Self-service password reset (token is delivered out-of-band, never in the API response)
PASSWORD_RESET_ENABLED: bool = os.getenv("PASSWORD_RESET_ENABLED", "true").lower() in ("true", "1", "yes")
JWT_SECRET: str = os.getenv("JWT_SECRET", "ethio-cyberguard-dev-default-signing-key-32chars-strictly")
JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
API_SECRET_KEY: str = os.getenv("API_SECRET_KEY", "ecg_dev_api_secret_key_32chars_long_placeholder")

# Ingestion & Protections
MAX_PAYLOAD_BYTES: int = int(os.getenv("MAX_PAYLOAD_BYTES", str(2 * 1024 * 1024))) # 2MB limit
RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "120"))
INGEST_API_KEY: str = os.getenv("INGEST_API_KEY", _DEFAULT_INGEST_API_KEY)
# Multi-tenant collectors. The shared INGEST_API_KEY above feeds INGEST_DEFAULT_ORG; each
# organization can also get its own collector key:  INGEST_ORG_KEYS="key1:org_awash_bank,key2:Telebirr"
INGEST_DEFAULT_ORG: str = os.getenv("INGEST_DEFAULT_ORG", "org_cbe_01")


def _parse_org_keys(raw: str) -> dict:
    keys = {}
    for pair in (raw or "").split(","):
        if ":" not in pair:
            continue
        key, org = pair.rsplit(":", 1)
        key, org = key.strip(), org.strip()
        if key and org:
            keys[key] = org
    return keys


INGEST_ORG_KEYS: dict = _parse_org_keys(os.getenv("INGEST_ORG_KEYS", ""))

# HTTP hardening (see apps/api/security_middleware.py)
# Per-IP limit on login / refresh / password-reset. Default: ON in production, OFF in demo mode.
_rl_env = os.getenv("AUTH_RATE_LIMIT_ENABLED")
AUTH_RATE_LIMIT_ENABLED: Optional[bool] = None if _rl_env is None else _rl_env.lower() in ("true", "1", "yes")
AUTH_RATE_LIMIT_PER_MINUTE: int = int(os.getenv("AUTH_RATE_LIMIT_PER_MINUTE", "10"))
# Set TRUST_PROXY=true only when the API sits behind a reverse proxy you control
# (it then reads the client IP from X-Forwarded-For).
TRUST_PROXY: bool = os.getenv("TRUST_PROXY", "false").lower() in ("true", "1", "yes")
# Strict-Transport-Security header. Default: ON in production, OFF in demo mode.
_hsts_env = os.getenv("ENABLE_HSTS")
ENABLE_HSTS: Optional[bool] = None if _hsts_env is None else _hsts_env.lower() in ("true", "1", "yes")

# CORS Origins
ALLOWED_ORIGINS: List[str] = [
    origin.strip() 
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,https://AbeniYirgalem.github.io"
    ).split(",")
    if origin.strip()
]

_INSECURE_MARKERS = (
    "change_in_prod",
    "dev_secret",
    "ethio-cyberguard-production-hmac",
    "ecg-collector-secure-api-key",
)
_MIN_SECRET_LENGTH = 32


def _is_weak(secret: str, min_length: int) -> bool:
    lowered = (secret or "").lower()
    return len(secret or "") < min_length or any(marker in lowered for marker in _INSECURE_MARKERS)


def validate_production_config(
    demo_mode: Optional[bool] = None,
    jwt_secret: Optional[str] = None,
    ingest_key: Optional[str] = None,
    bootstrap_email: Optional[str] = None,
    bootstrap_password: Optional[str] = None,
) -> None:
    """Refuse to start in production (DEMO_MODE=false) with default or weak secrets."""
    demo = DEMO_MODE if demo_mode is None else demo_mode
    if demo:
        return
    jwt = JWT_SECRET if jwt_secret is None else jwt_secret
    ingest = INGEST_API_KEY if ingest_key is None else ingest_key
    admin_email = BOOTSTRAP_ADMIN_EMAIL if bootstrap_email is None else bootstrap_email
    admin_password = BOOTSTRAP_ADMIN_PASSWORD if bootstrap_password is None else bootstrap_password
    problems = []
    if "@" not in (admin_email or ""):
        problems.append("BOOTSTRAP_ADMIN_EMAIL must be set to the first administrator's email address")
    admin_policy = validate_password_policy(admin_password)
    if admin_policy:
        problems.append("BOOTSTRAP_ADMIN_PASSWORD is not acceptable (" + " ".join(admin_policy) + ")")
    if _is_weak(jwt, _MIN_SECRET_LENGTH):
        problems.append("JWT_SECRET must be set to a unique random value of at least 32 characters")
    if _is_weak(ingest, 16):
        problems.append("INGEST_API_KEY must be set to a unique random value of at least 16 characters")
    for org_key in INGEST_ORG_KEYS:
        if _is_weak(org_key, 16):
            problems.append("every INGEST_ORG_KEYS key must be a unique random value of at least 16 characters")
            break
    if problems:
        raise RuntimeError("Insecure production configuration: " + "; ".join(problems) + ".")
# Insecure/Default Secret Blacklist
INSECURE_SECRETS = {
    "change_me",
    "secopspassw0rd_2026!",
    "ecg_development_jwt_secret_key_change_in_prod",
    "ethio-cyberguard-production-hmac-sha256-key-9281923",
    "ethio-cyberguard-dev-default-signing-key-32chars-strictly",
    "ecg_dev_api_secret_key_32chars_long_placeholder",
    "ecg-collector-secure-api-key-2026",
    "ecg_dev_jwt_secret_key_change_in_prod_strictly",
    "ecg_dev_insecure_password_do_not_use_in_prod",
    "ecg-dev-collector-key-2026",
    "ecg_dev_redis_secret_local",
    "secret",
    "password",
    "admin"
}

def is_production() -> bool:
    return ENVIRONMENT == "production"

def validate_production_configuration():
    """
    Validates that production configurations meet strict security standards.
    Fails closed by raising RuntimeError if insecure defaults or demo mode are detected.
    """
    if ENVIRONMENT != "production":
        return

    errors = []

    # 1. Enforce DEMO_MODE is False in production
    if DEMO_MODE:
        errors.append("DEMO_MODE must be set to 'false' in production environments.")

    # 2. Enforce strong JWT_SECRET
    jwt_secret_lower = (JWT_SECRET or "").lower()
    if not JWT_SECRET or len(JWT_SECRET) < 32:
        errors.append("JWT_SECRET must be at least 32 characters in production.")
    if any(insecure in jwt_secret_lower for insecure in ["change_me", "default", "placeholder"]) or JWT_SECRET in INSECURE_SECRETS:
        errors.append("Default or placeholder JWT_SECRET detected. Strong secret required in production.")

    # 3. Enforce strong API_SECRET_KEY
    api_secret_lower = (API_SECRET_KEY or "").lower()
    if not API_SECRET_KEY or len(API_SECRET_KEY) < 32:
        errors.append("API_SECRET_KEY must be at least 32 characters in production.")
    if any(insecure in api_secret_lower for insecure in ["change_me", "placeholder", "dev"]) or API_SECRET_KEY in INSECURE_SECRETS:
        errors.append("Default or placeholder API_SECRET_KEY detected in production.")

    # 4. Enforce strong INGEST_API_KEY
    ingest_key_lower = (INGEST_API_KEY or "").lower()
    if not INGEST_API_KEY or INGEST_API_KEY in INSECURE_SECRETS or "change_me" in ingest_key_lower:
        errors.append("Default or placeholder INGEST_API_KEY detected in production.")

    # 5. Enforce strong database password (no SecOpsPassw0rd_2026! or default strings)
    db_lower = (DATABASE_URL or "").lower()
    if any(insecure in db_lower for insecure in ["secopspassw0rd_2026!", "change_me", "insecure"]):
        errors.append("Default or placeholder database credentials detected in DATABASE_URL in production.")

    if errors:
        error_msg = "PRODUCTION STARTUP VALIDATION FAILED CLOSED:\n  - " + "\n  - ".join(errors)
        raise RuntimeError(error_msg)

# Execute validation on import if environment is production
if ENVIRONMENT == "production":
    validate_production_configuration()
