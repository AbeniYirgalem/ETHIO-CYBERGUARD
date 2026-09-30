"""
ETHIO-CYBERGUARD Event Schema Validators
Validates canonical schema conformance and provides prompt-injection sanitization.
"""

from typing import Dict, Any, Tuple
import re

from .schema import CanonicalEvent


class EventValidator:
    """
    Validates canonical event structures and enforces untrusted data tagging.
    """

    @staticmethod
    def validate_event(event: CanonicalEvent) -> Tuple[bool, str]:
        if not event.id:
            return False, "Missing event ID"
        if not event.timestamp:
            return False, "Missing timestamp"
        if not event.event_category:
            return False, "Missing event category"
        if event.severity not in ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            return False, f"Invalid severity: {event.severity}"
        return True, "Valid"

    @staticmethod
    def sanitize_untrusted_log(raw_text: str) -> str:
        """
        Strips or escapes prompt-injection sequences from attacker-controlled event text.
        Ensures raw text is strictly marked as UNTRUSTED_DATA before LLM ingestion.
        """
        if not raw_text:
            return ""

        # Normalize common prompt injection triggers
        sanitized = re.sub(r"(?i)(ignore\s+all\s+previous\s+instructions|system\s*prompt|you\s+are\s+now|disregard\s+prior)", "[REDACTED_INJECTION_TRIGGER]", raw_text)
        return f"<UNTRUSTED_LOG_DATA>{sanitized}</UNTRUSTED_LOG_DATA>"
