"""
Unit tests for Typosquatting & Brand Defense Monitor
"""

from services.typosquat.domain_monitor import TyposquatMonitor, levenshtein_distance


def test_levenshtein_distance():
    assert levenshtein_distance("telebirr", "telebirr") == 0
    assert levenshtein_distance("telebirr", "telebir") == 1
    assert levenshtein_distance("cbe", "cbe-bank") == 5


def test_scan_domain_generation():
    monitor = TyposquatMonitor()
    res = monitor.scan_domain("telebirr.et", limit=25)
    assert res["target"] == "telebirr.et"
    assert res["total_mutations_generated"] > 10
    assert len(res["results"]) <= 25

    # Check presence of key mutation types
    techniques = [item["technique"] for item in res["results"]]
    assert any("Homoglyph" in t or "Omission" in t or "Combosquatting" in t for t in techniques)

    # Check critical threats
    assert res["critical_threats_count"] >= 1
