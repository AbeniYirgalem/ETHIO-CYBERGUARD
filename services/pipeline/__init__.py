"""
ETHIO-CYBERGUARD - Unified Security Pipeline & Common Security Graph
Orchestrates: Event Ingestion -> ECS Normalization -> SIGMA Detection ->
Attack Graph Correlation -> Threat Intel -> 7 AI Agents -> Evidence Grounding ->
Dual-Custody SOAR Response -> Immutable Audit Trail.
"""

from .unified_engine import UnifiedPipelineEngine, PipelineExecutionResult

__all__ = ["UnifiedPipelineEngine", "PipelineExecutionResult"]
