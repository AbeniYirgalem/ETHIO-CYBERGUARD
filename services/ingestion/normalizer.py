"""
ETHIO-CYBERGUARD Event Ingestion & Normalization Engine
Converts disparate raw logs into the unified standard schema.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import hashlib

class EventNormalizer:
    """
    Standardizes endpoint, network, firewall, and cloud logs into a unified ECS-like security event schema.
    """

    def normalize(self, raw_event: Dict[str, Any], source_type: str = "endpoint") -> Dict[str, Any]:
        timestamp = raw_event.get("timestamp") or datetime.now(timezone.utc).isoformat()
        
        # Extract or generate unique event UID
        event_uid = raw_event.get("event_uid")
        if not event_uid:
            hash_input = f"{timestamp}-{raw_event.get('user', '')}-{raw_event.get('event_type', '')}"
            event_uid = f"ecg_{hashlib.sha256(hash_input.encode()).hexdigest()[:16]}"

        source_info = raw_event.get("source") or {}
        if not isinstance(source_info, dict):
            source_info = {}
        if "hostname" not in source_info and raw_event.get("host_name"):
            source_info["hostname"] = raw_event.get("host_name")
        if "ip" not in source_info and raw_event.get("source_ip"):
            source_info["ip"] = raw_event.get("source_ip")

        process_info = raw_event.get("process") or {}
        if not isinstance(process_info, dict):
            process_info = {}

        network_info = raw_event.get("network") or {}
        if not isinstance(network_info, dict):
            network_info = {}
        if "source_ip" not in network_info and raw_event.get("source_ip"):
            network_info["source_ip"] = raw_event.get("source_ip")
        if "destination_ip" not in network_info and raw_event.get("destination_ip"):
            network_info["destination_ip"] = raw_event.get("destination_ip")

        # Compute normalized severity
        severity = raw_event.get("severity", "INFO").upper()
        if severity not in ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            severity = "INFO"

        normalized = {
            "event_id": event_uid,
            "timestamp": timestamp,
            "source": {
                "type": source_info.get("type", source_type),
                "hostname": source_info.get("hostname", "SERVER-04"),
                "ip": source_info.get("ip", "10.10.1.24"),
                "os": source_info.get("os", "Windows")
            },
            "event_type": raw_event.get("event_type", "generic_security_event"),
            "severity": severity,
            "user": raw_event.get("user", "SYSTEM"),
            "process": {
                "name": process_info.get("name"),
                "path": process_info.get("path"),
                "command_line": process_info.get("command_line"),
                "pid": process_info.get("pid")
            },
            "network": {
                "source_ip": network_info.get("source_ip"),
                "source_port": network_info.get("source_port"),
                "destination_ip": network_info.get("destination_ip"),
                "destination_port": network_info.get("destination_port"),
                "protocol": network_info.get("protocol", "TCP")
            },
            "enrichment": {
                "geo_location": self._enrich_geo(network_info.get("destination_ip") or source_info.get("ip")),
                "is_internal_network": self._is_internal(source_info.get("ip", "")),
                "ingested_at": datetime.now(timezone.utc).isoformat()
            },
            "source_ip": source_info.get("ip") or network_info.get("source_ip") or raw_event.get("source_ip"),
            "destination_ip": network_info.get("destination_ip") or raw_event.get("destination_ip"),
            "host_name": source_info.get("hostname") or raw_event.get("host_name"),
            "raw_data": raw_event.get("raw_data", {})
        }
        return normalized

    def _is_internal(self, ip: str) -> bool:
        if not ip:
            return False
        return ip.startswith("10.") or ip.startswith("192.168.") or ip.startswith("172.16.")

    def _enrich_geo(self, ip: Optional[str]) -> Dict[str, str]:
        if not ip:
            return {"country": "Unknown", "city": "Unknown"}
        if ip.startswith("197.156.") or ip.startswith("213.55."):
            return {"country": "Ethiopia", "city": "Addis Ababa", "org": "Ethio Telecom"}
        if ip.startswith("185.220."):
            return {"country": "Germany", "city": "Tor Exit Relay", "reputation": "MALICIOUS"}
        return {"country": "External", "city": "Unknown"}
