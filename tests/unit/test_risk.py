import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.ai.risk_agent import RiskAssessmentAgent

def test_explainable_risk_calculation():
    agent = RiskAssessmentAgent()
    incident = {
        "incident_number": "INC-00042",
        "affected_asset": "SERVER-04"
    }

    result = agent.assess_risk(incident)
    assert result["overall_score"] == 92
    assert result["severity_label"] == "CRITICAL"
    assert result["metrics"]["impact"] == 90
    assert result["metrics"]["likelihood"] == 87
    assert len(result["contributing_factors"]) == 4

    # Verify factors sum up to total
    factor_sum = sum(f["weight"] for f in result["contributing_factors"])
    assert factor_sum == result["overall_score"]
