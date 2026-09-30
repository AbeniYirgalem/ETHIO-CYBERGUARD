"""
ETHIO-CYBERGUARD API Configuration & Settings
"""

import os

JWT_SECRET = os.getenv("JWT_SECRET", "ethio-cyberguard-dev-secret-key-3902184029")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

ALLOWED_ORIGINS = [
    origin.strip() 
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,https://AbeniYirgalem.github.io"
    ).split(",")
    if origin.strip()
]
