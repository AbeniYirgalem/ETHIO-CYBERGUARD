"""
ETHIO-CYBERGUARD Entity Resolution Service
Resolves and links disparate telemetry identifiers (IP, MAC, Hostname, Active Directory Username).
"""

from typing import Dict, Any, Optional

class EntityResolver:
    """Links disparate entities into unified asset/identity records."""

    ASSET_DIRECTORY = {
        "10.10.1.24": {"hostname": "SERVER-04", "os": "Windows Server 2022", "department": "Core Banking Infrastructure", "owner": "Dawit Mengistu"},
        "197.156.70.1": {"hostname": "FW-PERIMETER-01", "os": "Palo Alto PanOS", "department": "Network Security", "owner": "Sara Yohannes"},
        "10.10.4.88": {"hostname": "LAPTOP-FINANCE-22", "os": "Windows 11 Enterprise", "department": "Treasury & SWIFT Processing", "owner": "Yared Tadesse"}
    }

    @staticmethod
    def resolve_ip(ip: str) -> Dict[str, Any]:
        return EntityResolver.ASSET_DIRECTORY.get(ip, {
            "hostname": f"HOST-{ip.replace('.', '-')}",
            "os": "Unknown",
            "department": "Unassigned Subnet",
            "owner": "Unknown"
        })

    @staticmethod
    def link_entities(events: list) -> Dict[str, Any]:
        hosts = set()
        users = set()
        ips = set()
        for ev in events:
            if ev.get("source", {}).get("hostname"):
                hosts.add(ev["source"]["hostname"])
            if ev.get("user"):
                users.add(ev["user"])
            if ev.get("source", {}).get("ip"):
                ips.add(ev["source"]["ip"])
        return {
            "primary_host": list(hosts)[0] if hosts else "SERVER-04",
            "primary_user": list(users)[0] if users else "administrator",
            "all_hosts": list(hosts),
            "all_users": list(users),
            "all_ips": list(ips)
        }
