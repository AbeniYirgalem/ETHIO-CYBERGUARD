"""
Send sample security events to a running ETHIO-CYBERGUARD API, so you can watch the
Overview page update live (feed, EPS, counters, detection toasts).

Usage (API running on port 8000):
    python scripts/demo/send_events.py
    python scripts/demo/send_events.py --count 50 --interval 0.5
    python scripts/demo/send_events.py --url http://localhost:8000 --key YOUR_INGEST_API_KEY

In DEMO_MODE the API accepts events without a key. In production (DEMO_MODE=false)
pass the INGEST_API_KEY with --key or the INGEST_API_KEY environment variable.
"""

import argparse
import os
import random
import time
import uuid
from datetime import datetime, timezone

import requests

SAMPLES = [
    {"event_type": "registry_read", "severity": "INFO", "user": "SYSTEM",
     "source": {"hostname": "SERVER-04", "ip": "10.10.1.24"},
     "process": {"name": "reg.exe", "command_line": "reg query HKLM\\SAM"}},
    {"event_type": "firewall_drop", "severity": "LOW", "user": "ingress",
     "source": {"hostname": "FW-PERIMETER-01", "ip": "10.10.0.1", "type": "firewall"},
     "network": {"source_ip": "203.0.113.50", "destination_ip": "10.10.1.24", "destination_port": 23}},
    {"event_type": "dns_lookup", "severity": "INFO", "user": "finance_clerk",
     "source": {"hostname": "LAPTOP-22", "ip": "10.10.2.22"},
     "process": {"name": "chrome.exe", "command_line": "Query: office.com"}},
    {"event_type": "authentication_failed", "severity": "MEDIUM", "user": "administrator",
     "source": {"hostname": "SERVER-04", "ip": "10.10.1.24"},
     "network": {"source_ip": "198.51.100.23", "destination_ip": "10.10.1.24", "destination_port": 3389}},
    {"event_type": "process_execution", "severity": "CRITICAL", "user": "administrator",
     "source": {"hostname": "SERVER-04", "ip": "10.10.1.24"},
     "process": {"name": "powershell.exe",
                 "command_line": "powershell.exe -NoP -NonI -W Hidden -Exec Bypass -Enc SQBFAFgAIAAoAE4AZQB3AA=="}},
    {"event_type": "network_connection", "severity": "HIGH", "user": "administrator",
     "source": {"hostname": "SERVER-04", "ip": "10.10.1.24"},
     "network": {"source_ip": "10.10.1.24", "destination_ip": "185.220.101.5", "destination_port": 443}},
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Send sample events to ETHIO-CYBERGUARD")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--key", default=os.getenv("INGEST_API_KEY"), help="collector API key (production)")
    parser.add_argument("--count", type=int, default=20, help="number of events to send")
    parser.add_argument("--interval", type=float, default=1.0, help="seconds between events")
    args = parser.parse_args()

    headers = {"X-API-Key": args.key} if args.key else {}
    endpoint = args.url.rstrip("/") + "/api/v1/events/ingest"
    ok = 0
    for i in range(args.count):
        event = dict(random.choice(SAMPLES))
        event["event_uid"] = f"demo-{uuid.uuid4()}"
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        try:
            resp = requests.post(endpoint, json=event, headers=headers, timeout=10)
        except requests.RequestException as exc:
            print(f"[{i + 1}/{args.count}] cannot reach {endpoint}: {exc}")
            return 1
        if resp.status_code == 200:
            ok += 1
            body = resp.json()
            print(f"[{i + 1}/{args.count}] {event['event_type']:<22} {event['severity']:<8} "
                  f"{body['status']} alerts={body['alerts_triggered']}")
        else:
            print(f"[{i + 1}/{args.count}] HTTP {resp.status_code}: {resp.text[:120]}")
            if resp.status_code in (401, 403):
                print("The API needs a collector key: pass --key or set INGEST_API_KEY.")
                return 1
        time.sleep(args.interval)
    print(f"Done: {ok}/{args.count} events accepted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
