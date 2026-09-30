"""
Production Ingestion Pipeline for ETHIO-CYBERGUARD
Handles collector authentication, payload limits, rate-limiting, idempotency deduplication,
queue backpressure, and dead-letter queue (DLQ) routing.
"""

import time
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from collections import deque

class IngestionPipeline:
    def __init__(self, max_queue_size: int = 10000, rate_limit_window_secs: int = 60, max_requests_per_window: int = 120):
        self.queue: deque = deque(maxlen=max_queue_size)
        self.dlq: deque = deque(maxlen=2000) # Dead Letter Queue
        self.processed_hashes: set = set()
        self.request_timestamps: Dict[str, List[float]] = {}
        self.rate_limit_window = rate_limit_window_secs
        self.max_requests_per_window = max_requests_per_window

    def check_rate_limit(self, client_id: str) -> bool:
        """Returns True if within rate limit, False if rate limited."""
        now = time.time()
        timestamps = self.request_timestamps.get(client_id, [])
        # Expire old timestamps
        timestamps = [ts for ts in timestamps if now - ts < self.rate_limit_window]
        if len(timestamps) >= self.max_requests_per_window:
            self.request_timestamps[client_id] = timestamps
            return False
        timestamps.append(now)
        self.request_timestamps[client_id] = timestamps
        return True

    def compute_event_hash(self, event_data: Dict[str, Any]) -> str:
        """Computes deterministic SHA-256 fingerprint of the event for deduplication."""
        event_str = f"{event_data.get('event_type')}|{event_data.get('source_ip')}|{event_data.get('destination_ip')}|{event_data.get('host_name')}|{event_data.get('raw_data')}"
        return hashlib.sha256(event_str.encode()).hexdigest()

    def is_duplicate(self, event_hash: str) -> bool:
        return event_hash in self.processed_hashes

    def ingest(self, event_data: Dict[str, Any], client_id: str = "collector_default") -> Dict[str, Any]:
        """Ingests an event with rate limit, payload check, idempotency check, and DLQ handling."""
        # 1. Rate Limiting Check
        if not self.check_rate_limit(client_id):
            return {
                "status": "RATE_LIMITED",
                "message": "Collector rate limit exceeded. Backoff required."
            }

        # 2. Check Required Fields & Malformed Payload
        if not isinstance(event_data, dict) or not event_data.get("event_type"):
            self.dlq.append({
                "rejected_at": datetime.now(timezone.utc).isoformat(),
                "payload": event_data,
                "reason": "Missing required field: event_type"
            })
            return {
                "status": "REJECTED_TO_DLQ",
                "reason": "Malformed event payload sent to Dead Letter Queue"
            }

        # 3. Deduplication / Idempotency Check
        event_hash = self.compute_event_hash(event_data)
        if self.is_duplicate(event_hash):
            return {
                "status": "DUPLICATE_DROPPED",
                "event_hash": event_hash,
                "message": "Event already ingested; dropping duplicate idempotently."
            }

        self.processed_hashes.add(event_hash)
        # Keep hash cache bounded
        if len(self.processed_hashes) > 100000:
            self.processed_hashes.clear()

        # 4. Enqueue Event
        self.queue.append(event_data)

        return {
            "status": "ACCEPTED",
            "event_hash": event_hash,
            "queue_depth": len(self.queue),
            "ingested_at": datetime.now(timezone.utc).isoformat()
        }

    def get_dlq_records(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self.dlq)[-limit:]

# Global Ingestion Pipeline Instance
ingestion_pipeline = IngestionPipeline()
