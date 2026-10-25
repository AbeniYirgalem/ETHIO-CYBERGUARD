"""
Tenant resolution for data collectors.

A collector proves who it is with an API key (or a login token), and that identity also says
WHICH ORGANIZATION the events belong to:

* ``INGEST_ORG_KEYS`` key             -> the organization listed for that key
* the shared ``INGEST_API_KEY``       -> ``INGEST_DEFAULT_ORG`` (Commercial Bank of Ethiopia)
* a user's Bearer login token         -> that user's own organization
* demo mode only                      -> optional ``X-Org-ID`` header, so one demo server can
                                         simulate several organizations

In production a collector can never choose its organization: it is fixed by its key.
"""

import hmac
from typing import Optional

from fastapi import Header, HTTPException, status

from services.security.tenancy import DEFAULT_ORG_ID, normalize_org_id, org_of

from . import dependencies
from .config import INGEST_DEFAULT_ORG, INGEST_ORG_KEYS


def _same(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def resolve_collector_org(
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
    x_org_id: Optional[str] = Header(None),
) -> str:
    """Authenticate a collector and return the organization its events belong to."""
    if dependencies.DEMO_MODE:
        return normalize_org_id(x_org_id) if x_org_id else DEFAULT_ORG_ID

    if x_api_key:
        for key, org in INGEST_ORG_KEYS.items():
            if _same(key, x_api_key):
                return normalize_org_id(org)
        if _same(dependencies.INGEST_API_KEY, x_api_key):
            return normalize_org_id(INGEST_DEFAULT_ORG)

    if authorization and authorization.startswith("Bearer "):
        try:
            payload = dependencies.verify_token(authorization.split(" ", 1)[1])
        except Exception:  # noqa: BLE001 - any bad token falls through to the 401 below
            payload = None
        if payload is not None:
            user = dependencies.DEMO_USERS.get(payload.get("sub"))
            if user is not None:
                return org_of(user)
            return normalize_org_id(payload.get("org_id") or payload.get("organization"))

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized collector. Valid X-API-Key or Bearer token required.",
    )
