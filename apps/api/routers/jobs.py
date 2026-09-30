"""
ETHIO-CYBERGUARD Background Jobs API Router
Enqueues and monitors heavy asynchronous background security tasks.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from services.jobs.worker import job_manager, JobStatus
from ..dependencies import get_current_user

router = APIRouter(tags=["Background Workers & Jobs"])

class JobCreateRequest(BaseModel):
    job_type: str # phishing_analysis, osint_scan, typosquat_scan, report_generation, threat_intel_lookup
    payload: Dict[str, Any]

@router.post("/api/v1/jobs", status_code=status.HTTP_202_ACCEPTED)
@router.post("/api/jobs", status_code=status.HTTP_202_ACCEPTED)
def submit_job(request: JobCreateRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    user_email = current_user.get("email", "anonymous")
    job_id = job_manager.enqueue(
        job_type=request.job_type,
        payload=request.payload,
        requested_by=user_email
    )
    return {
        "status": "QUEUED",
        "job_id": job_id,
        "job_type": request.job_type,
        "check_status_url": f"/api/v1/jobs/{job_id}"
    }

@router.get("/api/v1/jobs/{job_id}")
@router.get("/api/jobs/{job_id}")
def get_job_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/api/v1/jobs")
@router.get("/api/jobs")
def list_jobs(limit: int = 50):
    return {
        "count": len(job_manager.jobs),
        "jobs": job_manager.list_jobs(limit=limit)
    }
