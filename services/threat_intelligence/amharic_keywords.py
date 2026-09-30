"""
ETHIO-CYBERGUARD Threat Intelligence - Amharic Cyber Threat Keywords
Curated dictionary of terms frequently utilized in Ethiopian social engineering campaigns.
"""

from typing import Dict, Any, List

THREAT_KEYWORDS = {
    "FINANCIAL_SCAM": [
        {"term": "የ10,000 ብር ሽልማት", "translation": "10,000 Birr prize", "threat": "Lottery scam lure"},
        {"term": "ቴሌብር ቦነስ", "translation": "Telebirr bonus", "threat": "Mobile money lure"},
        {"term": "የባንክ አካውንትዎ ተዘግቷል", "translation": "Your bank account is closed", "threat": "Fear/Panic trigger"}
    ],
    "CREDENTIAL_HARVEST": [
        {"term": "የቴሌብር ፒን ያስገቡ", "translation": "Enter your Telebirr PIN", "threat": "Direct PIN theft"},
        {"term": "የይለፍ ቃል ማደሻ", "translation": "Password reset", "threat": "Credential harvesting"},
        {"term": "የኦቲፒ (OTP) ቁጥር", "translation": "OTP code", "threat": "2FA bypass lure"}
    ],
    "AUTHORITY_IMPERSONATION": [
        {"term": "ከብሔራዊ ባንክ የተላለፈ", "translation": "Transmitted from National Bank", "threat": "Regulatory spoofing"},
        {"term": "የኢንሳ የደህንነት ማስጠንቀቂያ", "translation": "INSA security notice", "threat": "Cyber agency impersonation"}
    ]
}

def scan_text_for_threat_keywords(text: str) -> List[Dict[str, Any]]:
    matches = []
    for cat, items in THREAT_KEYWORDS.items():
        for item in items:
            if item["term"] in text:
                matches.append({"category": cat, **item})
    return matches
