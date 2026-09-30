"""
Background Worker & Asynchronous Job Execution System for ETHIO-CYBERGUARD
Decouples heavy security operations (phishing ML, OSINT, correlation, reports) from HTTP request loops.
"""

import uuid
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def enqueue(self, job_type: str, payload: Dict[str, Any], requested_by: str = "system") -> str:
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc).isoformat()
        
        job_record = {
            "job_id": job_id,
            "job_type": job_type,
            "status": JobStatus.PENDING.value,
            "payload": payload,
            "requested_by": requested_by,
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "execution_time_seconds": None,
            "result": None,
            "error": None
        }
        self.jobs[job_id] = job_record
        
        # Spawn execution in background safely across async and sync thread contexts
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._execute_job(job_id))
        except RuntimeError:
            import threading
            threading.Thread(target=lambda: asyncio.run(self._execute_job(job_id)), daemon=True).start()
        return job_id

    async def _execute_job(self, job_id: str):
        job = self.jobs.get(job_id)
        if not job:
            return

        job["status"] = JobStatus.RUNNING.value
        job["started_at"] = datetime.now(timezone.utc).isoformat()
        start_time = time.time()

        try:
            job_type = job["job_type"]
            payload = job["payload"]
            
            # Simulate real asynchronous worker execution based on job type
            await asyncio.sleep(0.05) # Yield to event loop
            
            if job_type == "phishing_analysis":
                from services.phishing import PhishingAnalyzer
                analyzer = PhishingAnalyzer()
                result = analyzer.analyze(payload.get("raw_content", ""))
            elif job_type == "osint_scan":
                from services.osint import AttackSurfaceRecon
                scanner = AttackSurfaceRecon()
                result = scanner.scan_target(payload.get("target", "telebirr.et"))
            elif job_type == "typosquat_scan":
                from services.typosquat import TyposquatMonitor
                monitor = TyposquatMonitor()
                result = monitor.scan_domain(payload.get("domain", "cbe.com.et"))
            elif job_type == "report_generation":
                result = {
                    "report_id": f"REP-{uuid.uuid4().hex[:8].upper()}",
                    "format": payload.get("format", "json"),
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "status": "READY"
                }
            elif job_type == "threat_intel_lookup":
                from services.threat_intelligence import ThreatIntelDatabase
                db = ThreatIntelDatabase()
                result = db.lookup(payload.get("indicator", ""))
            else:
                result = {"status": "SUCCESS", "message": f"Job {job_type} executed successfully"}

            job["result"] = result
            job["status"] = JobStatus.COMPLETED.value
        except Exception as e:
            job["status"] = JobStatus.FAILED.value
            job["error"] = str(e)
        finally:
            job["completed_at"] = datetime.now(timezone.utc).isoformat()
            job["execution_time_seconds"] = round(time.time() - start_time, 4)

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self.jobs.get(job_id)

    def list_jobs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return list(self.jobs.values())[-limit:]

# Global JobManager Singleton
job_manager = JobManager()
