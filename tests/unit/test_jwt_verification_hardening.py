"""Regression tests for strict JWT verification error handling."""
import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from apps.api.dependencies import (
    JWT_SECRET,
    create_access_token,
    verify_token,
)


def _encode_segment(value):
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _signed_token(header, payload):
    header_part = _encode_segment(json.dumps(header).encode())
    payload_part = _encode_segment(json.dumps(payload).encode())
    signing_input = f"{header_part}.{payload_part}".encode("ascii")
    signature = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    return f"{header_part}.{payload_part}.{_encode_segment(signature)}"


def test_valid_access_token_still_verifies():
    token = create_access_token({"sub": "analyst@example.com", "role": "SECURITY_ANALYST"})
    assert verify_token(token)["sub"] == "analyst@example.com"


@pytest.mark.parametrize("token", ["", "a.b", "a.b.c", "@@@.@@@.@@@", "a.eyJleHAiOjF9.@@@"])
def test_malformed_tokens_return_401(token):
    with pytest.raises(HTTPException) as exc:
        verify_token(token)
    assert exc.value.status_code == 401


def test_wrong_algorithm_is_rejected():
    exp = int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp())
    token = _signed_token({"alg": "none", "typ": "JWT"}, {"sub": "attacker", "exp": exp})
    with pytest.raises(HTTPException) as exc:
        verify_token(token)
    assert exc.value.status_code == 401


def test_missing_expiration_is_rejected():
    token = _signed_token({"alg": "HS256", "typ": "JWT"}, {"sub": "analyst@example.com"})
    with pytest.raises(HTTPException) as exc:
        verify_token(token)
    assert exc.value.status_code == 401


def test_non_object_payload_is_rejected():
    header = _encode_segment(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _encode_segment(json.dumps(["not", "an", "object"]).encode())
    signing_input = f"{header}.{payload}".encode("ascii")
    signature = hmac.new(JWT_SECRET.encode(), signing_input, hashlib.sha256).digest()
    token = f"{header}.{payload}.{_encode_segment(signature)}"
    with pytest.raises(HTTPException) as exc:
        verify_token(token)
    assert exc.value.status_code == 401
