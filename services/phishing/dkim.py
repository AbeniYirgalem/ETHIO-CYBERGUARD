"""
ETHIO-CYBERGUARD DKIM (DomainKeys Identified Mail) Verifier
Inspects DKIM cryptographic signatures and Authentication-Results headers.
"""

from typing import Dict, Any

class DKIMVerifier:
    """Verifies DKIM cryptographic signature status from headers."""

    @staticmethod
    def evaluate(raw_headers: str, sender_domain: str) -> Dict[str, Any]:
        raw_lower = raw_headers.lower()
        if "dkim=fail" in raw_lower:
            return {
                "status": "fail",
                "is_valid": False,
                "score_impact": 20,
                "detail": f"DKIM cryptographic signature verification failed for domain '{sender_domain}'. Message body or headers were modified in transit."
            }
        elif "dkim=pass" in raw_lower:
            return {
                "status": "pass",
                "is_valid": True,
                "score_impact": 0,
                "detail": f"DKIM signature valid and verified by recipient gateway for '{sender_domain}'."
            }
        return {
            "status": "none",
            "is_valid": True,
            "score_impact": 5,
            "detail": "No DKIM signature found in message headers."
        }
