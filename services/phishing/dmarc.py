"""
ETHIO-CYBERGUARD DMARC (Domain-based Message Authentication, Reporting, and Conformance) Verifier
Evaluates domain alignment and DMARC enforcement policy results.
"""

from typing import Dict, Any

class DMARCVerifier:
    """Verifies DMARC compliance and policy enforcement from headers."""

    @staticmethod
    def evaluate(raw_headers: str, sender_domain: str) -> Dict[str, Any]:
        raw_lower = raw_headers.lower()
        if "dmarc=fail" in raw_lower:
            return {
                "status": "fail",
                "is_valid": False,
                "score_impact": 25,
                "detail": f"DMARC policy alignment check FAILED for domain '{sender_domain}'. Message failed both SPF and DKIM alignment criteria."
            }
        elif "dmarc=pass" in raw_lower:
            return {
                "status": "pass",
                "is_valid": True,
                "score_impact": 0,
                "detail": f"DMARC alignment passed for '{sender_domain}'."
            }
        return {
            "status": "none",
            "is_valid": True,
            "score_impact": 5,
            "detail": "No explicit DMARC evaluation result recorded."
        }
