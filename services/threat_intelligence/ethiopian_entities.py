"""
ETHIO-CYBERGUARD Threat Intelligence - Ethiopian Critical Infrastructure & Entities
Catalog of protected national brands, official domains, and typical adversary attack profiles.
"""

from typing import Dict, Any, List

ETHIOPIAN_ORGANIZATIONS = [
    {
        "entity_id": "ORG-CBE",
        "name": "Commercial Bank of Ethiopia",
        "short_name": "CBE",
        "sector": "Banking & Finance",
        "official_domains": ["combanketh.et", "cbe.com.et"],
        "critical_services": ["CBE Birr", "Internet Banking", "SWIFT Core", "ATM Switch"],
        "primary_threat_vectors": ["Look-alike credential harvesting", "SWIFT transaction tampering", "Ransomware"]
    },
    {
        "entity_id": "ORG-TELEBIRR",
        "name": "Telebirr Mobile Money / Ethio Telecom",
        "short_name": "Telebirr",
        "sector": "Telecom & Digital Payments",
        "official_domains": ["telebirr.et", "ethiotelecom.et"],
        "critical_services": ["Telebirr SuperApp", "USSD *127#", "Payment APIs"],
        "primary_threat_vectors": ["SMS lottery scams", "OTP harvesting", "SIM swap fraud"]
    },
    {
        "entity_id": "ORG-AWASH",
        "name": "Awash Bank",
        "short_name": "Awash",
        "sector": "Banking & Finance",
        "official_domains": ["awashbank.com"],
        "critical_services": ["Awash Birr", "Online Banking"],
        "primary_threat_vectors": ["Credential phishing", "Mobile app cloning"]
    },
    {
        "entity_id": "ORG-DASHEN",
        "name": "Dashen Bank",
        "short_name": "Dashen",
        "sector": "Banking & Finance",
        "official_domains": ["dashenbanksc.com"],
        "critical_services": ["Amole", "Dashen Internet Banking"],
        "primary_threat_vectors": ["Phishing", "API abuse"]
    },
    {
        "entity_id": "ORG-CHAPA",
        "name": "Chapa Financial Technologies",
        "short_name": "Chapa",
        "sector": "Fintech & Payment Gateway",
        "official_domains": ["chapa.co"],
        "critical_services": ["Payment API", "Merchant Checkout"],
        "primary_threat_vectors": ["API key leakage", "Webhook tampering", "Payment spoofing"]
    },
    {
        "entity_id": "ORG-INSA",
        "name": "Information Network Security Administration",
        "short_name": "INSA",
        "sector": "Government & National Cybersecurity",
        "official_domains": ["insa.gov.et"],
        "critical_services": ["National CERT Portal", "Gov-Cloud"],
        "primary_threat_vectors": ["State-sponsored APT reconnaissance", "Web defacement", "DDoS"]
    },
    {
        "entity_id": "ORG-SAFARICOM",
        "name": "Safaricom Telecommunications Ethiopia",
        "short_name": "Safaricom",
        "sector": "Telecom & Mobile Money",
        "official_domains": ["safaricom.et"],
        "critical_services": ["M-PESA Ethiopia", "GSM Network"],
        "primary_threat_vectors": ["M-PESA phishing", "Network signaling attacks"]
    }
]

def get_entity_by_domain(domain: str) -> Dict[str, Any]:
    d_clean = domain.strip().lower()
    for org in ETHIOPIAN_ORGANIZATIONS:
        for off in org["official_domains"]:
            if d_clean == off or d_clean.endswith(f".{off}"):
                return org
    return None
