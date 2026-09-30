"""
ETHIO-CYBERGUARD Threat Intelligence - IOC Schema & Core Definitions
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class IndicatorRecord(BaseModel):
    indicator: str
    type: str # IPV4, DOMAIN, URL, SHA256, REGISTRY
    reputation: str # MALICIOUS, SUSPICIOUS, BENIGN, UNKNOWN
    confidence: int = Field(ge=0, le=100)
    threat_actor: Optional[str] = "Unknown"
    malware: Optional[str] = "Unknown"
    source_feed: str
    target_sector: Optional[str] = "National"
    first_seen: str
    last_verified: str
    is_active: bool = True
