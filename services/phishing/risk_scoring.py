"""
ETHIO-CYBERGUARD Phishing Risk Scoring Engine
Calculates weighted composite threat scores with explainable evidence attribution.
"""

from typing import Dict, Any, List
from .risk_scorer import PhishingRiskScorer

class ExplainableRiskScorer(PhishingRiskScorer):
    """Extends PhishingRiskScorer to output structured score breakdown items."""

    def compute_detailed_score(
        self,
        auth_data: Dict[str, Any],
        has_reply_to_mismatch: bool,
        suspicious_urls: List[Dict[str, Any]],
        brand_spoof: bool,
        amharic_threat_cues: bool,
        urgency_score: int
    ) -> Dict[str, Any]:
        base_result = self.score_email(
            auth_data=auth_data,
            has_reply_to_mismatch=has_reply_to_mismatch,
            suspicious_urls=suspicious_urls,
            brand_spoof=brand_spoof,
            amharic_threat_cues=amharic_threat_cues,
            urgency_score=urgency_score
        )

        breakdown = []
        if auth_data.get("dmarc") == "FAIL":
            breakdown.append({"factor": "DMARC Failure", "points": 30, "description": "Sender failed DMARC domain alignment policy"})
        if auth_data.get("spf") == "FAIL":
            breakdown.append({"factor": "SPF Failure", "points": 20, "description": "Sending IP not authorized in SPF record"})
        if auth_data.get("dkim") == "FAIL":
            breakdown.append({"factor": "DKIM Failure", "points": 20, "description": "DKIM digital signature invalid or missing"})
        if has_reply_to_mismatch:
            breakdown.append({"factor": "Reply-To Mismatch", "points": 25, "description": "Reply-To directs responses to external address"})
        if suspicious_urls:
            breakdown.append({"factor": "Malicious URLs", "points": 25, "description": f"{len(suspicious_urls)} deceptive or IP-based links"})
        if brand_spoof:
            breakdown.append({"factor": "Brand Impersonation", "points": 35, "description": "Unauthorized impersonation of Ethiopian entity"})
        if amharic_threat_cues:
            breakdown.append({"factor": "Amharic Fraud Lure", "points": 25, "description": "Regional language lottery/PIN harvest phrasing"})

        base_result["breakdown"] = breakdown
        return base_result
