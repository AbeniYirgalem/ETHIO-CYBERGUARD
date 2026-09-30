"""
ETHIO-CYBERGUARD External Connectors API Router
Manages external firewall, EDR, email gateway, and DNS integration adapters.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

from services.connectors import CONNECTOR_REGISTRY

router = APIRouter(tags=["External Connectors & Integrations"])

@router.get("/api/connectors")
@router.get("/api/v1/connectors")
def list_connectors():
    """Lists all configured external security connectors and their real-time health."""
    results = []
    for cid, conn in CONNECTOR_REGISTRY.items():
        results.append(conn.health_check())
    return {
        "total": len(results),
        "connectors": results
    }

@router.post("/api/connectors/{connector_id}/test")
@router.post("/api/v1/connectors/{connector_id}/test")
def test_connector_connection(connector_id: str):
    """Executes a diagnostic ping and health check against the requested integration."""
    conn = CONNECTOR_REGISTRY.get(connector_id)
    if not conn:
        raise HTTPException(status_code=404, detail=f"Connector '{connector_id}' not found")
    
    health = conn.health_check()
    return {
        "status": "SUCCESS" if health.get("status") == "HEALTHY" else "FAILED",
        "diagnostic_result": health
    }
