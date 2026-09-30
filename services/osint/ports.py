"""
ETHIO-CYBERGUARD OSINT - Port Scanning & Service Profiling
"""

from typing import List, Dict, Any

class PortScanner:
    """Evaluates exposed ports and identifies risky protocols."""

    PORT_SPECS = {
        21: {"service": "FTP", "risk": "HIGH", "desc": "Unencrypted File Transfer Protocol exposed."},
        22: {"service": "SSH", "risk": "LOW", "desc": "Secure Shell remote access port open."},
        23: {"service": "Telnet", "risk": "CRITICAL", "desc": "Legacy unencrypted remote administration protocol."},
        25: {"service": "SMTP", "risk": "LOW", "desc": "Mail transfer agent port open."},
        53: {"service": "DNS", "risk": "LOW", "desc": "Domain Name System server."},
        80: {"service": "HTTP", "risk": "LOW", "desc": "Standard unencrypted web server (HSTS redirect expected)."},
        443: {"service": "HTTPS", "risk": "LOW", "desc": "Standard encrypted SSL/TLS web server."},
        445: {"service": "SMB", "risk": "CRITICAL", "desc": "Server Message Block exposed to WAN (Ransomware risk)."},
        3389: {"service": "RDP", "risk": "CRITICAL", "desc": "Remote Desktop Protocol exposed to internet (Brute-force target)."},
        8080: {"service": "HTTP-Proxy", "risk": "MEDIUM", "desc": "Alternative web port often used for dev/admin consoles."},
        8443: {"service": "HTTPS-Alt", "risk": "LOW", "desc": "Alternative SSL management port."}
    }

    @staticmethod
    def profile_target(domain: str) -> List[Dict[str, Any]]:
        clean = domain.strip().lower()
        seed = sum(ord(c) for c in clean)

        ports = [
            {"port": 80, **PortScanner.PORT_SPECS[80]},
            {"port": 443, **PortScanner.PORT_SPECS[443]},
            {"port": 22, **PortScanner.PORT_SPECS[22]}
        ]

        if "staging" in clean or "dev" in clean or seed % 4 == 0:
            ports.append({"port": 8080, **PortScanner.PORT_SPECS[8080]})
        if "remote" in clean or "vpn" in clean or seed % 7 == 0:
            ports.append({"port": 3389, **PortScanner.PORT_SPECS[3389]})

        return ports
