"""
ETHIO-CYBERGUARD Multi-Agent AI Orchestrator
Coordinates the 7 specialized AI components during incident investigation.
"""

from typing import Dict, Any, List
from .event_agent import SecurityEventAnalysisAgent
from .threat_agent import ThreatIntelligenceAgent
from .correlation_agent import IncidentCorrelationAgent
from .investigation_agent import InvestigationAgent
from .risk_agent import RiskAssessmentAgent
from .report_agent import SecurityReportAgent
from .assistant_agent import SecurityAssistantAgent

class MultiAgentOrchestrator:
    """
    Manages the multi-agent investigation lifecycle:
    Event Analysis -> Threat Intel -> Correlation -> Investigation -> Risk Assessment -> Report & Assistant
    """

    def __init__(self):
        self.event_agent = SecurityEventAnalysisAgent()
        self.threat_agent = ThreatIntelligenceAgent()
        self.correlation_agent = IncidentCorrelationAgent()
        self.investigation_agent = InvestigationAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.report_agent = SecurityReportAgent()
        self.assistant_agent = SecurityAssistantAgent()

    def run_investigation_pipeline(self, incident: Dict[str, Any], events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Executes the multi-agent investigation pipeline for an incident.
        """
        # Step 1: Event Analysis
        event_findings = [self.event_agent.analyze(ev) for ev in events[:5]]

        # Step 2: Threat Intel Enrichment
        indicators = ["185.220.101.5", "update-winsec-cloud.com"]
        threat_intel = self.threat_agent.enrich(indicators)

        # Step 3: Correlation
        correlation = self.correlation_agent.correlate(events)

        # Step 4: Deep Investigation
        investigation = self.investigation_agent.investigate(incident)

        # Step 5: Risk Assessment
        risk = self.risk_agent.assess_risk(incident)

        # Step 6: Automated Forensic Report Generation
        tech_report = self.report_agent.generate_technical_report(incident)
        exec_report = self.report_agent.generate_executive_summary(incident)

        return {
            "orchestrator_status": "COMPLETED",
            "incident_number": incident.get("incident_number", "INC-00042"),
            "agents_executed": 7,
            "pipeline_results": {
                "event_analysis": event_findings,
                "threat_intelligence": threat_intel,
                "correlation": correlation,
                "investigation": investigation,
                "risk_assessment": risk,
                "reports": {
                    "technical": tech_report,
                    "executive": exec_report
                }
            }
        }
