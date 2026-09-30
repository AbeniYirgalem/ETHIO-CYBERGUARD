"""
ETHIO-CYBERGUARD ECS Mapper
Transforms heterogeneous event payloads into the standard CanonicalEvent structure.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import hashlib
import uuid

from .schema import CanonicalEvent


class ECSMapper:
    """
    Normalizes logs from:
    - Windows Event Forwarding / PowerShell (EventID 4104, 4624, 4625)
    - Linux Auditd / Syslog (auth.log, syslog)
    - Perimeter Firewall (Fortinet / Palo Alto drop logs)
    - Inbound Email MTA (Postfix / Microsoft 365)
    - Brand / Domain Scanners
    """

    def normalize(self, raw: Dict[str, Any], source_type: str = "endpoint", tenant_id: str = "org_default") -> Dict[str, Any]:
        return self.map_raw_event(raw, source_type, tenant_id).to_dict()

    def map_raw_event(self, raw: Dict[str, Any], source_type: str = "endpoint", tenant_id: str = "org_default") -> CanonicalEvent:
        timestamp = raw.get("timestamp") or datetime.now(timezone.utc).isoformat()
        event_id = raw.get("event_uid") or f"evt_{uuid.uuid4().hex[:12]}"
        raw_id = raw.get("raw_event_id") or f"raw_{hashlib.sha256(str(raw).encode()).hexdigest()[:10]}"

        source_dict = raw.get("source", {}) if isinstance(raw.get("source"), dict) else {}
        network_dict = raw.get("network", {}) if isinstance(raw.get("network"), dict) else {}
        process_dict = raw.get("process", {}) if isinstance(raw.get("process"), dict) else {}
        file_dict = raw.get("file", {}) if isinstance(raw.get("file"), dict) else {}
        user_dict = raw.get("user", {}) if isinstance(raw.get("user"), dict) else {}

        # Extract observables
        observables: List[Dict[str, str]] = []
        if network_dict.get("destination_ip"):
            observables.append({"type": "ip", "value": network_dict["destination_ip"], "role": "destination_ip"})
        if raw.get("destination_ip"):
            observables.append({"type": "ip", "value": raw["destination_ip"], "role": "destination_ip"})
        if file_dict.get("hash", {}).get("sha256"):
            observables.append({"type": "hash_sha256", "value": file_dict["hash"]["sha256"], "role": "file_hash"})
        if raw.get("domain"):
            observables.append({"type": "domain", "value": raw["domain"], "role": "domain"})
        if raw.get("url"):
            observables.append({"type": "url", "value": raw["url"], "role": "url"})

        severity = raw.get("severity", "INFO").upper()
        if severity not in ["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            severity = "INFO"

        return CanonicalEvent(
            id=event_id,
            timestamp=timestamp,
            tenant_id=tenant_id,
            event_kind=raw.get("event_kind", "event"),
            event_category=[source_type, raw.get("event_category", "security")],
            event_type=[raw.get("event_type", "generic")],
            event_action=raw.get("event_action", raw.get("event_type", "observed")),
            event_outcome=raw.get("status", "success").lower(),
            severity=severity,
            source_ip=network_dict.get("source_ip") or raw.get("source_ip"),
            source_port=network_dict.get("source_port") or raw.get("source_port"),
            destination_ip=network_dict.get("destination_ip") or raw.get("destination_ip"),
            destination_port=network_dict.get("destination_port") or raw.get("destination_port"),
            user_name=user_dict.get("name") if isinstance(user_dict, dict) else (user_dict if isinstance(user_dict, str) else None),
            user_email=user_dict.get("email") if isinstance(user_dict, dict) else raw.get("user_email"),
            host_name=source_dict.get("hostname") or raw.get("host_name") or "SERVER-04",
            host_ip=source_dict.get("ip") or raw.get("host_ip") or "10.10.1.24",
            url_full=raw.get("url"),
            dns_question_name=raw.get("domain") or raw.get("dns_query"),
            process_name=process_dict.get("name"),
            process_command_line=process_dict.get("command_line"),
            file_name=file_dict.get("name"),
            file_hash_sha256=file_dict.get("hash", {}).get("sha256") if isinstance(file_dict.get("hash"), dict) else file_dict.get("hash"),
            observables=observables,
            raw_event_id=raw_id,
            mode="simulation" if raw.get("mode") == "simulation" else "production"
        )
