"""
ETHIO-CYBERGUARD API Configuration & Settings
Environment-aware settings for Security Operations Center and AI Platform.
"""

import os
from typing import List

# Mode Separation
DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1", "yes")

# Database & Cache
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ethio_cyberguard.db")
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Security & Tokens
JWT_SECRET: str = os.getenv("JWT_SECRET", "ethio-cyberguard-production-hmac-sha256-key-9281923")
JWT_ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Ingestion & Protections
MAX_PAYLOAD_BYTES: int = int(os.getenv("MAX_PAYLOAD_BYTES", str(2 * 1024 * 1024))) # 2MB limit
RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "120"))
INGEST_API_KEY: str = os.getenv("INGEST_API_KEY", "ecg-collector-secure-api-key-2026")

# CORS Origins
ALLOWED_ORIGINS: List[str] = [
    origin.strip() 
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,https://AbeniYirgalem.github.io"
    ).split(",")
    if origin.strip()
]
