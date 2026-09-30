"""
ETHIO-CYBERGUARD Phishing Analysis Router
Provides endpoints to analyze emails, headers, URLs, and .eml payloads,
with specific checks for SPF, DKIM, DMARC, Amharic lures, and Ethiopian brand impersonation.
Supports /api/phishing and /api/v1/phishing.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import sys
import os

from services.phishing.email_analyzer import PhishingAnalyzer

router = APIRouter(tags=["Phishing Analyzer & Email Forensics"])
analyzer = PhishingAnalyzer()

class PhishingAnalyzeRequest(BaseModel):
    raw_content: str
    subject: Optional[str] = None
    sender: Optional[str] = None

class URLAnalyzeRequest(BaseModel):
    urls: List[str]

@router.post("/api/phishing/analyze")
@router.post("/api/v1/phishing/analyze")
def analyze_phishing_email(payload: PhishingAnalyzeRequest):
    result = analyzer.analyze(
        raw_content=payload.raw_content,
        subject=payload.subject,
        sender=payload.sender
    )
    return result

@router.post("/api/phishing/upload-eml")
@router.post("/api/v1/phishing/upload-eml")
async def analyze_eml_file(file: UploadFile = File(...)):
    if not file.filename.endswith((".eml", ".msg", ".txt")):
        raise HTTPException(status_code=400, detail="Only .eml, .msg or .txt email files are supported.")
    
    content = await file.read()
    raw_text = content.decode("utf-8", errors="replace")
    
    result = analyzer.analyze(raw_content=raw_text)
    return {
        "filename": file.filename,
        "file_size_bytes": len(content),
        "analysis": result
    }

@router.post("/api/phishing/extract-urls")
def extract_and_inspect_urls(payload: URLAnalyzeRequest):
    inspected = []
    for u in payload.urls:
        is_ip = any(char.isdigit() for char in u.split("/")[2:3]) if "://" in u else False
        inspected.append({
            "url": u,
            "is_ip_based": is_ip,
            "suspicious": is_ip or "telebirr" in u or "login" in u or "verify" in u or "claim" in u,
            "risk_contribution": 35 if is_ip else (25 if "telebirr" in u else 10)
        })
    return {"urls_inspected": len(inspected), "results": inspected}
