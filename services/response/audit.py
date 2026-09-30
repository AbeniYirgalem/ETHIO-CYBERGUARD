"""
ETHIO-CYBERGUARD SOAR Immutable Audit Trail
Records tamper-evident log entries using cryptographic SHA-256 block linking.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import hashlib

class ImmutableAuditLog:
    """Maintains a cryptographically verifiable audit trail of sensitive actions."""

    def __init__(self):
        self.chain: List[Dict[str, Any]] = []
        self._genesis()

    def _genesis(self):
        genesis_entry = {
            "index": 0,
            "timestamp": "2026-09-30T00:00:00Z",
            "operator": "SYSTEM",
            "action": "GENESIS_INITIALIZE",
            "target": "SOC_CORE",
            "reason": "Platform initialization",
            "result": "SUCCESS",
            "prev_hash": "0" * 64,
            "hash": hashlib.sha256(b"GENESIS_ETHIO_CYBERGUARD_2026").hexdigest()
        }
        self.chain.append(genesis_entry)

    def record(
        self,
        operator: str,
        action: str,
        target: str,
        reason: str,
        result: str = "SUCCESS",
        approval_id: Optional[str] = None
    ) -> Dict[str, Any]:
        prev_hash = self.chain[-1]["hash"]
        idx = len(self.chain)
        now_str = datetime.now(timezone.utc).isoformat()
        
        raw_data = f"{idx}|{now_str}|{operator}|{action}|{target}|{reason}|{result}|{approval_id}|{prev_hash}"
        curr_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

        entry = {
            "index": idx,
            "timestamp": now_str,
            "operator": operator,
            "action": action,
            "target": target,
            "reason": reason,
            "result": result,
            "approval_id": approval_id,
            "prev_hash": prev_hash,
            "hash": curr_hash
        }
        self.chain.append(entry)
        return entry

    def verify_integrity(self) -> bool:
        """Verifies hash continuity across the entire audit chain."""
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            curr = self.chain[i]
            if curr["prev_hash"] != prev["hash"]:
                return False
        return True
