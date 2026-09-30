import pytest
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from services.ai.assistant_agent import SecurityAssistantAgent

def test_ai_assistant_grounding_and_citations():
    assistant = SecurityAssistantAgent()
    context = {
        "incident_number": "INC-00042",
        "affected_asset": "SERVER-04"
    }

    # Query: why is this critical
    res = assistant.answer_query("Why is INC-00042 critical?", context)
    assert len(res["citations"]) > 0
    assert "185.220.101.5" in res["reply"]
    assert "SERVER-04" in res["reply"]

    # Verify no imaginary IOCs are introduced
    assert "8.8.8.8" not in res["reply"]
    assert "1.1.1.1" not in res["reply"]
