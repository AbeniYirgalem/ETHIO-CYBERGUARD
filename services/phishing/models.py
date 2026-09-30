"""
ETHIO-CYBERGUARD Phishing Analysis Models & Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class URLFinding(BaseModel):
    url: str
    is_ip_based: bool
    domain: str
    is_suspicious: bool
    risk_points: int
    threat_category: str

class AttachmentFinding(BaseModel):
    filename: str
    size_bytes: int
    content_type: str
    is_dangerous: bool
    risk_points: int
    explanation: str

class AuthResults(BaseModel):
    spf: str # pass, fail, softfail, neutral, none
    dkim: str # pass, fail, none
    dmarc: str # pass, fail, none
    explanation: str

class RiskFactor(BaseModel):
    factor: str
    points: int
    description: str
    amharic_description: Optional[str] = None

class PhishingVerdict(BaseModel):
    is_phishing: bool
    risk_score: int = Field(ge=0, le=100)
    verdict: str # CLEAN, SUSPICIOUS, HIGH_RISK, CRITICAL_PHISHING
    sender: str
    sender_domain: str
    reply_to: Optional[str] = None
    return_path: Optional[str] = None
    subject: str
    auth_results: AuthResults
    indicators: List[Dict[str, Any]]
    extracted_urls: List[URLFinding]
    attachments: List[AttachmentFinding] = []
    amharic_analysis: Dict[str, Any]
    risk_breakdown: List[RiskFactor]
    summary_en: str
    summary_am: str
    recommended_actions: List[str]
