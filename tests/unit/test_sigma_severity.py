import pytest

from services.detection.evaluator import SigmaRuleEvaluator


@pytest.mark.parametrize(
    ("rule", "expected"),
    [
        ({"level": "informational"}, "INFO"),
        ({"level": "low"}, "LOW"),
        ({"level": "medium"}, "MEDIUM"),
        ({"level": "high"}, "HIGH"),
        ({"level": "critical"}, "CRITICAL"),
        ({"severity": "medium", "level": "critical"}, "MEDIUM"),
        ({"severity": "invalid", "level": "low"}, "LOW"),
        ({}, "HIGH"),
    ],
)
def test_sigma_rule_severity_mapping(rule, expected):
    assert SigmaRuleEvaluator._get_rule_severity(rule) == expected