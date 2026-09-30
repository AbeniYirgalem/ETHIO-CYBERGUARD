"""
ETHIO-CYBERGUARD Detection Severity & Priority Scoring
"""

from typing import Dict, Any

class SeverityScorer:
    """Calculates prioritized alert severities and numerical scores."""

    SEVERITY_WEIGHTS = {
        "CRITICAL": 95,
        "HIGH": 75,
        "MEDIUM": 50,
        "LOW": 25,
        "INFO": 10
    }

    @staticmethod
    def get_score(severity: str) -> int:
        return SeverityScorer.SEVERITY_WEIGHTS.get(severity.upper(), 50)

    @staticmethod
    def get_level(score: int) -> str:
        if score >= 90:
            return "CRITICAL"
        elif score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        return "INFO"
