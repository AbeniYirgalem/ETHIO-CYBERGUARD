"""
Durable state store for ETHIO-CYBERGUARD.

Keeps the API's working collections (incidents, SOAR actions, audit log) alive across
restarts. Each collection is stored as one JSON document in the ``state_documents``
table, so it works unchanged on SQLite (local default) and PostgreSQL (Docker, via
``DATABASE_URL``).

How it fits together
--------------------
* Routers keep using plain in-memory lists for speed and simplicity.
* ``register(name, store)`` tells this module which list belongs to which collection.
* ``restore_all()`` (called at API startup) loads saved data into those same list
  objects *in place* (so modules that imported the list keep working). If nothing was
  saved yet, the built-in seed data is written as the first snapshot.
* ``save(name, store)`` writes a snapshot after every state-changing request.

Limitations (documented on purpose)
-----------------------------------
Snapshots are last-writer-wins, so run a single API worker per database until the
collections move to relational tables. Persistence failures are logged, never silently
swallowed, and the API keeps serving from memory.
"""

import copy
import json
import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, DateTime, Integer, MetaData, String, Table, Text, insert, select, update
from sqlalchemy.exc import IntegrityError

from database.connection import engine

logger = logging.getLogger("ecg.state_store")

ENABLED: bool = os.getenv("PERSISTENCE_ENABLED", "true").lower() in ("true", "1", "yes")

_metadata = MetaData()
state_documents = Table(
    "state_documents",
    _metadata,
    Column("name", String(64), primary_key=True),
    Column("data", Text, nullable=False),
    Column("version", Integer, nullable=False, default=1),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

_registry: Dict[str, List[Dict[str, Any]]] = {}
_lock = threading.RLock()
_table_ready = False


def _ensure_table() -> None:
    global _table_ready
    if _table_ready:
        return
    _metadata.create_all(bind=engine, tables=[state_documents])
    _table_ready = True


def register(name: str, store: List[Dict[str, Any]]) -> None:
    """Bind an in-memory list to a persisted collection (no database access yet)."""
    _registry[name] = store


def load(name: str) -> Optional[List[Dict[str, Any]]]:
    """Return the saved collection, or None if nothing valid is saved."""
    if not ENABLED:
        return None
    with _lock:
        _ensure_table()
        with engine.connect() as conn:
            row = conn.execute(
                select(state_documents.c.data).where(state_documents.c.name == name)
            ).first()
    if row is None:
        return None
    try:
        data = json.loads(row[0])
    except (TypeError, ValueError):
        logger.error("Saved state '%s' is corrupt and was ignored.", name)
        return None
    if not isinstance(data, list):
        logger.error("Saved state '%s' has an unexpected shape and was ignored.", name)
        return None
    return data


def save(name: str, store: Optional[List[Dict[str, Any]]] = None) -> bool:
    """Write a snapshot of the collection. Returns False (and logs) on failure."""
    if not ENABLED:
        return False
    target = store if store is not None else _registry.get(name)
    if target is None:
        raise KeyError(f"Unknown state collection '{name}'")
    try:
        with _lock:
            payload = json.dumps(copy.deepcopy(target), default=str, ensure_ascii=False)
            _ensure_table()
            now = datetime.now(timezone.utc)
            with engine.begin() as conn:
                result = conn.execute(
                    update(state_documents)
                    .where(state_documents.c.name == name)
                    .values(data=payload, version=state_documents.c.version + 1, updated_at=now)
                )
                if result.rowcount == 0:
                    try:
                        conn.execute(
                            insert(state_documents).values(
                                name=name, data=payload, version=1, updated_at=now
                            )
                        )
                    except IntegrityError:
                        # Another worker inserted first; fall back to updating.
                        conn.execute(
                            update(state_documents)
                            .where(state_documents.c.name == name)
                            .values(data=payload, updated_at=now)
                        )
        return True
    except Exception:  # noqa: BLE001 - persistence must never crash a request
        logger.exception("Failed to persist state collection '%s'", name)
        return False


def restore_all(attempts: Optional[int] = None, delay: float = 2.0) -> Dict[str, str]:
    """Load every registered collection in place; seed the database when empty.

    Returns a mapping of collection -> "restored" | "seeded" | "memory-only".
    Retries on connection errors (useful while Postgres is still starting in Docker).
    """
    outcome: Dict[str, str] = {}
    if not ENABLED:
        return {name: "memory-only" for name in _registry}
    if attempts is None:
        attempts = 1 if str(engine.url).startswith("sqlite") else 8
    for name, store in _registry.items():
        outcome[name] = "memory-only"
        for attempt in range(1, attempts + 1):
            try:
                saved = load(name)
                if saved is not None:
                    store[:] = saved  # in place: other modules hold references to this list
                    outcome[name] = "restored"
                elif save(name, store):
                    outcome[name] = "seeded"
                break
            except Exception:  # noqa: BLE001
                logger.warning("State restore for '%s' failed (attempt %d/%d)", name, attempt, attempts, exc_info=True)
                if attempt < attempts:
                    time.sleep(delay)
    return outcome
