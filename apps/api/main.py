"""
ETHIO-CYBERGUARD Central Backend API Service
FastAPI REST & WebSocket Gateway for SOC Monitoring, Ingestion, Detection & Multi-Agent AI
"""

from fastapi import FastAPI, HTTPException, Request, Depends, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import sys
import os

# Ensure services directory is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.ingestion.normalizer import EventNormalizer
from services.detection.engine import DetectionEngine
from services.correlation.correlator import CorrelationEngine
from services.ai.orchestrator import MultiAgentOrchestrator
from services.ai.assistant_agent import SecurityAssistantAgent
from services.phishing.email_analyzer import PhishingAnalyzer
from services.typosquat.domain_monitor import TyposquatMonitor
from services.osint.surface_recon import AttackSurfaceRecon
from services.awareness.simulator import AwarenessSimulator
from services.pipeline.unified_engine import UnifiedPipelineEngine
from services.alerting.notifier import AlertNotifier
from scripts.benchmark_eps import run_benchmark

app = FastAPI(
    title="ETHIO-CYBERGUARD Central SOC API",
    description="Centralized Security Operations Center and AI Investigation Platform API",
    version="1.0.0"
)

# Enable CORS for frontend web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
normalizer = EventNormalizer()
detection_engine = DetectionEngine()
correlation_engine = CorrelationEngine()
ai_orchestrator = MultiAgentOrchestrator()
assistant_agent = SecurityAssistantAgent()
phishing_analyzer = PhishingAnalyzer()
typosquat_monitor = TyposquatMonitor()
osint_recon = AttackSurfaceRecon()
awareness_simulator = AwarenessSimulator()
unified_pipeline = UnifiedPipelineEngine()
alert_notifier = AlertNotifier()

class ConnectionManager:
    """Manages active WebSocket connections from SOC frontend clients."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

ws_manager = ConnectionManager()

# In-Memory State for Demonstration & Local Running
mock_incidents = [
    {
        "id": "e0000000-0000-0000-0000-000000000001",
        "incident_number": "INC-00042",
        "title": "Suspicious Obfuscated PowerShell Activity & C2 Beaconing",
        "severity": "CRITICAL",
        "status": "INVESTIGATING",
        "risk_score": 92,
        "affected_asset": "SERVER-04",
        "asset_ip": "10.10.1.24",
        "department": "Core Banking Infrastructure",
        "first_seen": "2026-09-30 10:42:00+03:00",
        "last_activity": "2026-09-30 11:18:00+03:00",
        "assigned_analyst": "Dawit Mengistu",
        "summary": "Privileged service account initiated hidden PowerShell with base64 encoded command, establishing outbound beaconing to known malicious C2 IP 185.220.101.5."
    },
    {
        "id": "e0000000-0000-0000-0000-000000000002",
        "incident_number": "INC-00021",
        "title": "Perimeter Gateway Distributed SSH & RDP Brute Force",
        "severity": "HIGH",
        "status": "OPEN",
        "risk_score": 78,
        "affected_asset": "FW-PERIMETER-01",
        "asset_ip": "197.156.70.1",
        "department": "Network Security",
        "first_seen": "2026-09-30 09:15:00+03:00",
        "last_activity": "2026-09-30 09:22:00+03:00",
        "assigned_analyst": "Sara Yohannes",
        "summary": "Over 1,200 failed authentication attempts detected within 4 minutes originating from distributed IP ranges targeting perimeter firewall management interface."
    },
    {
        "id": "e0000000-0000-0000-0000-000000000003",
        "incident_number": "INC-00019",
        "title": "Unusual Off-Hours Privileged SWIFT Access from Remote IP",
        "severity": "MEDIUM",
        "status": "INVESTIGATING",
        "risk_score": 64,
        "affected_asset": "LAPTOP-FINANCE-22",
        "asset_ip": "10.10.4.88",
        "department": "Treasury & SWIFT Processing",
        "first_seen": "2026-09-30 03:14:00+03:00",
        "last_activity": "2026-09-30 03:45:00+03:00",
        "assigned_analyst": "Dawit Mengistu",
        "summary": "Treasury workstation user logged in at 03:14 AM EAT from unmanaged residential IP subnet, accessing SWIFT payment file transfer directory."
    }
]

mock_response_actions = [
    {
        "id": "ACT-001",
        "incident_number": "INC-00042",
        "action_type": "ISOLATE_HOST",
        "target_entity": "SERVER-04 (10.10.1.24)",
        "recommended_by": "AI_RISK_AGENT",
        "reasoning": "Potential active malware / C2 beaconing. Host isolation cuts lateral traversal while maintaining forensic link to SOC.",
        "confidence": 94,
        "status": "PENDING_APPROVAL",
        "created_at": "2026-09-30T10:45:00Z"
    },
    {
        "id": "ACT-002",
        "incident_number": "INC-00042",
        "action_type": "BLOCK_IP",
        "target_entity": "185.220.101.5",
        "recommended_by": "AI_THREAT_INTEL_AGENT",
        "reasoning": "Confirmed Cobalt Strike C2 server on Ethio-CERT blacklist. Egress and ingress drop recommended.",
        "confidence": 98,
        "status": "PENDING_APPROVAL",
        "created_at": "2026-09-30T10:46:00Z"
    }
]

# Pydantic Schemas
class EventIngestPayload(BaseModel):
    event_uid: Optional[str] = None
    timestamp: Optional[str] = None
    source: Optional[Dict[str, Any]] = None
    event_type: str
    severity: Optional[str] = "INFO"
    user: Optional[str] = None
    process: Optional[Dict[str, Any]] = None
    network: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None

class AssistantQueryRequest(BaseModel):
    query: str
    incident_number: Optional[str] = "INC-00042"

class ActionDecisionPayload(BaseModel):
    reason: Optional[str] = "Approved by SOC analyst Dawit Mengistu"

class PhishingAnalyzeRequest(BaseModel):
    raw_content: str
    subject: Optional[str] = None
    sender: Optional[str] = None

class AwarenessLaunchRequest(BaseModel):
    campaign_id: str
    department: Optional[str] = "All"

class UnifiedPipelineRequest(BaseModel):
    source_type: str = "email"
    raw_payload: Optional[str] = None
    recipient_user: Optional[str] = "dawit.mengistu@cbe.com.et"
    recipient_host: Optional[str] = "SERVER-04"
    recipient_ip: Optional[str] = "10.10.1.24"

# REST Endpoints
@app.get("/")
def root():
    return {
        "platform": "ETHIO-CYBERGUARD Central SOC API",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "docs_url": "/docs"
    }

@app.get("/api/v1/stats/overview")
def get_soc_overview():
    return {
        "metrics": {
            "critical_alerts": 7,
            "high_risk_alerts": 23,
            "active_incidents": 12,
            "events_processed_today": 284921
        },
        "top_threats": [
            {"name": "Distributed Brute Force", "count": 1420, "severity": "HIGH"},
            {"name": "Obfuscated PowerShell Execution", "count": 18, "severity": "CRITICAL"},
            {"name": "Off-Hours SWIFT Directory Access", "count": 3, "severity": "MEDIUM"},
            {"name": "Known Malicious C2 Beaconing", "count": 12, "severity": "CRITICAL"}
        ],
        "system_health": {
            "ingestion_pipeline": "HEALTHY (4,210 eps)",
            "detection_engine": "ACTIVE (148 rules)",
            "correlation_engine": "RUNNING",
            "ai_agents_cluster": "ONLINE (7/7 Agents Ready)"
        }
    }

@app.post("/api/v1/events/ingest")
def ingest_event(payload: EventIngestPayload):
    norm = normalizer.normalize(payload.dict())
    alerts = detection_engine.evaluate_event(norm)
    return {
        "status": "ACCEPTED",
        "event_id": norm["event_id"],
        "alerts_triggered": len(alerts),
        "alerts": alerts
    }

@app.get("/api/v1/incidents")
def list_incidents():
    return {"incidents": mock_incidents}

@app.get("/api/v1/incidents/{incident_number}")
def get_incident(incident_number: str):
    inc = next((i for i in mock_incidents if i["incident_number"] == incident_number), None)
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Enrich with timeline, attack graph, and multi-agent AI data
    correlated = correlation_engine.correlate_alerts([], asset_name=inc["affected_asset"])
    investigation = ai_orchestrator.run_investigation_pipeline(inc, [])
    
    return {
        "incident": inc,
        "timeline": correlated["timeline"],
        "attack_graph": correlated["attack_graph"],
        "ai_investigation": investigation["pipeline_results"]
    }

@app.get("/api/v1/threat-intelligence")
def get_threat_indicators():
    return {
        "indicators": [
            {
                "indicator": "185.220.101.5",
                "type": "IPV4",
                "reputation": "MALICIOUS",
                "confidence": 96,
                "first_seen": "2026-04-12",
                "threat_actor": "APT-CobaltStrike-Actor",
                "malware": "Cobalt Strike Beacon",
                "country": "Germany",
                "related_incidents": ["INC-00042", "INC-00021"]
            },
            {
                "indicator": "update-winsec-cloud.com",
                "type": "DOMAIN",
                "reputation": "MALICIOUS",
                "confidence": 92,
                "first_seen": "2026-08-19",
                "threat_actor": "Fin-Threat Cluster",
                "malware": "Empire C2 Stager",
                "country": "Russia",
                "related_incidents": ["INC-00019"]
            },
            {
                "indicator": "7d4b29c9103a89e924a2734ef0350d24fb4b3e6480c55ffc06a928db6928e469",
                "type": "SHA256",
                "reputation": "MALICIOUS",
                "confidence": 99,
                "first_seen": "2026-01-10",
                "threat_actor": "Lazarus Group",
                "malware": "Mimikatz LSASS Infiltrator",
                "country": "North Korea",
                "related_incidents": ["INC-00042"]
            }
        ]
    }

@app.post("/api/v1/ai/assistant/chat")
def chat_with_assistant(payload: AssistantQueryRequest):
    inc = next((i for i in mock_incidents if i["incident_number"] == payload.incident_number), mock_incidents[0])
    answer = assistant_agent.answer_query(payload.query, inc)
    return answer

@app.get("/api/v1/response/actions")
def list_response_actions():
    return {"actions": mock_response_actions}

@app.post("/api/v1/response/actions/{action_id}/approve")
def approve_action(action_id: str, payload: ActionDecisionPayload):
    action = next((a for a in mock_response_actions if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    action["status"] = "APPROVED"
    action["executed_at"] = datetime.now(timezone.utc).isoformat()
    action["reviewed_by"] = "Dawit Mengistu (Security Analyst)"
    return {
        "status": "SUCCESS",
        "message": f"Action {action_id} APPROVED and executed by response engine.",
        "action": action
    }

@app.post("/api/v1/response/actions/{action_id}/reject")
def reject_action(action_id: str, payload: ActionDecisionPayload):
    action = next((a for a in mock_response_actions if a["id"] == action_id), None)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    action["status"] = "REJECTED"
    action["rejection_reason"] = payload.reason
    action["reviewed_by"] = "Dawit Mengistu (Security Analyst)"
    return {
        "status": "SUCCESS",
        "message": f"Action {action_id} REJECTED.",
        "action": action
    }

# --- Phishing Email Analyzer (ThePhish / NLP Engine) ---
@app.post("/api/v1/phishing/analyze")
def analyze_phishing_email(payload: PhishingAnalyzeRequest):
    result = phishing_analyzer.analyze(
        raw_content=payload.raw_content,
        subject=payload.subject,
        sender=payload.sender
    )
    return result

# --- Typosquatting & Brand Defense Monitor (openSquat Engine) ---
@app.get("/api/v1/typosquat/scan")
def scan_typosquats(target: str = "telebirr.et", limit: int = 40):
    return typosquat_monitor.scan_domain(domain_or_brand=target, limit=limit)

# --- OSINT & Attack Surface Recon (SpiderFoot / Sherlock Engine) ---
@app.get("/api/v1/osint/scan")
def scan_attack_surface(target: str = "ethiotelecom.et"):
    return osint_recon.scan_target(target=target)

# --- Security Awareness & Training (CyberSatark Engine) ---
@app.get("/api/v1/awareness/campaigns")
def list_awareness_campaigns():
    return {"campaigns": awareness_simulator.get_campaigns()}

@app.get("/api/v1/awareness/metrics")
def get_awareness_metrics():
    return awareness_simulator.get_org_metrics()

@app.post("/api/v1/awareness/launch")
def launch_awareness_simulation(payload: AwarenessLaunchRequest):
    return awareness_simulator.launch_simulation(campaign_id=payload.campaign_id, department=payload.department)

# --- Common Security Graph Unified Pipeline Engine ---
@app.post("/api/v1/pipeline/execute-slice")
def execute_unified_pipeline_slice(payload: UnifiedPipelineRequest):
    default_email = """From: "Telebirr Support" <support@telebirr-bonus.xyz>
To: dawit.mengistu@cbe.com.et
Reply-To: phisher-collector@gmail.com
Subject: URGENT: ቴሌብር 10,000 ብር የሽልማት አሸናፊ - አሁኑኑ ያረጋግጡ
Received-SPF: fail (domain telebirr-bonus.xyz does not match sender IP 196.188.99.12)
Authentication-Results: mx.ethiotelecom.et; spf=fail; dkim=fail; dmarc=fail

እንኳን ደስ አሎት! በብሔራዊ የዲጂታል ክፍያ ማበረታቻ ፕሮግራም የ10,000 ብር የቴሌብር ቦነስ አሸንፈዋል።
ሽልማቱን በቀጥታ ወደ አካውንትዎ ለማስገባት በ24 ሰዓት ውስጥ ይህን ይጫኑና የቴሌብር ፒን (PIN / OTP) ቁጥርዎን ያረጋግጡ፡
http://196.188.99.12/claim-prize/telebirr-login.php
"""
    raw_email = payload.raw_payload or default_email
    result = unified_pipeline.process_phishing_event_to_incident(
        raw_email=raw_email,
        recipient_user=payload.recipient_user or "dawit.mengistu@cbe.com.et",
        recipient_host=payload.recipient_host or "SERVER-04",
        recipient_ip=payload.recipient_ip or "10.10.1.24"
    )
    return result

# --- Health, Readiness & Observability Endpoints ---
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ETHIO-CYBERGUARD-API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_websockets": len(ws_manager.active_connections)
    }

@app.get("/api/v1/ready")
def readiness_check():
    return {
        "status": "ready",
        "database": "connected",
        "rule_engine": "loaded",
        "ai_orchestrator": "ready"
    }

# --- Real-Time SOC WebSocket Telemetry Stream ---
@app.websocket("/ws/live-events")
async def websocket_live_events(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Welcome event handshake
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to ETHIO-CYBERGUARD live SOC telemetry stream",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        while True:
            # Keepalive and client message handler
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# --- Multi-Channel Alert Notification Dispatch ---
class AlertNotifyRequest(BaseModel):
    incident_id: str
    severity: str = "HIGH"
    risk_score: int = 85
    target_asset: str = "SERVER-04"
    target_user: Optional[str] = "dawit.mengistu"
    title_en: Optional[str] = "Security Incident Alert"
    title_am: Optional[str] = "የደህንነት ማስጠንቀቂያ"
    channel: str = "webhook"

@app.post("/api/v1/alerts/notify")
async def dispatch_alert_notification(payload: AlertNotifyRequest):
    alert_dict = payload.model_dump()
    result = alert_notifier.dispatch(alert_dict, channel=payload.channel)
    # Broadcast to live SOC console via WebSocket
    await ws_manager.broadcast({
        "type": "NEW_ALERT_DISPATCHED",
        "alert": alert_dict,
        "notification": result
    })
    return result

# --- Ingestion & Detection EPS Benchmark Runner ---
@app.get("/api/v1/benchmark/run")
def trigger_benchmark(events: int = 5000):
    report = run_benchmark(total_events=events, num_workers=4)
    return report


