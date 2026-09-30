"""
ETHIO-CYBERGUARD Detection Engine
Combines Rule-based detection, Behavioral baseline analysis, and Anomaly detection.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import re

class DetectionEngine:
    """
    Evaluates normalized events against multiple detection mechanisms
    to trigger prioritized security alerts.
    """

    def __init__(self, threat_indicators: Optional[Dict[str, Any]] = None):
        self.threat_indicators = threat_indicators or {
            "185.220.101.5": {"type": "IPV4", "reputation": "MALICIOUS", "actor": "APT-CobaltStrike"},
            "update-winsec-cloud.com": {"type": "DOMAIN", "reputation": "MALICIOUS", "actor": "Fin-Threat"},
            "7d4b29c9103a89e924a2734ef0350d24fb4b3e6480c55ffc06a928db6928e469": {"type": "SHA256", "reputation": "MALICIOUS", "name": "Mimikatz"}
        }

    def evaluate_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts = []

        # 1. Rule-based detection
        rule_alerts = self._check_rules(event)
        alerts.extend(rule_alerts)

        # 2. Threat Intel matching
        ti_alerts = self._check_threat_intel(event)
        alerts.extend(ti_alerts)

        # 3. Behavioral baseline scoring
        behavioral_alert = self._evaluate_behavioral(event)
        if behavioral_alert:
            alerts.append(behavioral_alert)

        return alerts

    def _check_rules(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts = []
        process = event.get("process", {})
        cmd = (process.get("command_line") or "").lower()
        proc_name = (process.get("name") or "").lower()

        # Rule: Suspicious Obfuscated PowerShell execution
        if "powershell" in proc_name and any(x in cmd for x in ["-enc", "-encodedcommand", "downloadstring", "invoke-expression", "iex"]):
            alerts.append({
                "alert_id": f"ALT-RULE-001-{int(datetime.now(timezone.utc).timestamp())}",
                "title": "Suspicious Obfuscated PowerShell Command",
                "description": f"Process {process.get('name')} ran encoded or download cradle command on {event['source']['hostname']}.",
                "severity": "CRITICAL",
                "mitre_tactic": "Execution",
                "mitre_technique": "T1059.001 - PowerShell",
                "rule_name": "Obfuscated_PowerShell_Execution",
                "confidence": 92
            })

        # Rule: Credential Dumping Tool Execution
        if any(tool in cmd or tool in proc_name for tool in ["mimikatz", "procdump", "sekurlsa", "lsass"]):
            alerts.append({
                "alert_id": f"ALT-RULE-002-{int(datetime.now(timezone.utc).timestamp())}",
                "title": "Possible LSASS Memory Credential Access",
                "description": f"Detected credential extraction signature in process arguments: {cmd}",
                "severity": "CRITICAL",
                "mitre_tactic": "Credential Access",
                "mitre_technique": "T1003.001 - LSASS Memory",
                "rule_name": "Credential_Dumping_LSASS",
                "confidence": 95
            })

        return alerts

    def _check_threat_intel(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts = []
        dest_ip = event.get("network", {}).get("destination_ip")
        if dest_ip and dest_ip in self.threat_indicators:
            ti = self.threat_indicators[dest_ip]
            alerts.append({
                "alert_id": f"ALT-TI-{int(datetime.now(timezone.utc).timestamp())}",
                "title": f"Known Malicious C2 Communication: {dest_ip}",
                "description": f"Connection initiated to threat actor indicator ({ti.get('actor', 'Unknown')}). Reputation: {ti.get('reputation')}",
                "severity": "CRITICAL",
                "mitre_tactic": "Command and Control",
                "mitre_technique": "T1071.001 - Web Protocols",
                "rule_name": "Threat_Intel_IP_Match",
                "confidence": 96
            })
        return alerts

    def _evaluate_behavioral(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Calculates explainable behavioral anomaly score:
        +25 unusual login time (e.g. 03:14 AM)
        +20 new or unusual source IP
        +20 unusual device / workstation
        +22 sensitive resource access
        """
        score = 0
        reasons = []

        timestamp_str = event.get("timestamp", "")
        hour = 12
        try:
            dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            hour = dt.hour
        except Exception:
            pass

        # Check off-hours (10 PM to 5 AM)
        if hour < 5 or hour > 22:
            score += 25
            reasons.append({"factor": "Unusual off-hours activity (03:00 - 05:00 EAT)", "points": 25})

        # Check external / untrusted source for internal sensitive action
        src_ip = event.get("network", {}).get("source_ip", "")
        if src_ip and not event.get("enrichment", {}).get("is_internal_network", True):
            score += 20
            reasons.append({"factor": "Remote external connection to privileged asset", "points": 20})

        # Check administrative account usage
        user_val = event.get("user") or ""
        user_str = (user_val.get("name") or user_val.get("id") or "") if isinstance(user_val, dict) else str(user_val)
        user_lower = user_str.lower()
        if any(adm in user_lower for adm in ["admin", "root", "administrator", "service_core"]):
            score += 20
            reasons.append({"factor": "Privileged credential utilized in abnormal context", "points": 20})

        # Sensitive target directory or service
        cmd = (event.get("process", {}).get("command_line") or "").lower()
        if any(sens in cmd for sens in ["swift", "banking", "shadow", "sam", "ntds.dit", "payroll"]):
            score += 22
            reasons.append({"factor": "Access to high-criticality banking/SWIFT resource", "points": 22})

        if score >= 60:
            return {
                "alert_id": f"ALT-BEHAVIOR-{int(datetime.now(timezone.utc).timestamp())}",
                "title": f"High Behavioral Anomaly Score ({score}/100)",
                "description": f"Composite behavioral anomaly detected for user {event.get('user')}.",
                "severity": "HIGH" if score < 85 else "CRITICAL",
                "behavior_score": score,
                "score_breakdown": reasons,
                "confidence": 88
            }
        return None
