"""
ETHIO-CYBERGUARD Phishing Risk Scoring Engine
Calculates weighted composite threat scores with explainable evidence attribution.
"""

from typing import Dict, Any, List


class PhishingRiskScorer:
    """
    Computes deterministic phishing verdicts with explicit evidence references.
    """

    def score_email(
        self,
        auth_data: Dict[str, Any],
        has_reply_to_mismatch: bool,
        suspicious_urls: List[Dict[str, Any]],
        brand_spoof: bool,
        amharic_threat_cues: bool,
        urgency_score: int
    ) -> Dict[str, Any]:
        score = 0
        evidence: List[str] = []

        # 1. Authentication failures
        if auth_data.get("dmarc") == "FAIL":
            score += 30
            evidence.append("DMARC alignment check failed completely")
        elif auth_data.get("alignment_issue"):
            score += 20
            evidence.append(auth_data["alignment_issue"])

        if auth_data.get("spf") == "FAIL":
            score += 20
            evidence.append("SPF record validation failed: unauthorized sender IP")

        if auth_data.get("dkim") == "FAIL":
            score += 20
            evidence.append("Cryptographic DKIM body signature verification failed")

        # 2. Reply-To mismatch
        if has_reply_to_mismatch:
            score += 25
            evidence.append("Reply-To header domain does not match visible sender address")

        # 3. Malicious URLs
        for u in suspicious_urls:
            score += u.get("risk_weight", 15)
            evidence.append(f"Suspicious URL: {u['url']} ({u.get('reason', 'Risky link')})")

        # 4. Brand spoofing
        if brand_spoof:
            score += 35
            evidence.append("Unauthorized brand impersonation targeting Ethiopian financial/telecom institutions")

        # 5. Regional language & urgency
        if amharic_threat_cues:
            score += 25
            evidence.append("Regional Amharic fraud keywords detected (PIN/OTP harvesting lure)")

        if urgency_score > 0:
            score += min(urgency_score, 20)
            evidence.append("Aggressive psychological urgency and account suspension threats")

        final_score = min(max(score, 5), 100)

        if final_score >= 70:
            classification = "CRITICAL_PHISHING"
            confidence = 0.96
        elif final_score >= 45:
            classification = "SUSPICIOUS"
            confidence = 0.88
        else:
            classification = "BENIGN"
            confidence = 0.94

        return {
            "score": final_score,
            "classification": classification,
            "confidence": confidence,
            "evidence": evidence
        }
