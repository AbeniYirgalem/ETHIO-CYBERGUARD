"""
ETHIO-CYBERGUARD API Configuration & Settings
Environment-aware settings for Security Operations Center and AI Platform.
"""

import os
from typing import List, Optional

from services.security.passwords import validate_password_policy

# Mode Separation
# DEMO_MODE=true  -> simulated data, guest access and demo collector bypass allowed.
# DEMO_MODE=false -> production: every sensitive route needs a real login and
#                    the app refuses to start with default/weak secrets.
DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

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

# Bootstrap administrator (production). In DEMO_MODE=false the built-in demo accounts do
# not exist, so this account is the only way to sign in until more users are created.
BOOTSTRAP_ADMIN_EMAIL: str = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "").strip().lower()
BOOTSTRAP_ADMIN_PASSWORD: str = os.getenv("BOOTSTRAP_ADMIN_PASSWORD", "")

# Self-service password reset (token is delivered out-of-band, never in the API response)
PASSWORD_RESET_ENABLED: bool = os.getenv("PASSWORD_RESET_ENABLED", "true").lower() in ("true", "1", "yes")

# Ingestion & Protections
MAX_PAYLOAD_BYTES: int = int(os.getenv("MAX_PAYLOAD_BYTES", str(2 * 1024 * 1024))) # 2MB limit
RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "120"))
INGEST_API_KEY: str = os.getenv("INGEST_API_KEY", _DEFAULT_INGEST_API_KEY)

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
    if problems:
        raise RuntimeError("Insecure production configuration: " + "; ".join(problems) + ".")
