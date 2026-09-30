"""
Unit tests for OSINT Attack Surface Reconnaissance
"""

from services.osint.surface_recon import AttackSurfaceRecon


def test_osint_scan_target():
    recon = AttackSurfaceRecon()
    res = recon.scan_target("ethiotelecom.et")
    assert res["target"] == "ethiotelecom.et"
    assert "primary_ip" in res
    assert "asn_info" in res
    assert res["asn_info"]["country"] == "ET"
    assert len(res["subdomains_discovered"]) > 0
    assert len(res["exposed_ports"]) > 0
    assert res["attack_surface_risk_score"] >= 0
    assert "recommendations" in res
