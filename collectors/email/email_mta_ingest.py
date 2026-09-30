"""
ETHIO-CYBERGUARD Email Ingestion Hook (MTA / Postfix / Exchange Mailbox Connector)
Pipes raw RFC-822 messages into the central ingestion & normalization pipeline.
"""

from typing import Dict, Any
from datetime import datetime, timezone
import hashlib


class EmailMTACollector:
    """
    Ingests raw email strings or files and generates standard raw collector events.
    """

    def ingest_raw_eml(self, eml_bytes_or_str: str, mailbox_user: str = "security@cbe.com.et") -> Dict[str, Any]:
        raw_text = eml_bytes_or_str if isinstance(eml_bytes_or_str, str) else eml_bytes_or_str.decode(errors="ignore")
        raw_hash = hashlib.sha256(raw_text.encode()).hexdigest()

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": {
                "type": "email_gateway",
                "hostname": "MTA-POSTFIX-01",
                "ip": "10.10.2.15"
            },
            "event_type": "inbound_email_received",
            "raw_payload": raw_text,
            "raw_event_id": f"eml_{raw_hash[:16]}",
            "user": {
                "email": mailbox_user
            }
        }
