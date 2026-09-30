"""
ETHIO-CYBERGUARD Security Awareness & Phishing Simulation Router
Manages localized awareness campaigns, training modules, and employee vulnerability metrics.
Supports /api/awareness and /api/v1/awareness.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.awareness.simulator import AwarenessSimulator

router = APIRouter(tags=["Security Awareness & Training"])
simulator = AwarenessSimulator()

class AwarenessLaunchRequest(BaseModel):
    campaign_id: str
    department: Optional[str] = "All"

class TrackEventRequest(BaseModel):
    campaign_id: str
    user_email: str
    event_type: str # CLICK, REPORT, SUBMIT_CREDENTIALS

@router.get("/api/awareness/campaigns")
@router.get("/api/v1/awareness/campaigns")
def list_awareness_campaigns():
    return {"campaigns": simulator.get_campaigns()}

@router.get("/api/awareness/metrics")
@router.get("/api/v1/awareness/metrics")
def get_awareness_metrics():
    return simulator.get_org_metrics()

@router.post("/api/awareness/launch")
@router.post("/api/v1/awareness/launch")
def launch_awareness_simulation(payload: AwarenessLaunchRequest):
    return simulator.launch_simulation(campaign_id=payload.campaign_id, department=payload.department)

@router.post("/api/awareness/track-event")
def track_awareness_interaction(payload: TrackEventRequest):
    return {
        "status": "RECORDED",
        "campaign_id": payload.campaign_id,
        "user_email": payload.user_email,
        "event": payload.event_type,
        "educational_tip": (
            "Never enter your Telebirr PIN, mobile OTP, or bank passwords on external domains."
            if "telebirr" in payload.campaign_id or "cbe" in payload.campaign_id else
            "Always inspect sender email address and verify urgency claims with IT security."
        )
    }

@router.get("/api/awareness/modules")
def get_training_modules():
    return {
        "modules": [
            {
                "id": "MOD-01",
                "title_en": "Defending Against Mobile Money & Telebirr Scams",
                "title_am": "የቴሌብር እና የሞባይል ገንዘብ ማጭበርበርን መከላከል",
                "duration_minutes": 10,
                "completion_rate": "89%"
            },
            {
                "id": "MOD-02",
                "title_en": "Executive Impersonation & BEC Wire Fraud",
                "title_am": "የሃሰተኛ የገንዘብ ማዘዣ እና የስራ ሃላፊዎች ስም ማጭበርበር",
                "duration_minutes": 15,
                "completion_rate": "76%"
            },
            {
                "id": "MOD-03",
                "title_en": "Password Hygiene & MFA Protection",
                "title_am": "ጥንቃቄ የተሞላበት የይለፍ ቃል እና ባለሁለት ደረጃ ማረጋገጫ",
                "duration_minutes": 8,
                "completion_rate": "94%"
            }
        ]
    }
