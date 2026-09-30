"""
Unit tests for Phishing Email & Header Analyzer
"""

from services.phishing.email_analyzer import PhishingAnalyzer


def test_benign_email_analysis():
    analyzer = PhishingAnalyzer()
    benign_raw = """From: alerts@ethiotelecom.et
To: employee@ethiotelecom.et
Subject: Monthly Network Maintenance Schedule
Date: Mon, 30 Sep 2026 09:00:00 +0300
Received-SPF: pass (ethiotelecom.et: domain of alerts@ethiotelecom.et designates 196.188.1.10 as permitted sender)
Authentication-Results: mx.ethiotelecom.et; dkim=pass; dmarc=pass

Dear Team,
Scheduled maintenance on the data center backbone will occur this Saturday at 02:00 AM.
Official documentation is available at https://ethiotelecom.et/maintenance.
"""
    result = analyzer.analyze(raw_content=benign_raw)
    assert not result.is_phishing
    assert result.risk_score < 40
    assert result.auth_results["spf"] == "pass"
    assert result.auth_results["dkim"] == "pass"


def test_malicious_telebirr_phishing_detection():
    analyzer = PhishingAnalyzer()
    phishing_raw = """From: "Telebirr Support" <support@telebirr-bonus.xyz>
Reply-To: phisher-collector@gmail.com
Subject: URGENT: ቴሌብር 10,000 ብር የሽልማት አሸናፊ
Received-SPF: fail
Authentication-Results: mx.ethiotelecom.et; dkim=fail; dmarc=fail

እንኳን ደስ አሎት! የ10,000 ብር የቴሌብር ሽልማት አሸንፈዋል!
አካውንትዎ እንዳይታገድ አሁኑኑ ያረጋግጡ።
የምስጢር ቁጥር ወይም ፒን (PIN / OTP) ለማረጋገጥ ይህን ይጫኑ፡
http://196.188.99.12/claim-prize/login.php
"""
    result = analyzer.analyze(raw_content=phishing_raw)
    assert result.is_phishing
    assert result.risk_score >= 70
    assert result.verdict in ["HIGH_RISK", "CRITICAL_PHISHING"]
    assert result.regional_context["amharic_detected"] is True
    assert result.regional_context["targeted_brand"] is not None
    assert len(result.extracted_urls) > 0
    assert result.extracted_urls[0]["is_suspicious"] is True
    assert any(ind["rule"] == "REPLY_TO_MISMATCH" for ind in result.indicators)
