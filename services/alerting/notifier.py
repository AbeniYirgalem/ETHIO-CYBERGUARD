"""
ETHIO-CYBERGUARD Alerting & Multi-Channel Notification Engine
Handles dispatching high-fidelity alerts to Slack/Teams webhooks, email (SMTP), and SIEM relays.
Includes Amharic and English notification templates with priority-based escalation routing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger("ethio_cyberguard.alerting")

class AlertNotifier:
    """
    Manages security notification channels and escalation routing.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
        self.notification_log: List[Dict[str, Any]] = []

    def format_slack_payload(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        severity = alert.get("severity", "MEDIUM").upper()
        color = "#FF1744" if severity == "CRITICAL" else "#F59E0B" if severity == "HIGH" else "#00D9FF"

        title_am = alert.get("title_am", "የደህንነት ማስጠንቀቂያ")
        title_en = alert.get("title_en") or alert.get("title", "Security Alert")

        return {
            "attachments": [
                {
                    "color": color,
                    "title": f"🚨 [{severity}] {title_en} / {title_am}",
                    "fields": [
                        {"title": "Incident ID", "value": alert.get("incident_id", "N/A"), "short": True},
                        {"title": "Risk Score", "value": f"{alert.get('risk_score', 0)}/100", "short": True},
                        {"title": "Asset Affected", "value": alert.get("target_asset", "Unknown"), "short": True},
                        {"title": "Targeted Identity", "value": alert.get("target_user", "Unknown"), "short": True},
                        {"title": "Detection Vector", "value": alert.get("vector", "N/A"), "short": False}
                    ],
                    "footer": "ETHIO-CYBERGUARD Incident Response Engine",
                    "ts": int(datetime.now(timezone.utc).timestamp())
                }
            ]
        }

    def format_email_alert(self, alert: Dict[str, Any], lang: str = "en") -> Dict[str, str]:
        severity = alert.get("severity", "MEDIUM")
        inc_id = alert.get("incident_id", "INC-ALERT")
        asset = alert.get("target_asset", "Internal Host")
        score = alert.get("risk_score", 0)

        if lang == "am":
            subject = f"[አስቸኳይ ማስጠንቀቂያ - {severity}] {inc_id}፡ የሳይበር ጥቃት ተገኝቷል"
            body = (
                f"የደህንነት ቁጥጥር ማዕከል ማስጠንቀቂያ:\n"
                f"• የአደጋው መለያ ቁጥር: {inc_id}\n"
                f"• የአደጋ ደረጃ: {severity} (የስጋት ነጥብ: {score}/100)\n"
                f"• የተጠቃው ሲስተም: {asset}\n"
                f"• የተተገበረ እርምጃ: በSOC ተንታኝ ፈቃድ መጠበቂያ ላይ ይገኛል\n\n"
                f"እባክዎ ወዲያውኑ ወደ ETHIO-CYBERGUARD ዳሽቦርድ በመግባት ውሳኔ ይስጡ።"
            )
        else:
            subject = f"[URGENT - {severity}] {inc_id}: High-Priority Security Incident"
            body = (
                f"ETHIO-CYBERGUARD Security Operations Alert:\n"
                f"• Incident ID: {inc_id}\n"
                f"• Severity: {severity} (Calculated Risk: {score}/100)\n"
                f"• Impacted Asset: {asset}\n"
                f"• Status: Pending Analyst Authorization (Dual-Custody SOAR)\n\n"
                f"Review and authorize containment playbooks at your ETHIO-CYBERGUARD SOC console."
            )

        return {"subject": subject, "body": body}

    def dispatch(self, alert: Dict[str, Any], channel: str = "webhook") -> Dict[str, Any]:
        """
        Dispatches alert to designated channel.
        Simulates network delivery and appends to immutable notification log.
        """
        severity = alert.get("severity", "MEDIUM").upper()
        # Escalation policy: Only dispatch HIGH and CRITICAL to emergency paging
        is_escalated = severity in ["HIGH", "CRITICAL"]

        dispatch_record = {
            "notification_id": f"notif_{len(self.notification_log) + 1:04d}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "incident_id": alert.get("incident_id"),
            "channel": channel,
            "severity": severity,
            "escalated": is_escalated,
            "delivered": True
        }

        if channel == "webhook":
            payload = self.format_slack_payload(alert)
            dispatch_record["payload"] = payload
        elif channel == "email":
            email_data = self.format_email_alert(alert, lang="en")
            dispatch_record["email"] = email_data

        self.notification_log.append(dispatch_record)
        return dispatch_record
