"""SOAR audit trail with verifiable SHA-256 hash chaining."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import hashlib


GENESIS_HASH = hashlib.sha256(b"GENESIS_ETHIO_CYBERGUARD_2026").hexdigest()
ZERO_HASH = "0" * 64


class ImmutableAuditLog:
    """Maintain a tamper-evident audit chain and verify links plus entry contents."""

    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self._genesis()

    def _genesis(self) -> None:
        self.chain.append({
            "index": 0,
            "timestamp": "2026-09-30T00:00:00Z",
            "operator": "SYSTEM",
            "action": "GENESIS_INITIALIZE",
            "target": "SOC_CORE",
            "reason": "Platform initialization",
            "result": "SUCCESS",
            "prev_hash": ZERO_HASH,
            "hash": GENESIS_HASH,
        })

    @staticmethod
    def _calculate_hash(entry: Dict[str, Any]) -> str:
        raw_data = (
            f"{entry['index']}|{entry['timestamp']}|{entry['operator']}|"
            f"{entry['action']}|{entry['target']}|{entry['reason']}|"
            f"{entry['result']}|{entry.get('approval_id')}|{entry['prev_hash']}"
        )
        return hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

    def record(
        self,
        operator: str,
        action: str,
        target: str,
        reason: str,
        result: str = "SUCCESS",
        approval_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not self.chain:
            self._genesis()
        prev_hash = self.chain[-1]["hash"]
        entry = {
            "index": len(self.chain),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operator": str(operator),
            "action": str(action),
            "target": str(target),
            "reason": str(reason),
            "result": str(result),
            "approval_id": approval_id,
            "prev_hash": prev_hash,
        }
        entry["hash"] = self._calculate_hash(entry)
        self.chain.append(entry)
        return entry

    def verify_integrity(self) -> bool:
        """Return False if any event field, hash, index, or chain link was changed."""
        if not self.chain:
            return False
        genesis = self.chain[0]
        if (
            genesis.get("index") != 0
            or genesis.get("prev_hash") != ZERO_HASH
            or genesis.get("hash") != GENESIS_HASH
            or genesis.get("operator") != "SYSTEM"
            or genesis.get("action") != "GENESIS_INITIALIZE"
        ):
            return False

        for expected_index, entry in enumerate(self.chain[1:], start=1):
            previous = self.chain[expected_index - 1]
            if entry.get("index") != expected_index:
                return False
            if entry.get("prev_hash") != previous.get("hash"):
                return False
            try:
                if entry.get("hash") != self._calculate_hash(entry):
                    return False
            except (KeyError, TypeError, ValueError):
                return False
        return True
