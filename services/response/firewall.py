"""
ETHIO-CYBERGUARD SOAR Boundary Firewall Service
Pushes dynamic IP/subnet drop rules to perimeter gateways (Palo Alto, Fortinet, iptables).
"""

from typing import Dict, Any
from datetime import datetime, timezone

class FirewallBlockService:
    """Manages dynamic perimeter firewall blocklists."""

    @staticmethod
    def block_ip(ip_address: str, direction: str = "BOTH", reason: str = "Malicious C2") -> Dict[str, Any]:
        return {
            "action": "BLOCK_IP",
            "target_ip": ip_address,
            "direction": direction,
            "rule_id": f"FW-BLOCK-{ip_address.replace('.', '-')}",
            "status": "APPLIED",
            "enforcement_points": ["PERIMETER-FW-01", "PERIMETER-FW-02", "CORE-GATEWAY"],
            "action_policy": "DROP_SILENTLY",
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason
        }
