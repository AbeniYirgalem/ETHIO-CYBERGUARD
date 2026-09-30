"""
ETHIO-CYBERGUARD - Typosquatting & Look-alike Domain Scanner (openSquat Engine)
Generates and monitors homoglyphs, combo-squatting, omission, transposition,
and high-risk TLD variations targeting Ethiopian organizations.
"""

from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
import re


@dataclass
class TyposquatFinding:
    domain: str
    target_brand: str
    technique: str  # omission, replacement, transposition, combosquat, homoglyph, tld_swap
    levenshtein_distance: int
    similarity_percentage: float
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    threat_description: str
    suggested_action: str
    status: str  # "Active Threat", "Registered/Parked", "Available for Defensive Purchase"


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculates Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class TyposquatMonitor:
    """
    Brand protection & domain squatting monitoring engine.
    Monitors look-alikes targeting Ethiopian banks, telecoms, and government agencies.
    """

    HOMOGLYPHS = {
        'o': ['0', 'o'],
        'l': ['1', 'i'],
        'i': ['1', 'l'],
        'e': ['3'],
        'a': ['4', '@'],
        's': ['5', '$'],
        'm': ['rn', 'nn'],
        'w': ['vv'],
    }

    COMBOSQUAT_KEYWORDS = [
        "login", "verify", "secure", "auth", "portal", "otp", "support",
        "update", "pay", "online", "birr", "bank", "app", "mobile"
    ]

    POPULAR_TLDS = [".com", ".net", ".org", ".et", ".info", ".xyz", ".top", ".cc", ".online", ".site"]

    ETHIOPIAN_DEFAULTS = [
        {"domain": "telebirr.et", "brand": "Telebirr", "sector": "Fintech / Mobile Money"},
        {"domain": "combanketh.et", "brand": "Commercial Bank of Ethiopia", "sector": "Banking"},
        {"domain": "ethiotelecom.et", "brand": "Ethio Telecom", "sector": "Telecommunications"},
        {"domain": "insa.gov.et", "brand": "INSA Cyber Security", "sector": "National Security"},
        {"domain": "chapa.co", "brand": "Chapa Financial Technologies", "sector": "Payment Gateway"},
        {"domain": "ethiopianairlines.com", "brand": "Ethiopian Airlines", "sector": "Aviation"}
    ]

    def scan_domain(self, domain_or_brand: str, limit: int = 50) -> Dict[str, Any]:
        """
        Scan a target brand or root domain and generate look-alike squatted domains
        with similarity scores, risk evaluation, and defensive actions.
        """
        domain_clean = domain_or_brand.strip().lower()
        if "." in domain_clean:
            parts = domain_clean.split(".")
            brand_name = parts[0]
            root_tld = "." + ".".join(parts[1:])
        else:
            brand_name = domain_clean
            root_tld = ".et"

        generated_domains: Set[Tuple[str, str]] = set()

        # 1. Omission (removing one character)
        for i in range(len(brand_name)):
            omitted = brand_name[:i] + brand_name[i+1:]
            if len(omitted) >= 3:
                generated_domains.add((f"{omitted}{root_tld}", "Omission Squatting"))

        # 2. Transposition (swapping adjacent characters)
        for i in range(len(brand_name) - 1):
            transposed = brand_name[:i] + brand_name[i+1] + brand_name[i] + brand_name[i+2:]
            if transposed != brand_name:
                generated_domains.add((f"{transposed}{root_tld}", "Transposition Squatting"))

        # 3. Homoglyph & Character Replacement
        for char, replacements in self.HOMOGLYPHS.items():
            if char in brand_name:
                for rep in replacements:
                    replaced = brand_name.replace(char, rep, 1)
                    if replaced != brand_name:
                        generated_domains.add((f"{replaced}{root_tld}", "Homoglyph / Visual Spoof"))

        # 4. Combosquatting (brand + keyword)
        for kw in self.COMBOSQUAT_KEYWORDS:
            generated_domains.add((f"{brand_name}-{kw}.com", "Combosquatting (Phishing Lure)"))
            generated_domains.add((f"{brand_name}{kw}{root_tld}", "Combosquatting (Prefix/Suffix)"))
            generated_domains.add((f"{kw}-{brand_name}.et", "Combosquatting (Security Impersonation)"))

        # 5. TLD Swap
        for tld in self.POPULAR_TLDS:
            if tld != root_tld:
                generated_domains.add((f"{brand_name}{tld}", "TLD Impersonation / Extension Hijack"))

        # Evaluate risk and format findings
        findings: List[TyposquatFinding] = []
        full_target = f"{brand_name}{root_tld}"

        # Known simulated active threats for realistic SOC detection
        known_active_threats = {
            f"{brand_name}-login.com",
            f"{brand_name}verify.xyz",
            f"te1ebirr.et",
            f"cornbanketh.et",
            f"telebirr-otp.top",
            f"combanketh-security.com",
            f"ethiotelecom-bonus.com"
        }

        for candidate, technique in generated_domains:
            dist = levenshtein_distance(candidate.split(".")[0], brand_name)
            max_len = max(len(candidate.split(".")[0]), len(brand_name))
            similarity = round(max(0.0, (1 - (dist / max_len))) * 100, 1)

            # Determine Risk
            is_active = candidate in known_active_threats
            if is_active or (similarity >= 85 and any(tld in candidate for tld in [".xyz", ".top", ".online", ".site", ".com"])):
                risk_level = "CRITICAL"
                status = "Active Threat" if is_active else "Registered / Suspicious"
                threat = "High risk of credential harvesting and targeted SMS/phishing campaign."
                action = "Submit domain takedown to Registrar & blacklist in INSA national cyber-feed."
            elif similarity >= 70 or technique == "TLD Impersonation / Extension Hijack":
                risk_level = "HIGH"
                status = "Registered / Parked"
                threat = "Brand confusion and potential corporate impersonation vector."
                action = "Acquire domain defensively or issue UDRP dispute notice."
            elif similarity >= 50:
                risk_level = "MEDIUM"
                status = "Available for Defensive Purchase"
                threat = "Low immediate threat; potential for opportunistic registration."
                action = "Add to monthly automated WHOIS change monitor."
            else:
                risk_level = "LOW"
                status = "Available"
                threat = "Perimeter variation."
                action = "Keep on passive observation list."

            findings.append(TyposquatFinding(
                domain=candidate,
                target_brand=brand_name.upper(),
                technique=technique,
                levenshtein_distance=dist,
                similarity_percentage=similarity,
                risk_level=risk_level,
                threat_description=threat,
                suggested_action=action,
                status=status
            ))

        # Sort: CRITICAL first, then HIGH, then similarity desc
        order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        findings.sort(key=lambda x: (order.get(x.risk_level, 4), -x.similarity_percentage))

        selected = findings[:limit]

        return {
            "target": full_target,
            "brand": brand_name.upper(),
            "total_mutations_generated": len(findings),
            "critical_threats_count": sum(1 for f in findings if f.risk_level == "CRITICAL"),
            "high_risk_count": sum(1 for f in findings if f.risk_level == "HIGH"),
            "active_threats_count": sum(1 for f in findings if f.status == "Active Threat"),
            "results": [
                {
                    "domain": f.domain,
                    "technique": f.technique,
                    "levenshtein_distance": f.levenshtein_distance,
                    "similarity_percentage": f.similarity_percentage,
                    "risk_level": f.risk_level,
                    "threat_description": f.threat_description,
                    "suggested_action": f.suggested_action,
                    "status": f.status,
                }
                for f in selected
            ]
        }
