"""
ETHIO-CYBERGUARD Email Authentication Verifier
Performs SPF, DKIM, DMARC checks, and evaluates header alignment.
"""

from typing import Dict, Any, Optional
import re


class EmailAuthVerifier:
    """
    Computes authentication verdicts and detects alignment spoofing.
    Distinguishes raw cryptographic checks from RFC-7489 DMARC identity alignment.
    """

    def verify_headers(self, headers: Dict[str, str], sender_address: str) -> Dict[str, Any]:
        # Extract sender domain
        sender_match = re.search(r"[\w\.-]+@([\w\.-]+)", sender_address)
        sender_domain = sender_match.group(1).lower() if sender_match else ""

        # Extract Return-Path domain
        return_path = headers.get("return-path", "")
        return_path_match = re.search(r"[\w\.-]+@([\w\.-]+)", return_path)
        return_path_domain = return_path_match.group(1).lower() if return_path_match else None

        auth_results = headers.get("authentication-results", "").lower()
        received_spf = headers.get("received-spf", "").lower()

        # SPF Verdict
        if "spf=pass" in auth_results or "pass" in received_spf:
            spf = "PASS"
        elif "spf=fail" in auth_results or "fail" in received_spf:
            spf = "FAIL"
        elif "softfail" in received_spf or "spf=softfail" in auth_results:
            spf = "SOFTFAIL"
        else:
            spf = "NONE"

        # DKIM Verdict
        if "dkim=pass" in auth_results:
            dkim = "PASS"
        elif "dkim=fail" in auth_results:
            dkim = "FAIL"
        elif "dkim-signature" in headers:
            dkim = "PRESENT_UNVERIFIED"
        else:
            dkim = "NONE"

        # DMARC Verdict & Alignment
        is_aligned = bool(return_path_domain and sender_domain and return_path_domain == sender_domain)
        
        if "dmarc=pass" in auth_results:
            dmarc = "PASS"
        elif "dmarc=fail" in auth_results or (spf == "FAIL" and dkim == "FAIL"):
            dmarc = "FAIL"
        elif not is_aligned and spf == "PASS":
            dmarc = "ALIGNMENT_FAILED"
        else:
            dmarc = "NONE"

        alignment_issue = None
        if return_path_domain and sender_domain and return_path_domain != sender_domain:
            alignment_issue = f"Envelope sender domain '{return_path_domain}' does not align with header From '{sender_domain}'"

        return {
            "spf": spf,
            "dkim": dkim,
            "dmarc": dmarc,
            "sender_domain": sender_domain,
            "envelope_domain": return_path_domain,
            "is_aligned": is_aligned if return_path_domain else True,
            "alignment_issue": alignment_issue,
            "is_authenticated": spf == "PASS" and dkim == "PASS" and dmarc == "PASS"
        }
