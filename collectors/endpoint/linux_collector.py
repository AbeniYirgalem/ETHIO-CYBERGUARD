#!/usr/bin/env python3
"""
ETHIO-CYBERGUARD Linux Endpoint Security Collector
Monitors /var/log/auth.log or auditd, detects unauthorized sudo, SSH brute force,
normalizes to standard schema, and streams to central ingestion API.
"""

import os
import sys
import time
import json
import socket
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone

INGEST_URL = os.environ.get("ECG_INGEST_URL", "http://localhost:8000/api/v1/events/ingest")
API_KEY = os.environ.get("ECG_API_KEY", "ecg_agent_token_dev_secret")
AUTH_LOG_PATH = os.environ.get("ECG_LOG_PATH", "/var/log/auth.log")

HOSTNAME = socket.gethostname()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

LOCAL_IP = get_local_ip()

def send_event(event_dict):
    data = json.dumps(event_dict).encode("utf-8")
    req = urllib.request.Request(INGEST_URL, data=data, headers={
        "Content-Type": "application/json",
        "X-Agent-Key": API_KEY
    })
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            pass
    except Exception as e:
        print(f"[-] Ingest delivery error: {e}", file=sys.stderr)

def parse_auth_line(line):
    # Regex patterns for SSH login / sudo
    ssh_fail = re.search(r"Failed password for (invalid user )?(\w+) from ([\d\.]+) port (\d+)", line)
    if ssh_fail:
        user = ssh_fail.group(2)
        ip = ssh_fail.group(3)
        port = int(ssh_fail.group(4))
        return {
            "event_uid": f"lin_ssh_fail_{time.time_ns()}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": {"type": "endpoint", "hostname": HOSTNAME, "ip": LOCAL_IP, "os": "Linux"},
            "event_type": "authentication_failure",
            "severity": "MEDIUM",
            "user": user,
            "network": {"source_ip": ip, "source_port": port, "destination_ip": LOCAL_IP, "destination_port": 22},
            "raw_data": {"line": line.strip()}
        }

    sudo_exec = re.search(r"sudo:\s+(\w+)\s+:\s+TTY=\S+\s+;\s+PWD=\S+\s+;\s+USER=(\w+)\s+;\s+COMMAND=(.+)", line)
    if sudo_exec:
        user = sudo_exec.group(1)
        target_user = sudo_exec.group(2)
        cmd = sudo_exec.group(3)
        return {
            "event_uid": f"lin_sudo_{time.time_ns()}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": {"type": "endpoint", "hostname": HOSTNAME, "ip": LOCAL_IP, "os": "Linux"},
            "event_type": "privilege_escalation_command",
            "severity": "HIGH" if "chmod 777" in cmd or "/bin/sh" in cmd or "curl" in cmd else "LOW",
            "user": user,
            "process": {"name": "sudo", "command_line": cmd},
            "raw_data": {"target_user": target_user, "line": line.strip()}
        }
    return None

def main():
    print(f"[*] ETHIO-CYBERGUARD Linux Collector started on {HOSTNAME} ({LOCAL_IP})")
    if not os.path.exists(AUTH_LOG_PATH):
        print(f"[!] Warning: {AUTH_LOG_PATH} not found. Running in mock daemon mode.")
        while True:
            time.sleep(10)
        return

    with open(AUTH_LOG_PATH, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
            event = parse_auth_line(line)
            if event:
                send_event(event)

if __name__ == "__main__":
    main()
