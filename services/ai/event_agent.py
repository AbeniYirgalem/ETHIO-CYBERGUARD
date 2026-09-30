"""
AI Agent 1: Security Event Analysis Agent
Analyzes individual security events and identifies suspicious behavior with MITRE mapping.
"""

from typing import Dict, Any

class SecurityEventAnalysisAgent:
    def __init__(self, model_client=None):
        self.model_client = model_client

    def analyze(self, event: Dict[str, Any]) -> Dict[str, Any]:
        process_cmd = (event.get("process", {}).get("command_line") or "").lower()
        proc_name = (event.get("process", {}).get("name") or "").lower()
        user = event.get("user", "")

        is_suspicious = False
        reasons = []
        techniques = []
        confidence = 0.5

        if "powershell" in proc_name and ("-enc" in process_cmd or "downloadstring" in process_cmd):
            is_suspicious = True
            confidence = 0.94
            reasons.append("Base64 encoded payload executed via PowerShell to bypass command line logging.")
            reasons.append("Web download cradle detected in memory execution parameters.")
            techniques.append("T1059.001 - Command and Scripting Interpreter: PowerShell")
            techniques.append("T1027 - Obfuscated Files or Information")

        if "mimikatz" in process_cmd or "sekurlsa" in process_cmd:
            is_suspicious = True
            confidence = 0.98
            reasons.append("Direct invocation of credential dumping library against LSASS.")
            techniques.append("T1003.001 - OS Credential Dumping: LSASS Memory")

        if not is_suspicious:
            reasons.append("Process and argument parameters match baseline administrative operations.")
            confidence = 0.85

        return {
            "agent": "SecurityEventAnalysisAgent",
            "suspicious": is_suspicious,
            "reasons": reasons,
            "techniques": techniques,
            "confidence": confidence,
            "analyst_guidance": "Examine parent process lineage and network socket bindings immediately." if is_suspicious else "Normal operations."
        }
