"""
Password hashing and policy for ETHIO-CYBERGUARD.

* Hashes use PBKDF2-HMAC-SHA256 with a random 16-byte salt per password.
* Stored format: ``pbkdf2_sha256$<iterations>$<salt_b64>$<hash_b64>`` so the work factor
  can be raised later without invalidating existing hashes.
* Verification is constant-time and never raises on malformed input.
* Legacy fixed-salt PBKDF2 hex hashes (old ``database.connection`` format) still verify,
  so existing database rows keep working; use ``needs_rehash`` to upgrade them on login.

Set ``PASSWORD_HASH_ITERATIONS`` to tune the work factor (tests use a tiny value).
"""

import base64
import hashlib
import hmac
import os
import re
import secrets
from typing import List, Optional

SCHEME = "pbkdf2_sha256"
DEFAULT_ITERATIONS = int(os.getenv("PASSWORD_HASH_ITERATIONS", "600000"))
_MIN_ITERATIONS = 1
_MAX_ITERATIONS = 5_000_000  # refuse absurd values from a tampered hash (CPU DoS)
_LEGACY_SALT = b"ecg_salt_2026_ethiopia"
_LEGACY_ITERATIONS = 100_000

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128
_COMMON_PASSWORDS = {
    "password1234", "password12345", "123456789012", "qwertyuiop12",
    "administrator", "ethiocyberguard", "changemechangeme", "letmein123456",
}


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.b64decode(text + "=" * ((4 - len(text) % 4) % 4), validate=True)


def hash_password(password: str, iterations: Optional[int] = None) -> str:
    """Return a salted PBKDF2-SHA256 hash string for the password."""
    rounds = int(iterations or DEFAULT_ITERATIONS)
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, rounds)
    return f"{SCHEME}${rounds}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, stored: Optional[str]) -> bool:
    """Constant-time check. Returns False (never raises) for malformed or empty input."""
    if not isinstance(password, str) or not isinstance(stored, str) or not stored:
        return False
    try:
        if stored.startswith(SCHEME + "$"):
            _, rounds_text, salt_text, hash_text = stored.split("$")
            rounds = int(rounds_text)
            if not (_MIN_ITERATIONS <= rounds <= _MAX_ITERATIONS):
                return False
            expected = _unb64(hash_text)
            actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _unb64(salt_text), rounds)
            return hmac.compare_digest(actual, expected)
        # Legacy fixed-salt PBKDF2 hex digest (64 hex chars)
        if re.fullmatch(r"[0-9a-fA-F]{64}", stored):
            legacy = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), _LEGACY_SALT, _LEGACY_ITERATIONS).hex()
            return hmac.compare_digest(legacy, stored.lower())
    except (ValueError, TypeError):
        return False
    return False


def needs_rehash(stored: str) -> bool:
    """True for legacy hashes or hashes weaker than the current work factor."""
    if not isinstance(stored, str) or not stored.startswith(SCHEME + "$"):
        return True
    try:
        return int(stored.split("$")[1]) < DEFAULT_ITERATIONS
    except (IndexError, ValueError):
        return True


def validate_password_policy(password: object) -> List[str]:
    """Return a list of human-readable problems (empty list means the password is acceptable)."""
    if not isinstance(password, str) or not password:
        return ["Password is required."]
    problems: List[str] = []
    if len(password) < MIN_PASSWORD_LENGTH:
        problems.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")
    if len(password) > MAX_PASSWORD_LENGTH:
        problems.append(f"Password must be at most {MAX_PASSWORD_LENGTH} characters long.")
    classes = sum(
        bool(re.search(pattern, password))
        for pattern in (r"[a-z]", r"[A-Z]", r"\d", r"[^A-Za-z0-9]")
    )
    if classes < 3:
        problems.append("Password must mix at least three of: lowercase, uppercase, digits, symbols.")
    if password.lower() in _COMMON_PASSWORDS:
        problems.append("Password is too common.")
    return problems
