"""
ETHIO-CYBERGUARD API Routes Package
Aliases routers to routes to ensure full backward compatibility.
"""

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

__all__ = [
    "auth_router",
    "incidents_router",
    "phishing_router",
    "threat_intel_router",
    "osint_router",
    "typosquat_router",
    "awareness_router",
    "ai_router",
    "response_router",
    "dashboard_router",
    "reports_router",
    "jobs_router",
    "connectors_router",
    "health_router"
]
