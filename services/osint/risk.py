"""
ETHIO-CYBERGUARD OSINT - Attack Surface Risk Scoring & Remediation Engine
"""

from typing import List, Dict, Any

class OSINTRiskCalculator:
    """Computes comprehensive attack surface risk scores with actionable hardening guidance."""

    @staticmethod
    def calculate(
        ports: List[Dict[str, Any]],
        ssl_info: Dict[str, Any],
        subdomains: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        score = 15
        findings = []
        recommendations = []

        for p in ports:
            if p["risk"] == "CRITICAL":
                score += 30
                findings.append(f"Critical port exposed to public Internet: Port {p['port']} ({p['service']})")
                recommendations.append(f"Immediately place port {p['port']} ({p['service']}) behind VPN and IP whitelist.")
            elif p["risk"] == "HIGH":
                score += 20
                findings.append(f"High-risk port exposed: Port {p['port']} ({p['service']})")
                recommendations.append(f"Restrict access to port {p['port']} to authorized management jump hosts.")

        if not ssl_info.get("has_hsts", True):
            score += 15
            findings.append("Missing HTTP Strict Transport Security (HSTS)")
            recommendations.append("Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains' header.")

        final_score = min(max(score, 10), 100)
        level = "CRITICAL" if final_score >= 75 else "HIGH" if final_score >= 50 else "MODERATE" if final_score >= 25 else "LOW"

        return {
            "attack_surface_risk_score": final_score,
            "risk_level": level,
            "findings": findings,
            "recommendations": recommendations
        }
