"""
ETHIO-CYBERGUARD AI Incident Memory Vault
Provides tenant-isolated, ephemeral scratchpad and structured context memory for multi-agent reasoning.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class IncidentMemoryVault:
    """
    Maintains investigation scratchpad per incident and organization.
    Prevents cross-tenant state leakage.
    """

    def __init__(self):
        self._memory: Dict[str, Dict[str, Any]] = {}

    def _key(self, org_id: str, incident_number: str) -> str:
        return f"{org_id}:{incident_number}"

    def set_hypothesis(self, org_id: str, incident_number: str, hypothesis: str, confidence: int):
        k = self._key(org_id, incident_number)
        if k not in self._memory:
            self._memory[k] = {"hypotheses": [], "verified_facts": [], "citations": []}
        self._memory[k]["hypotheses"].append({
            "text": hypothesis,
            "confidence": confidence,
            "recorded_at": datetime.now(timezone.utc).isoformat()
        })

    def add_verified_fact(self, org_id: str, incident_number: str, fact: str, source_citation: str):
        k = self._key(org_id, incident_number)
        if k not in self._memory:
            self._memory[k] = {"hypotheses": [], "verified_facts": [], "citations": []}
        self._memory[k]["verified_facts"].append({
            "fact": fact,
            "source": source_citation,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self._memory[k]["citations"].append(source_citation)

    def get_context(self, org_id: str, incident_number: str) -> Dict[str, Any]:
        k = self._key(org_id, incident_number)
        return self._memory.get(k, {"hypotheses": [], "verified_facts": [], "citations": []})
