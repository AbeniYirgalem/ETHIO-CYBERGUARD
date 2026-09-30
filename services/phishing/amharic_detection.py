"""
ETHIO-CYBERGUARD Amharic Phishing Detection Engine
Detects Ge'ez / Amharic script phishing patterns, financial scam words, and regional urgency triggers.
"""

from typing import Dict, Any, List
import re

class AmharicDetector:
    """Analyzes text for Amharic psychological urgency and scam keywords."""

    # Ge'ez Unicode Block: \u1200 - \u137F
    GEEZ_RANGE_REGEX = r'[\u1200-\u137F]'

    AMHARIC_SCAM_KEYWORDS = {
        "ቴሌብር": {"weight": 25, "category": "Telebirr Brand Lure"},
        "የሽልማት": {"weight": 20, "category": "Prize / Lottery Scam"},
        "ቦነስ": {"weight": 20, "category": "Bonus Lure"},
        "አሸንፈዋል": {"weight": 20, "category": "You Have Won"},
        "ፒን": {"weight": 25, "category": "PIN / Credential Theft"},
        "ይለፍ ቃል": {"weight": 25, "category": "Password Harvesting"},
        "ያረጋግጡ": {"weight": 15, "category": "Verification Urgency"},
        "አሁኑኑ": {"weight": 15, "category": "Immediate Urgency"},
        "ኢትዮጵያ ንግድ ባንክ": {"weight": 25, "category": "Commercial Bank of Ethiopia (CBE) Impersonation"},
        "አካውንትዎ ተዘግቷል": {"weight": 30, "category": "Account Suspension Fear Lure"},
        "የባንክ ሂሳብ": {"weight": 15, "category": "Bank Account Lure"},
        "ብሔራዊ ባንክ": {"weight": 20, "category": "National Bank of Ethiopia Authority Impersonation"}
    }

    @staticmethod
    def analyze_amharic(text: str) -> Dict[str, Any]:
        has_geez = bool(re.search(AmharicDetector.GEEZ_RANGE_REGEX, text))
        detected_keywords = []
        total_weight = 0

        if has_geez:
            for kw, meta in AmharicDetector.AMHARIC_SCAM_KEYWORDS.items():
                if kw in text:
                    detected_keywords.append({
                        "keyword": kw,
                        "category": meta["category"],
                        "weight": meta["weight"]
                    })
                    total_weight += meta["weight"]

        is_amharic_phishing = total_weight >= 35

        return {
            "contains_geez_script": has_geez,
            "detected_keywords_count": len(detected_keywords),
            "keywords": detected_keywords,
            "total_amharic_weight": total_weight,
            "is_amharic_phishing": is_amharic_phishing,
            "explanation": (
                f"Amharic scam language detected with {len(detected_keywords)} high-confidence indicators "
                f"(Weight: {total_weight}). Targets regional mobile money and banking users."
                if is_amharic_phishing else "No high-risk Amharic scam patterns identified."
            )
        }
