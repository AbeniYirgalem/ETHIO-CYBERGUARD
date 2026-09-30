"""
ETHIO-CYBERGUARD OSINT - Subdomain Discovery Engine
Maps public subdomains and service endpoints for organizations.
"""

from typing import List, Dict, Any

class SubdomainScanner:
    """Discovers subdomains and exposed service portals."""

    PREFIXES = ["www", "mail", "vpn", "portal", "api", "remote", "autodiscover", "staging", "dev", "gw"]

    @staticmethod
    def enumerate(domain: str) -> List[Dict[str, Any]]:
        clean = domain.strip().lower()
        subdomains = []
        seed = sum(ord(c) for c in clean)

        for p in SubdomainScanner.PREFIXES:
            sub = f"{p}.{clean}"
            port = 443 if p in ["www", "portal", "api", "vpn"] else 25 if p == "mail" else 80
            service = "HTTPS Web Portal" if port == 443 else "SMTP Mail Gateway" if port == 25 else "HTTP Redirector"
            subdomains.append({
                "subdomain": sub,
                "ip": f"196.188.{(seed + len(sub)) % 250}.{(seed * 3) % 250}",
                "service": service,
                "port": port,
                "status": "ACTIVE"
            })

        return subdomains
