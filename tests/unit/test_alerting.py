from services.alerting.notifier import AlertNotifier

def test_alert_notifier_dispatch_webhook():
    notifier = AlertNotifier()
    sample_alert = {
        "incident_id": "INC-00042",
        "title_en": "Critical Spearphishing Incident",
        "title_am": "አደገኛ የኢሜይል ማጭበርበር",
        "severity": "CRITICAL",
        "risk_score": 92,
        "target_asset": "SERVER-04",
        "target_user": "dawit.mengistu",
        "vector": "telebirr-bonus.xyz"
    }

    result = notifier.dispatch(sample_alert, channel="webhook")
    assert result["delivered"] is True
    assert result["severity"] == "CRITICAL"
    assert result["escalated"] is True
    assert "attachments" in result["payload"]
    assert result["payload"]["attachments"][0]["color"] == "#FF1744"

def test_alert_notifier_email_amharic():
    notifier = AlertNotifier()
    sample_alert = {
        "incident_id": "INC-00045",
        "severity": "HIGH",
        "risk_score": 85,
        "target_asset": "AWS Console"
    }

    email = notifier.format_email_alert(sample_alert, lang="am")
    assert "አስቸኳይ ማስጠንቀቂያ" in email["subject"]
    assert "INC-00045" in email["subject"]
    assert "የሳይበር ጥቃት ተገኝቷል" in email["subject"]
    assert "ETHIO-CYBERGUARD" in email["body"]
