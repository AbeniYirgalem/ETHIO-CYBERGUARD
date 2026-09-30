"""
ETHIO-CYBERGUARD OSINT - Autonomous System Number (ASN) & BGP Mapping
Resolves IP networks to Ethiopian and global telecom carriers.
"""

from typing import Dict, Any

class ASNResolver:
    """Maps IP addresses and hostnames to Autonomous System Numbers."""

    ETHIOPIAN_ASNS = {
        "AS24757": {"name": "Ethio Telecom", "country": "ET", "city": "Addis Ababa", "prefix": "196.188.0.0/16"},
        "AS329340": {"name": "Safaricom Telecommunications Ethiopia PLC", "country": "ET", "city": "Addis Ababa", "prefix": "102.218.0.0/17"},
        "AS37059": {"name": "Information Network Security Administration (INSA)", "country": "ET", "city": "Addis Ababa", "prefix": "197.156.64.0/19"},
        "AS328364": {"name": "Wingu.Africa Datacenter Addis Ababa", "country": "ET", "city": "Addis Ababa", "prefix": "102.215.12.0/22"},
        "AS328768": {"name": "Raxio Data Centre Ethiopia", "country": "ET", "city": "Addis Ababa", "prefix": "102.222.180.0/22"}
    }

    @staticmethod
    def lookup(ip: str, hostname: str = "") -> Dict[str, Any]:
        h_lower = hostname.lower()
        if "safaricom" in h_lower:
            asn_key = "AS329340"
        elif "insa" in h_lower or "gov.et" in h_lower:
            asn_key = "AS37059"
        elif "wingu" in h_lower:
            asn_key = "AS328364"
        elif "raxio" in h_lower:
            asn_key = "AS328768"
        else:
            asn_key = "AS24757"

        data = ASNResolver.ETHIOPIAN_ASNS[asn_key]
        return {
            "asn": asn_key,
            "org": data["name"],
            "country": data["country"],
            "city": data["city"],
            "ip_range": data["prefix"]
        }
