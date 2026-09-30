"""
ETHIO-CYBERGUARD SPF (Sender Policy Framework) Verifier
Evaluates Received-SPF and Authentication-Results headers to identify sender IP spoofing.
"""

from typing import Dict, Any
import re

class SPFVerifier:
    """Verifies SPF status from email headers."""

    @staticmethod
    def evaluate(raw_headers: str, sender_domain: str) -> Dict[str, Any]:
        raw_lower = raw_headers.lower()
        if "received-spf: fail" in raw_lower or "spf=fail" in raw_lower:
            return {
                "status": "fail",
                "is_valid": False,
                "score_impact": 25,
                "detail": f"SPF validation failed for domain '{sender_domain}'. Sending MTA IP is not authorized in SPF record."
            }
        elif "received-spf: softfail" in raw_lower or "spf=softfail" in raw_lower:
            return {
                "status": "softfail",
                "is_valid": False,
                "score_impact": 15,
                "detail": f"SPF softfail: Domain '{sender_domain}' discourages sending MTA IP (~all)."
            }
        elif "received-spf: pass" in raw_lower or "spf=pass" in raw_lower:
            return {
                "status": "pass",
                "is_valid": True,
                "score_impact": 0,
                "detail": f"SPF validation passed for domain '{sender_domain}'."
            }
        return {
            "status": "none",
            "is_valid": True,
            "score_impact": 5,
            "detail": "No explicit SPF validation header observed."
        }
