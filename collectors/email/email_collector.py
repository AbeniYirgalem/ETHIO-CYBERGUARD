"""
ETHIO-CYBERGUARD Email Telemetry Collector
Ingests incoming enterprise emails from Postfix/Sendmail MTA milters, Microsoft Exchange,
Google Workspace webhooks, or local Maildir directories for automated forensic phishing analysis.
"""

import sys
import os
from typing import Dict, Any, Optional

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.phishing.email_analyzer import PhishingAnalyzer

class EmailCollector:
    """
    Ingests and normalizes emails into ECS security events.
    """

    def __init__(self, analyzer: Optional[PhishingAnalyzer] = None):
        self.analyzer = analyzer or PhishingAnalyzer()

    def process_raw_email(self, raw_eml_content: str, mailbox_user: str = "security@cbe.com.et") -> Dict[str, Any]:
        """
        Parses raw email text, runs phishing analysis, and produces an ECS security event.
        """
        analysis = self.analyzer.analyze(raw_content=raw_eml_content)
        
        ecs_event = {
            "event_type": "email_message",
            "severity": "CRITICAL" if analysis.get("verdict") == "CRITICAL_PHISHING" else "HIGH" if analysis.get("verdict") == "HIGH_RISK" else "LOW",
            "user": mailbox_user,
            "email": {
                "sender": analysis.get("sender"),
                "sender_domain": analysis.get("sender_domain"),
                "reply_to": analysis.get("reply_to"),
                "subject": analysis.get("subject"),
                "is_phishing": analysis.get("is_phishing"),
                "risk_score": analysis.get("risk_score"),
                "auth_status": analysis.get("auth_results", {})
            },
            "source": {
                "type": "email_gateway",
                "hostname": "mta-core.cbe.internal",
                "ip": "10.10.1.50"
            }
        }
        return ecs_event

# Standalone execution test
if __name__ == "__main__":
    collector = EmailCollector()
    sample = "From: hr@telecom-promo.xyz\nTo: dawit@cbe.com.et\nSubject: Bonus\n\nClaim now: http://196.188.99.12/win"
    result = collector.process_raw_email(sample)
    print("Email Ingestion ECS Event:")
    print(result)
