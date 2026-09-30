#!/usr/bin/env python3
"""
ETHIO-CYBERGUARD Synthetic Security Scenario Generator
Generates realistic telemetry for university presentations and SOC training demonstrations:
Scenarios:
- [1] Distributed SSH & RDP Brute Force
- [2] Suspicious Obfuscated PowerShell C2 Rendezvous
- [3] LSASS Memory Credential Access
- [4] Off-Hours SWIFT Directory Access
- [5] Network Port Scan Sweep
"""

import sys
import time
import json
import urllib.request
from datetime import datetime, timezone

INGEST_URL = "http://localhost:8000/api/v1/events/ingest"

def post_event(payload):
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(INGEST_URL, data=data, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            print(f"[+] Dispatched: {payload.get('event_type')} | Alerts: {res.get('alerts_triggered')}")
    except Exception as e:
        print(f"[*] Generated (Offline mode): {payload.get('event_type')} - {payload.get('severity')}")

def simulate_powershell_c2():
    print("\n--- Triggering Scenario: Obfuscated PowerShell & Cobalt Strike C2 ---")
    ev1 = {
        "event_uid": f"sim_ps_{time.time_ns()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": { "hostname": "SERVER-04", "ip": "10.10.1.24", "type": "endpoint" },
        "event_type": "process_execution",
        "severity": "CRITICAL",
        "user": "administrator",
        "process": {
            "name": "powershell.exe",
            "command_line": "powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc SQBFAFgAIAAoAE4AZQB3AC0...",
            "pid": 4812
        }
    }
    post_event(ev1)
    
    ev2 = {
        "event_uid": f"sim_net_{time.time_ns()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": { "hostname": "SERVER-04", "ip": "10.10.1.24", "type": "network" },
        "event_type": "network_connection",
        "severity": "CRITICAL",
        "user": "administrator",
        "network": { "destination_ip": "185.220.101.5", "destination_port": 443 }
    }
    post_event(ev2)

def simulate_brute_force():
    print("\n--- Triggering Scenario: Distributed SSH/RDP Brute Force ---")
    for i in range(5):
        ev = {
            "event_uid": f"sim_bf_{i}_{time.time_ns()}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": { "hostname": "FW-PERIMETER-01", "ip": "197.156.70.1", "type": "firewall" },
            "event_type": "authentication_failure",
            "severity": "HIGH",
            "user": f"root_{i}",
            "network": { "source_ip": f"45.154.255.{10+i}", "destination_port": 22 }
        }
        post_event(ev)
        time.sleep(0.2)

def main():
    print("=================================================================")
    print("🛡️ ETHIO-CYBERGUARD Synthetic Security Event Generator")
    print("=================================================================")
    simulate_powershell_c2()
    simulate_brute_force()
    print("\n[✓] Synthetic attack telemetry successfully dispatched.")

if __name__ == "__main__":
    main()
