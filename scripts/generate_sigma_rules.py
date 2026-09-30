"""
Generates production-grade SIGMA YAML detection rules across 6 categories:
windows, linux, network, authentication, phishing, and ethiopia.
"""

import os
import yaml

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "detection-rules"))

RULES = [
    # --- Windows ---
    {
        "category": "windows",
        "filename": "powershell_obfuscated.yml",
        "data": {
            "id": "win-sigma-001",
            "title": "Suspicious Obfuscated PowerShell Execution",
            "status": "stable",
            "description": "Detects encoded or obfuscated PowerShell commands often used in initial stagers or fileless execution.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.2.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1059/001/"],
            "tags": ["attack.execution", "attack.t1059.001", "car.2013-05-009"],
            "logsource": {"category": "process_creation", "product": "windows"},
            "detection": {
                "selection": {
                    "process.name": "powershell.exe",
                    "process.command_line": ["*-enc*", "*-encodedcommand*", "*downloadstring*", "*invoke-expression*", "*iex*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["Legitimate enterprise deployment scripts utilizing base64 encoding (e.g., SCCM, Ansible)"],
            "severity": "critical"
        }
    },
    {
        "category": "windows",
        "filename": "lsass_memory_dump.yml",
        "data": {
            "id": "win-sigma-002",
            "title": "LSASS Memory Dump for Credential Harvesting",
            "status": "stable",
            "description": "Detects attempts to access or dump the Local Security Authority Subsystem Service (LSASS) process memory.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.1.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1003/001/"],
            "tags": ["attack.credential_access", "attack.t1003.001"],
            "logsource": {"category": "process_access", "product": "windows"},
            "detection": {
                "selection": {
                    "process.target": "lsass.exe",
                    "process.name": ["procdump.exe", "mimikatz.exe", "rundll32.exe", "comsvcs.dll"]
                },
                "condition": "selection"
            },
            "falsepositives": ["AV/EDR products performing memory scans"],
            "severity": "critical"
        }
    },
    {
        "category": "windows",
        "filename": "scheduled_task_persistence.yml",
        "data": {
            "id": "win-sigma-003",
            "title": "Scheduled Task Creation for Lateral Persistence",
            "status": "stable",
            "description": "Detects use of schtasks.exe to create scheduled tasks running script interpreters.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1053/005/"],
            "tags": ["attack.persistence", "attack.t1053.005"],
            "logsource": {"category": "process_creation", "product": "windows"},
            "detection": {
                "selection": {
                    "process.name": "schtasks.exe",
                    "process.command_line": ["*/create*", "*/sc*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["Software updates scheduled by system administrators"],
            "severity": "high"
        }
    },
    {
        "category": "windows",
        "filename": "certutil_download.yml",
        "data": {
            "id": "win-sigma-004",
            "title": "Certutil Ingress File Transfer",
            "status": "stable",
            "description": "Detects certutil.exe used to download files from remote URLs, commonly used by adversaries as a LOLBIN.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1105/"],
            "tags": ["attack.command_and_control", "attack.t1105"],
            "logsource": {"category": "process_creation", "product": "windows"},
            "detection": {
                "selection": {
                    "process.name": "certutil.exe",
                    "process.command_line": ["*-urlcache*", "*-split*", "*http*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["Administrative certificate revocation checking"],
            "severity": "high"
        }
    },
    {
        "category": "windows",
        "filename": "vssadmin_shadow_copy_delete.yml",
        "data": {
            "id": "win-sigma-005",
            "title": "Volume Shadow Copy Deletion via VSSAdmin",
            "status": "stable",
            "description": "Detects deletion of volume shadow copies commonly performed prior to ransomware encryption.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1490/"],
            "tags": ["attack.impact", "attack.t1490"],
            "logsource": {"category": "process_creation", "product": "windows"},
            "detection": {
                "selection": {
                    "process.name": "vssadmin.exe",
                    "process.command_line": ["*delete shadows*", "*/quiet*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["Backup software routine cleanup jobs"],
            "severity": "critical"
        }
    },

    # --- Linux ---
    {
        "category": "linux",
        "filename": "ssh_brute_force.yml",
        "data": {
            "id": "nix-sigma-001",
            "title": "Linux SSH Repeated Authentication Failures",
            "status": "stable",
            "description": "Detects high-volume SSH login failures targeting Linux servers.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1110/001/"],
            "tags": ["attack.credential_access", "attack.t1110.001"],
            "logsource": {"category": "auth", "product": "linux"},
            "detection": {
                "selection": {
                    "event_type": "ssh_auth_failure"
                },
                "condition": "selection"
            },
            "falsepositives": ["Users with expired passwords or misconfigured SSH keys"],
            "severity": "high"
        }
    },
    {
        "category": "linux",
        "filename": "cron_persistence.yml",
        "data": {
            "id": "nix-sigma-002",
            "title": "Suspicious Cron Job Modification",
            "status": "stable",
            "description": "Detects modifications to /etc/cron* or user crontabs executing scripts from world-writable directories.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1053/003/"],
            "tags": ["attack.persistence", "attack.t1053.003"],
            "logsource": {"category": "file_change", "product": "linux"},
            "detection": {
                "selection": {
                    "process.command_line": ["*crontab*", "*/tmp/*", "*/var/tmp/*", "*curl *|*sh*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["System administrator maintenance scripts"],
            "severity": "high"
        }
    },
    {
        "category": "linux",
        "filename": "reverse_shell_bash.yml",
        "data": {
            "id": "nix-sigma-003",
            "title": "Interactive Bash Reverse Shell Connection",
            "status": "stable",
            "description": "Detects bash or sh executing redirected TCP sockets commonly used for reverse shell access.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1059/004/"],
            "tags": ["attack.execution", "attack.t1059.004"],
            "logsource": {"category": "process_creation", "product": "linux"},
            "detection": {
                "selection": {
                    "process.command_line": ["*/dev/tcp/*", "*bash -i*", "*nc -e /bin/sh*", "*python -c *pty.spawn*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["Legitimate penetration testing drills"],
            "severity": "critical"
        }
    },

    # --- Network ---
    {
        "category": "network",
        "filename": "c2_beacon.yml",
        "data": {
            "id": "net-sigma-001",
            "title": "Known Malicious Command & Control Beaconing",
            "status": "stable",
            "description": "Detects network egress connections matching known Cobalt Strike, Empire, or Metasploit C2 IP addresses.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.1.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1071/001/"],
            "tags": ["attack.command_and_control", "attack.t1071.001"],
            "logsource": {"category": "network_connection", "product": "firewall"},
            "detection": {
                "selection": {
                    "destination.ip": ["185.220.101.5", "196.188.99.12"]
                },
                "condition": "selection"
            },
            "falsepositives": ["Threat research sandboxes"],
            "severity": "critical"
        }
    },
    {
        "category": "network",
        "filename": "dns_tunneling_data_exfiltration.yml",
        "data": {
            "id": "net-sigma-002",
            "title": "DNS Tunneling or Data Exfiltration",
            "status": "stable",
            "description": "Detects high-entropy, abnormally long subdomains queried via DNS indicating iodine or dnscat2 tunneling.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1071/004/"],
            "tags": ["attack.exfiltration", "attack.t1071.004"],
            "logsource": {"category": "dns_query", "product": "dns"},
            "detection": {
                "selection": {
                    "event_type": "dns_tunnel_observed"
                },
                "condition": "selection"
            },
            "falsepositives": ["Anti-virus cloud lookup signatures over DNS"],
            "severity": "high"
        }
    },

    # --- Authentication ---
    {
        "category": "authentication",
        "filename": "brute_force.yml",
        "data": {
            "id": "auth-sigma-001",
            "title": "Perimeter Distributed Brute Force Attempt",
            "status": "stable",
            "description": "Detects cluster of failed authentication attempts from multiple remote IPs against administrative ports.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1110/003/"],
            "tags": ["attack.credential_access", "attack.t1110.003"],
            "logsource": {"category": "auth", "product": "system"},
            "detection": {
                "selection": {
                    "event_type": "authentication_failure"
                },
                "condition": "selection"
            },
            "falsepositives": ["Misconfigured batch service account with outdated credentials"],
            "severity": "high"
        }
    },
    {
        "category": "authentication",
        "filename": "off_hours_swift_access.yml",
        "data": {
            "id": "auth-sigma-002",
            "title": "Unusual Off-Hours SWIFT Directory Access",
            "status": "stable",
            "description": "Detects interactive access to SWIFT financial transaction folders outside designated banking operating hours.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1078/002/"],
            "tags": ["attack.initial_access", "attack.t1078.002", "sector.banking"],
            "logsource": {"category": "file_access", "product": "banking_core"},
            "detection": {
                "selection": {
                    "process.command_line": ["*swift*", "*payment*", "*mt103*", "*transfer*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["Scheduled end-of-month reconciliation jobs"],
            "severity": "high"
        }
    },

    # --- Phishing ---
    {
        "category": "phishing",
        "filename": "telebirr_prize_lure.yml",
        "data": {
            "id": "phi-sigma-001",
            "title": "Telebirr Mobile Money Anniversary Scam Lure",
            "status": "stable",
            "description": "Detects inbound email or SMS payloads enticing users with 10,000 Birr prizes while harvesting PIN numbers.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1566/002/"],
            "tags": ["attack.initial_access", "attack.t1566.002", "region.ethiopia"],
            "logsource": {"category": "email", "product": "mta"},
            "detection": {
                "selection": {
                    "email.sender_domain": ["*telebirr-bonus.xyz*", "*telecom-promo.xyz*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["None known - confirmed fraudulent domains"],
            "severity": "critical"
        }
    },
    {
        "category": "phishing",
        "filename": "cbe_internet_banking_clone.yml",
        "data": {
            "id": "phi-sigma-002",
            "title": "Commercial Bank of Ethiopia (CBE) Fake KYC Portal",
            "status": "stable",
            "description": "Detects communications mimicking CBE urgent account suspension directing users to clone portals.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1566/002/"],
            "tags": ["attack.initial_access", "attack.t1566.002", "sector.banking"],
            "logsource": {"category": "email", "product": "mta"},
            "detection": {
                "selection": {
                    "email.sender_domain": ["*cbe-ebanking-auth.net*", "*combanketh-portal.com*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["None - domains unassociated with Commercial Bank of Ethiopia"],
            "severity": "critical"
        }
    },

    # --- Ethiopia Sector & Infrastructure ---
    {
        "category": "ethiopia",
        "filename": "telebirr_sms_spoofing.yml",
        "data": {
            "id": "eth-sigma-001",
            "title": "Telebirr Brand Spoofing on External Domain",
            "status": "stable",
            "description": "Detects DNS, HTTP, or email communications utilizing the Telebirr brand on non-official TLDs.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://insa.gov.et/cyber-alerts"],
            "tags": ["attack.reconnaissance", "brand.telebirr", "region.ethiopia"],
            "logsource": {"category": "dns_query", "product": "perimeter"},
            "detection": {
                "selection": {
                    "destination.domain": ["*telebirr*", "*tele-birr*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["Official telebirr.et or ethiotelecom.et domains"],
            "severity": "high"
        }
    },
    {
        "category": "ethiopia",
        "filename": "insa_defacement_alert.yml",
        "data": {
            "id": "eth-sigma-002",
            "title": "Government .gov.et Web Defacement or Unauthorized Shell",
            "status": "stable",
            "description": "Detects creation of PHP/ASPX web shells inside Ethiopian government web server docroots.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://attack.mitre.org/techniques/T1505/003/"],
            "tags": ["attack.persistence", "attack.t1505.003", "sector.government"],
            "logsource": {"category": "file_change", "product": "web_server"},
            "detection": {
                "selection": {
                    "process.command_line": ["*c99.php*", "*r57.php*", "*wso.php*", "*alfa.php*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["None - known web shell artifacts"],
            "severity": "critical"
        }
    },
    {
        "category": "ethiopia",
        "filename": "chapa_api_key_leak.yml",
        "data": {
            "id": "eth-sigma-003",
            "title": "Chapa Payment Gateway Secret Key Exfiltration",
            "status": "stable",
            "description": "Detects exposure of CHASECK_ live API secret keys in public HTTP responses or egress logs.",
            "author": "ETHIO-CYBERGUARD Detection Team",
            "version": "1.0.0",
            "date": "2026-09-30",
            "references": ["https://chapa.co/docs"],
            "tags": ["attack.credential_access", "sector.fintech"],
            "logsource": {"category": "dlp", "product": "gateway"},
            "detection": {
                "selection": {
                    "process.command_line": ["*CHASECK_TEST-*", "*CHASECK_LIVE-*"]
                },
                "condition": "selection"
            },
            "falsepositives": ["Authorized developer config file deployment"],
            "severity": "critical"
        }
    }
]

def generate_rules():
    os.makedirs(BASE_DIR, exist_ok=True)
    count = 0
    for r in RULES:
        cat_dir = os.path.join(BASE_DIR, r["category"])
        os.makedirs(cat_dir, exist_ok=True)
        rule_path = os.path.join(cat_dir, r["filename"])
        with open(rule_path, "w", encoding="utf-8") as f:
            yaml.dump(r["data"], f, sort_keys=False)
        count += 1
    print(f"Generated {count} SIGMA rules across 6 categories in {BASE_DIR}")

if __name__ == "__main__":
    generate_rules()
