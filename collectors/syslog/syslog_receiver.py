#!/usr/bin/env python3
"""
ETHIO-CYBERGUARD Central Syslog Listener (RFC 5424 / RFC 3164)
Receives network firewall, router, and perimeter appliance logs over UDP port 514,
normalizes and passes to message queue or direct ingestion pipeline.
"""

import socket
import json
import urllib.request
import re
from datetime import datetime, timezone

UDP_IP = "0.0.0.0"
UDP_PORT = 5140 # Port 5140 for unprivileged execution
INGEST_URL = "http://localhost:8000/api/v1/events/ingest"

def parse_syslog(msg_str, client_ip):
    # Basic RFC parser
    pri = 13
    body = msg_str
    pri_match = re.match(r"^<(\d+)>(.*)", msg_str)
    if pri_match:
        pri = int(pri_match.group(1))
        body = pri_match.group(2)

    severity_code = pri % 8
    severity_map = {
        0: "CRITICAL", 1: "CRITICAL", 2: "CRITICAL",
        3: "HIGH",     4: "MEDIUM",   5: "LOW",
        6: "INFO",     7: "INFO"
    }

    return {
        "event_uid": f"syslog_{datetime.now(timezone.utc).timestamp()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": {
            "type": "firewall_or_router",
            "hostname": f"device-{client_ip}",
            "ip": client_ip
        },
        "event_type": "network_firewall_event",
        "severity": severity_map.get(severity_code, "INFO"),
        "raw_data": {"syslog_pri": pri, "payload": body}
    }

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"[*] ETHIO-CYBERGUARD Syslog Receiver listening on UDP {UDP_IP}:{UDP_PORT}...")

    while True:
        data, addr = sock.recvfrom(4096)
        try:
            msg = data.decode("utf-8", errors="ignore")
            event = parse_syslog(msg, addr[0])
            
            req = urllib.request.Request(
                INGEST_URL, 
                data=json.dumps(event).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req, timeout=1)
        except Exception:
            pass

if __name__ == "__main__":
    main()
