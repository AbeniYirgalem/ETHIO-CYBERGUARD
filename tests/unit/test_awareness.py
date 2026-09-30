"""
Unit tests for Cyber Awareness Training & Phishing Simulation
"""

from services.awareness.simulator import AwarenessSimulator


def test_awareness_campaigns():
    sim = AwarenessSimulator()
    campaigns = sim.get_campaigns()
    assert len(campaigns) >= 4
    telebirr_camp = next((c for c in campaigns if "telebirr" in c["id"]), None)
    assert telebirr_camp is not None
    assert "ቴሌብር" in telebirr_camp["title_am"]
    assert len(telebirr_camp["clues"]) > 0


def test_awareness_launch_and_metrics():
    sim = AwarenessSimulator()
    metrics = sim.get_org_metrics()
    assert "departments" in metrics
    assert len(metrics["departments"]) >= 5
    assert metrics["overall_phish_prone_percentage"] > 0

    launch_res = sim.launch_simulation("camp-cbe-kyc", department="Finance & Accounting")
    assert launch_res["status"] == "LAUNCHED"
    assert launch_res["campaign_id"] == "camp-cbe-kyc"
