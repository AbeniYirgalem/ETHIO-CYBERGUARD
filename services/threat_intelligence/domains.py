"""
ETHIO-CYBERGUARD Threat Intelligence - Malicious Domain Registry
Maintains active domain reputation indicators targeting Ethiopian organizations.
"""

from typing import Dict, Any, Optional

class DomainReputationService:
    """Evaluates domain reputation and malicious registration history."""

    KNOWN_BAD_DOMAINS = {
        "telebirr-bonus.xyz": {
            "category": "Credential Harvesting",
            "target": "Telebirr Mobile Money",
            "confidence": 99,
            "status": "BLOCKED"
        },
        "cbe-ebanking-auth.net": {
            "category": "Banking Phishing Clone",
            "target": "Commercial Bank of Ethiopia",
            "confidence": 97,
            "status": "BLOCKED"
        },
        "awash-online-verify.com": {
            "category": "Banking Phishing Clone",
            "target": "Awash Bank",
            "confidence": 95,
            "status": "BLOCKED"
        },
        "update-winsec-cloud.com": {
            "category": "Empire C2 Stager",
            "target": "Enterprise Active Directory",
            "confidence": 92,
            "status": "ACTIVE_MALICIOUS"
        }
    }

    @staticmethod
    def check_domain(domain: str) -> Dict[str, Any]:
        d_clean = domain.strip().lower()
        if d_clean in DomainReputationService.KNOWN_BAD_DOMAINS:
            rec = DomainReputationService.KNOWN_BAD_DOMAINS[d_clean]
            return {
                "domain": d_clean,
                "is_malicious": True,
                "reputation": "MALICIOUS",
                "confidence": rec["confidence"],
                "category": rec["category"],
                "target": rec["target"]
            }
        return {
            "domain": d_clean,
            "is_malicious": False,
            "reputation": "CLEAN",
            "confidence": 80
        }
