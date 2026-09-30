"""
ETHIO-CYBERGUARD URL Inspection & Link Analysis Engine
Detects raw IP hosts, suspicious TLDs, typosquatting domains, and credential-harvesting URI patterns.
"""

from typing import List, Dict, Any
import re
from urllib.parse import urlparse

class URLAnalyzer:
    """Analyzes links extracted from email bodies or HTML parts."""

    SUSPICIOUS_TLDS = {".xyz", ".top", ".club", ".icu", ".work", ".click", ".buzz", ".monster", ".fit"}
    HARVESTING_PATHS = ["login", "signin", "verify", "claim", "secure", "update", "banking", "kyc", "otp", "pin", "auth"]

    @staticmethod
    def extract_and_analyze_urls(body_text: str) -> List[Dict[str, Any]]:
        url_regex = r'https?://[^\s<>"\')]+'
        matches = re.findall(url_regex, body_text)
        findings = []

        for url_str in matches:
            clean_url = url_str.rstrip(".,;>")
            try:
                parsed = urlparse(clean_url)
                netloc = parsed.netloc.lower()
                path = parsed.path.lower()
            except Exception:
                continue

            # Check if domain is a direct IP
            host_only = netloc.split(":")[0]
            is_ip = any(char.isdigit() for char in host_only) and all(part.isdigit() for part in host_only.split(".") if len(host_only.split(".")) == 4)

            # Check suspicious TLD
            has_suspicious_tld = any(netloc.endswith(tld) for tld in URLAnalyzer.SUSPICIOUS_TLDS)
            
            # Check harvesting path keywords
            has_harvest_path = any(kw in path for kw in URLAnalyzer.HARVESTING_PATHS)

            # Scoring impact
            points = 0
            reasons = []
            if is_ip:
                points += 35
                reasons.append("Raw IPv4 address used in URL instead of legitimate domain name")
            if has_suspicious_tld:
                points += 20
                reasons.append("High-abuse top-level domain (.xyz, .top, .click, etc.)")
            if has_harvest_path:
                points += 15
                reasons.append("Credential or identity harvesting keyword in URI path (login, verify, kyc, pin)")
            if "telebirr" in netloc and not netloc.endswith("telebirr.et"):
                points += 35
                reasons.append("Telebirr brand impersonation in third-party domain")
            if "cbe" in netloc and not (netloc.endswith("combanketh.et") or netloc.endswith("cbe.com.et")):
                points += 35
                reasons.append("Commercial Bank of Ethiopia (CBE) brand impersonation in domain")

            findings.append({
                "url": clean_url,
                "domain": netloc,
                "is_ip_based": is_ip,
                "is_suspicious": points >= 20,
                "risk_points": points,
                "reasons": reasons
            })

        return findings
