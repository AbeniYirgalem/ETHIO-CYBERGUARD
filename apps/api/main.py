"""
ETHIO-CYBERGUARD Central Backend API Service
FastAPI REST & WebSocket Gateway for SOC Monitoring, Ingestion, Detection & Multi-Agent AI
"""

from fastapi import FastAPI, HTTPException, Request, Depends, Query, status, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal, Optional
from datetime import datetime, timezone
from contextlib import asynccontextmanager
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
from apps.api.routers.auth import router as auth_router
from apps.api.routers.incidents import router as incidents_router
from apps.api.routers.phishing import router as phishing_router
from apps.api.routers.threat_intel import router as threat_intel_router
from apps.api.routers.osint import router as osint_router
from apps.api.routers.typosquat import router as typosquat_router
from apps.api.routers.awareness import router as awareness_router
from apps.api.routers.ai import router as ai_router
from apps.api.routers.response import router as response_router
from apps.api.routers.dashboard import router as dashboard_router
from apps.api.routers.reports import router as reports_router
from apps.api.routers.jobs import router as jobs_router
from apps.api.routers.connectors import router as connectors_router
from apps.api.routers.health import router as health_router
from database.connection import init_db
from database import state_store
from apps.api.routers import response as response_module
from services.websocket.manager import ws_manager
from services.telemetry.stats import telemetry_stats, telemetry_registry, register_persistence, restore_from_store
from services.security.tenancy import DEFAULT_ORG_ID, org_of, is_global
from services.ingestion.pipeline import ingestion_pipeline
from apps.api.dependencies import require_permission, verify_token, after_state_restore, DEMO_USERS
from apps.api.tenancy import resolve_collector_org
from apps.api.config import DEMO_MODE, MAX_PAYLOAD_BYTES, validate_production_config
from apps.api.security_middleware import install_security_middleware

register_persistence()

@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_production_config()
    init_db()
    state_store.restore_all()
    after_state_restore()
    restore_from_store()  # event counters and hourly history survive restarts
    response_module._rearm_demo_seed_actions()
    yield
    telemetry_stats.flush()  # save the last few seconds of counts
    telemetry_registry.flush_all()

app = FastAPI(
    title="ETHIO-CYBERGUARD Central SOC API",
    description="Centralized Security Operations Center and AI Investigation Platform API",
    version="1.1.0",
    lifespan=lifespan,
    # Interactive API docs are only exposed in demo mode.
    docs_url="/docs" if DEMO_MODE else None,
    redoc_url="/redoc" if DEMO_MODE else None,
)

# Register Modular Routers (Supporting both /api and /api/v1 paths)
app.include_router(auth_router)
app.include_router(incidents_router)
app.include_router(phishing_router)
app.include_router(threat_intel_router)
app.include_router(osint_router)
app.include_router(typosquat_router)
app.include_router(awareness_router)
app.include_router(ai_router)
app.include_router(response_router)
app.include_router(dashboard_router)
app.include_router(reports_router)
app.include_router(jobs_router)
app.include_router(connectors_router)
app.include_router(health_router)

# Secure CORS configuration (strictly disallow insecure wildcard with credentials)
allowed_origins_env = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,https://AbeniYirgalem.github.io"
)
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

# Added before CORS so CORS wraps it (429 responses still carry CORS headers).
install_security_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "Accept"],
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

# Production Channel-based WebSocket Manager imported from services.websocket.manager

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

@app.get("/api/system/mode")
@app.get("/api/v1/system/mode")
def get_system_mode():
    return {
        "demo_mode": DEMO_MODE,
        "banner": "Demo Mode: all incidents and metrics are simulated." if DEMO_MODE else "Production Mode: live infrastructure active.",
        "max_payload_bytes": MAX_PAYLOAD_BYTES
    }

def _stream_event(norm: Dict[str, Any]) -> Dict[str, Any]:
    """The part of a normalized event that is safe and useful to push to SOC consoles
    (raw_data and enrichment stay on the server)."""
    process = norm.get("process") or {}
    return {
        "event_id": norm.get("event_id"),
        "timestamp": norm.get("timestamp"),
        "source": norm.get("source"),
        "event_type": norm.get("event_type"),
        "severity": norm.get("severity"),
        "user": norm.get("user"),
        "process": {"name": process.get("name"), "command_line": process.get("command_line")},
        "network": norm.get("network"),
    }


@app.post("/api/v1/events/ingest")
async def ingest_event(
    payload: EventIngestPayload,
    org_id: str = Depends(resolve_collector_org)
):
    norm = normalizer.normalize(payload.model_dump(exclude_none=True))
    # The collector's key decides the organization; the event body can never choose it.
    norm["org_id"] = org_id
    # Rate limit per organization + host, so one organization cannot exhaust another's allowance.
    client_id = f"{org_id}:{(norm.get('source') or {}).get('hostname') or 'collector'}"
    ingest_result = ingestion_pipeline.ingest(norm, client_id=client_id)
    result_status = ingest_result.get("status", "ACCEPTED")
    if result_status == "RATE_LIMITED":
        raise HTTPException(status_code=429, detail=ingest_result.get("message"))

    alerts: List[Dict[str, Any]] = []
    if result_status == "ACCEPTED":
        alerts = detection_engine.evaluate_event(norm)
        telemetry_registry.record_event(org_id, norm.get("severity", "INFO"), alerts)
        # Push to the consoles of THIS organization only (plus national administrators).
        await ws_manager.broadcast_to_tenant(org_id, {
            "type": "EVENT_INGESTED",
            "org_id": org_id,
            "event": _stream_event(norm),
            "alerts": alerts,
            "stats": telemetry_registry.for_org(org_id).snapshot(),
        })
    return {
        "status": result_status,
        "event_id": norm["event_id"],
        "event_hash": ingest_result.get("event_hash"),
        "queue_depth": ingest_result.get("queue_depth", 0),
        "alerts_triggered": len(alerts),
        "alerts": alerts
    }

# NOTE: SOAR response routes live in apps/api/routers/response.py (authenticated, RBAC + audit).

# --- Phishing Email Analyzer (ThePhish / NLP Engine) ---
# --- Typosquatting & Brand Defense Monitor (openSquat Engine) ---
# --- OSINT & Attack Surface Recon (SpiderFoot / Sherlock Engine) ---
# --- Security Awareness & Training (CyberSatark Engine) ---
# --- Common Security Graph Unified Pipeline Engine ---
@app.post("/api/v1/pipeline/execute-slice")
def execute_unified_pipeline_slice(
    payload: UnifiedPipelineRequest,
    _user: Dict[str, Any] = Depends(require_permission("incident:assign")),
):
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
        "active_websockets": ws_manager.get_active_count()
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
async def websocket_live_events(websocket: WebSocket, token: Optional[str] = None):
    user_meta = {
        "role": "SECURITY_ANALYST",
        "organization": "Commercial Bank of Ethiopia",
        "org_id": DEFAULT_ORG_ID,
        "global": False,
    }
    if token:
        # A token that is present must be valid; a bad token is never silently downgraded to guest.
        try:
            payload = verify_token(token)
        except Exception:
            await websocket.close(code=1008)
            return
        known_user = DEMO_USERS.get(payload.get("sub"))
        if known_user is not None:
            # Same rule as the REST API: a password reset retires every earlier session.
            if int(payload.get("tv", 0) or 0) != int(known_user.get("token_version", 0) or 0):
                await websocket.close(code=1008)
                return
            identity = known_user          # the live account decides role and organization
        elif DEMO_MODE:
            identity = payload             # demo sandbox: accept an unknown but validly signed token
        else:
            await websocket.close(code=1008)
            return
        user_meta = {
            "role": identity.get("role", "SECURITY_ANALYST"),
            "organization": identity.get("organization", "Commercial Bank of Ethiopia"),
            "org_id": org_of(identity),
            "global": is_global(identity),
            "email": payload.get("sub")
        }
    elif not DEMO_MODE:
        # Production: the live stream carries security telemetry, so a login is mandatory.
        await websocket.close(code=1008)
        return

    connected = await ws_manager.connect(websocket, user_meta)
    if not connected:
        return

    try:
        # Welcome event handshake with channel confirmations
        await websocket.send_json({
            "type": "CONNECTION_ESTABLISHED",
            "message": "Connected to authenticated ETHIO-CYBERGUARD live SOC telemetry stream",
            "tenant_channel": f"tenant:{user_meta.get('org_id')}",
            "role": user_meta.get("role"),
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
    incident_id: str = Field(max_length=64)
    severity: Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"] = "HIGH"
    risk_score: int = Field(default=85, ge=0, le=100)
    target_asset: str = Field(default="SERVER-04", max_length=200)
    target_user: Optional[str] = Field(default="dawit.mengistu", max_length=200)
    title_en: Optional[str] = Field(default="Security Incident Alert", max_length=200)
    title_am: Optional[str] = Field(default="የደህንነት ማስጠንቀቂያ", max_length=200)
    channel: Literal["webhook", "email"] = "webhook"

@app.post("/api/v1/alerts/notify")
async def dispatch_alert_notification(
    payload: AlertNotifyRequest,
    _user: Dict[str, Any] = Depends(require_permission("incident:assign")),
):
    alert_dict = payload.model_dump()
    result = alert_notifier.dispatch(alert_dict, channel=payload.channel)
    # Broadcast to the live SOC consoles of the sender's organization only
    await ws_manager.broadcast_to_tenant(org_of(_user), {
        "type": "NEW_ALERT_DISPATCHED",
        "alert": alert_dict,
        "notification": result
    })
    return result

# --- Ingestion & Detection EPS Benchmark Runner ---
@app.get("/api/v1/benchmark/run")
def trigger_benchmark(
    events: int = Query(5000, ge=100, le=50000),
    _user: Dict[str, Any] = Depends(require_permission("user:admin")),
):
    report = run_benchmark(total_events=events, num_workers=4)
    return report


