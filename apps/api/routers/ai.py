"""
ETHIO-CYBERGUARD Multi-Agent AI Router
Coordinates the 7 specialized LLM agents for deep incident investigation,
grounded AI assistant chat, and explainable forensic report generation.
Supports /api/ai and /api/v1/ai.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.ai.orchestrator import MultiAgentOrchestrator
from services.ai.assistant_agent import SecurityAssistantAgent
from .incidents import INCIDENTS_STORE

router = APIRouter(tags=["Multi-Agent AI & Copilot"])

orchestrator = MultiAgentOrchestrator()
assistant = SecurityAssistantAgent()

class InvestigateRequest(BaseModel):
    incident_number: str = "INC-00042"
    include_raw_telemetry: Optional[bool] = True

class AIChatRequest(BaseModel):
    query: str
    incident_number: Optional[str] = "INC-00042"

@router.post("/api/ai/investigate")
@router.post("/api/v1/ai/investigate")
def run_ai_investigation(payload: InvestigateRequest):
    inc = next(
        (i for i in INCIDENTS_STORE if i["incident_number"].upper() == payload.incident_number.upper()), 
        INCIDENTS_STORE[0]
    )
    # Gather mock telemetry events related to this incident
    events = [
        {"event_id": "evt_001", "event_type": "process_execution", "severity": "CRITICAL", "process": {"name": "powershell.exe"}, "user": "administrator"},
        {"event_id": "evt_002", "event_type": "network_connection", "severity": "HIGH", "destination": {"ip": "185.220.101.5"}}
    ]
    return orchestrator.run_investigation_pipeline(inc, events)

@router.post("/api/ai/chat")
@router.post("/api/v1/ai/chat")
@router.post("/api/v1/ai/assistant/chat")
def chat_with_copilot(payload: AIChatRequest):
    inc = next(
        (i for i in INCIDENTS_STORE if i["incident_number"].upper() == (payload.incident_number or "INC-00042").upper()), 
        INCIDENTS_STORE[0]
    )
    return assistant.answer_query(payload.query, inc)

@router.get("/api/ai/agents")
@router.get("/api/v1/ai/agents")
def list_ai_agents():
    return {
        "cluster_status": "ONLINE",
        "total_agents": 7,
        "agents": [
            {
                "id": "agent-01",
                "name": "Event Analysis Agent",
                "role": "Parses ECS raw telemetries, extracts process arguments, evaluates obfuscation",
                "tools": ["parse_ecs", "deobfuscate_powershell", "detect_anomalies"],
                "status": "READY"
            },
            {
                "id": "agent-02",
                "name": "Threat Intelligence Agent",
                "role": "Queries Ethio-CERT, INSA feeds, and global threat databases for IOC reputation",
                "tools": ["query_ioc", "asn_lookup", "check_cert_blacklist"],
                "status": "READY"
            },
            {
                "id": "agent-03",
                "name": "Correlation Agent",
                "role": "Synthesizes multi-stage attack chains into unified incident graphs",
                "tools": ["build_attack_graph", "link_killchain", "cluster_alerts"],
                "status": "READY"
            },
            {
                "id": "agent-04",
                "name": "Investigation Agent",
                "role": "Performs deep forensic hypothesis testing and root cause determination",
                "tools": ["hypothesize_attack_path", "validate_evidence", "trace_lateral_movement"],
                "status": "READY"
            },
            {
                "id": "agent-05",
                "name": "Risk Assessment Agent",
                "role": "Computes explainable asset, vulnerability, and mission criticality risk scores",
                "tools": ["calculate_risk_vector", "evaluate_business_impact", "explain_scoring"],
                "status": "READY"
            },
            {
                "id": "agent-06",
                "name": "Executive Report Agent",
                "role": "Generates boardroom executive summaries and forensic technical disclosures",
                "tools": ["generate_executive_pdf", "format_insa_disclosure", "export_csv"],
                "status": "READY"
            },
            {
                "id": "agent-07",
                "name": "Security Assistant Agent",
                "role": "Grounded conversational SOC copilot with strict citation verification",
                "tools": ["grounded_rag", "cite_evidence", "explain_incident"],
                "status": "READY"
            }
        ]
    }
