"""
ETHIO-CYBERGUARD Perimeter Firewall Collector
Parses firewall drop / deny syslog messages (Palo Alto, Fortinet, pfSense)
and pushes them directly to the ECS normalizer.
"""

from typing import Dict, Any, Optional
import re
from datetime import datetime, timezone


class FirewallLogParser:
    """
    Parses vendor firewall messages into raw collector format.
    """

    # Sample Fortinet / Palo Alto regex
    SYSLOG_PATTERN = re.compile(
        r"src=(?P<src_ip>[\d\.]+)\s+dst=(?P<dst_ip>[\d\.]+)\s+sport=(?P<src_port>\d+)\s+dport=(?P<dst_port>\d+)\s+proto=(?P<proto>\w+)\s+action=(?P<action>\w+)"
    )

    def parse_line(self, line: str) -> Optional[Dict[str, Any]]:
        match = self.SYSLOG_PATTERN.search(line)
        if not match:
            # Fallback basic parse
            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "source": {"type": "firewall", "hostname": "FW-PERIMETER-01"},
                "event_type": "firewall_drop",
                "severity": "MEDIUM",
                "raw_payload": line
            }

        data = match.groupdict()
        action = data.get("action", "drop").lower()
        is_drop = action in ["deny", "drop", "block", "close"]

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": {"type": "firewall", "hostname": "FW-PERIMETER-01", "ip": "197.156.70.1"},
            "event_type": "firewall_drop" if is_drop else "firewall_allow",
            "event_action": action,
            "status": "blocked" if is_drop else "allowed",
            "severity": "HIGH" if (is_drop and data.get("dst_port") in ["22", "3389", "445"]) else "LOW",
            "network": {
                "source_ip": data.get("src_ip"),
                "source_port": int(data.get("src_port", 0)),
                "destination_ip": data.get("dst_ip"),
                "destination_port": int(data.get("dst_port", 0)),
                "protocol": data.get("proto", "TCP")
            },
            "raw_payload": line
        }
