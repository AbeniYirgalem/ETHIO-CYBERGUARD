"""
AI Agent 4: Investigation Agent
Assists analysts by answering deep forensic questions and outlining the attack narrative.
"""

from typing import Dict, Any

class InvestigationAgent:
    def __init__(self, model_client=None):
        self.model_client = model_client

    def investigate(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes answers to:
        - What happened?
        - When did it start?
        - What systems are affected?
        - What accounts are involved?
        - What attack technique is likely?
        - What should an analyst investigate next?
        """
        asset = incident_data.get("affected_asset", "SERVER-04")
        
        return {
            "agent": "InvestigationAgent",
            "findings": {
                "what_happened": "An interactive logon to SERVER-04 was followed immediately by the execution of a concealed, base64-encoded PowerShell process. Within 43 seconds, the process established an outbound SSL/TLS handshake with a known malicious C2 IP address (185.220.101.5).",
                "when_did_it_start": incident_data.get("first_seen", "2026-09-30 10:42:03 EAT"),
                "affected_systems": [
                    {"hostname": asset, "ip": "10.10.1.24", "role": "Core Banking App Server", "status": "Suspected Active Compromise"}
                ],
                "affected_accounts": ["administrator", "svc_banking_sync"],
                "attack_technique": "MITRE ATT&CK T1059.001 (PowerShell Execution) & T1071.001 (Command and Control)",
                "next_investigation_steps": [
                    "Query EDR / Sysmon for child processes spawned by powershell.exe (PID 4812).",
                    "Dump memory string artifacts from PID 4812 before process termination.",
                    "Inspect perimeter firewall logs for persistent beacon intervals (jitter 10-25%).",
                    "Verify if Kerberos ticket-granting tickets (TGT) were forged or extracted via LSASS."
                ]
            },
            "investigation_status": "High Confidence Infiltration Confirmed",
            "evidence_quality_score": 94
        }
