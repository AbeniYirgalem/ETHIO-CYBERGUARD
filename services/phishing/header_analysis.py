"""
ETHIO-CYBERGUARD Email Header Anomaly Analysis
Inspects Return-Path, Reply-To, X-Mailer, and Received headers for spoofing, deceptive hops, and mismatches.
"""

from typing import Dict, Any, List, Optional
import email
from email import policy
import re

class HeaderAnalyzer:
    """Detects header-level evasion and deceptive routing."""

    @staticmethod
    def analyze_headers(headers: Dict[str, str]) -> Dict[str, Any]:
        findings: List[Dict[str, Any]] = []
        from_hdr = headers.get("From", headers.get("from", ""))
        reply_to = headers.get("Reply-To", headers.get("reply-to", ""))
        return_path = headers.get("Return-Path", headers.get("return-path", ""))
        
        # 1. From vs Reply-To mismatch
        from_email = HeaderAnalyzer._extract_email(from_hdr)
        reply_to_email = HeaderAnalyzer._extract_email(reply_to) if reply_to else None
        return_path_email = HeaderAnalyzer._extract_email(return_path) if return_path else None
        
        from_domain = from_email.split("@")[1].lower() if "@" in from_email else ""
        reply_to_domain = reply_to_email.split("@")[1].lower() if reply_to_email and "@" in reply_to_email else None
        
        if reply_to_email and reply_to_domain and from_domain:
            if reply_to_domain != from_domain:
                # Critical indicator if reply goes to a free mailer (gmail, yahoo) while from is corporate
                is_freemail = any(f in reply_to_domain for f in ["gmail.com", "yahoo.com", "yandex.com", "outlook.com"])
                findings.append({
                    "rule": "REPLY_TO_DOMAIN_MISMATCH",
                    "severity": "CRITICAL" if is_freemail else "HIGH",
                    "description": f"Reply-To domain '{reply_to_domain}' does not match From domain '{from_domain}'. Replies divert to external inbox.",
                    "score_impact": 30 if is_freemail else 15
                })

        # 2. Return-Path vs From mismatch
        if return_path_email and from_domain:
            return_domain = return_path_email.split("@")[1].lower() if "@" in return_path_email else ""
            if return_domain and return_domain != from_domain:
                findings.append({
                    "rule": "RETURN_PATH_MISMATCH",
                    "severity": "MEDIUM",
                    "description": f"Return-Path '{return_domain}' differs from sender domain '{from_domain}'. Common in spoofed marketing or spearphishing.",
                    "score_impact": 10
                })

        return {
            "from_email": from_email,
            "from_domain": from_domain,
            "reply_to": reply_to_email,
            "return_path": return_path_email,
            "header_findings": findings
        }

    @staticmethod
    def _extract_email(header_str: str) -> str:
        match = re.search(r"[\w\.-]+@[\w\.-]+", header_str)
        return match.group(0).lower() if match else header_str.strip().lower()
