"""
Multi-tenant isolation helpers for ETHIO-CYBERGUARD.

Every stored record (incident, SOAR action, audit entry) belongs to one organization
through its ``org_id`` field. A signed-in user belongs to exactly one organization and only
sees that organization's records. The one exception is SUPER_ADMIN, the national
administrator, who can see and act across all organizations.

Design rules
------------
* A record that has no ``org_id`` (saved before tenancy existed, or a built-in demo record)
  belongs to the default organization (Commercial Bank of Ethiopia). Old data keeps working.
* A user's organization comes from an explicit ``org_id`` if the account has one, otherwise
  from the account's ``organization`` name, otherwise the default organization.
* Looking up another organization's record answers "not found", never "forbidden", so a
  caller cannot even learn that the record exists.

This module has no web-framework imports, so it can be unit-tested on its own.
"""

import re
from typing import Any, Dict, Iterable, List, Optional

DEFAULT_ORG_ID = "org_cbe_01"
DEFAULT_ORG_NAME = "Commercial Bank of Ethiopia"
GLOBAL_ROLES = frozenset({"SUPER_ADMIN"})

_ORG_ID_RE = re.compile(r"^org_[a-z0-9_]{1,60}$")
_KNOWN_NAMES = {
    "commercial bank of ethiopia": DEFAULT_ORG_ID,
    "cbe": DEFAULT_ORG_ID,
}


def org_id_from_name(name: Optional[str]) -> str:
    """Turn an organization name into a stable id: 'Awash Bank' -> 'org_awash_bank'."""
    cleaned = re.sub(r"\s+", " ", str(name or "")).strip().lower()
    if not cleaned:
        return DEFAULT_ORG_ID
    if cleaned in _KNOWN_NAMES:
        return _KNOWN_NAMES[cleaned]
    slug = re.sub(r"[^a-z0-9]+", "_", cleaned).strip("_")[:56]
    return f"org_{slug}" if slug else DEFAULT_ORG_ID


def normalize_org_id(value: Optional[str]) -> str:
    """Accept a ready-made id ('org_awash_bank') or a plain name ('Awash Bank')."""
    text = str(value or "").strip().lower()
    if _ORG_ID_RE.match(text):
        return text
    return org_id_from_name(value)


def org_of(user: Optional[Dict[str, Any]]) -> str:
    """The organization a user belongs to."""
    if not user:
        return DEFAULT_ORG_ID
    explicit = user.get("org_id")
    if explicit:
        return normalize_org_id(str(explicit))
    return org_id_from_name(user.get("organization"))


def is_global(user: Optional[Dict[str, Any]]) -> bool:
    """True for national administrators who may see every organization."""
    return bool(user) and str(user.get("role", "")).upper() in GLOBAL_ROLES


def record_org(record: Optional[Dict[str, Any]]) -> str:
    """The organization a stored record belongs to (legacy records -> default org)."""
    if not record:
        return DEFAULT_ORG_ID
    explicit = record.get("org_id")
    return normalize_org_id(str(explicit)) if explicit else DEFAULT_ORG_ID


def can_access(user: Optional[Dict[str, Any]], record: Optional[Dict[str, Any]]) -> bool:
    return is_global(user) or record_org(record) == org_of(user)


def scope(user: Optional[Dict[str, Any]], records: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """The records this user is allowed to see (a new list; the store is never modified)."""
    if is_global(user):
        return list(records)
    mine = org_of(user)
    return [r for r in records if record_org(r) == mine]
