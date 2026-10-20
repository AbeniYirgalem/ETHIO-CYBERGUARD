"""Load Sigma YAML rules and evaluate them against incoming events."""

from typing import Any, Dict, List, Optional
import logging
import os
import yaml

from .matcher import SigmaMatcher

logger = logging.getLogger(__name__)


class SigmaRuleEvaluator:
    """Evaluates active YAML detection rules against events."""

    def __init__(self, rules_dir: Optional[str] = None):
        self.rules_dir = rules_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../detection-rules")
        )
        self.rules: List[Dict[str, Any]] = []
        self.load_rules()

    def load_rules(self) -> None:
        self.rules = []
        if not os.path.exists(self.rules_dir):
            logger.warning("Sigma rules directory does not exist: %s", self.rules_dir)
            return

        for root, _, files in os.walk(self.rules_dir):
            for filename in sorted(files):
                if not filename.endswith((".yml", ".yaml")):
                    continue
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as stream:
                        rule = yaml.safe_load(stream)
                    if not isinstance(rule, dict):
                        logger.warning("Skipping non-mapping Sigma rule: %s", filepath)
                        continue
                    if not rule.get("id") or not isinstance(rule.get("detection"), dict):
                        logger.warning("Skipping rule missing id/detection: %s", filepath)
                        continue
                    self.rules.append(rule)
                except (OSError, yaml.YAMLError) as exc:
                    logger.warning("Could not load Sigma rule %s: %s", filepath, exc)

    @staticmethod
    def _get_rule_severity(rule: Dict[str, Any]) -> str:
        """Normalize custom severity and standard Sigma level."""
        valid_levels = {"INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"}

        for value in (rule.get("severity"), rule.get("level")):
            if not isinstance(value, str) or not value.strip():
                continue

            normalized = value.strip().upper()

            if normalized == "INFORMATIONAL":
                normalized = "INFO"

            if normalized in valid_levels:
                return normalized

        return "HIGH"

    def evaluate(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts: List[Dict[str, Any]] = []
        for rule in self.rules:
            detection = rule.get("detection", {})
            if not SigmaMatcher.match_condition(event, detection):
                continue
            tags = rule.get("tags", [])
            if not isinstance(tags, list):
                tags = []
            techniques = [tag for tag in tags if isinstance(tag, str) and "attack.t" in tag.lower()]
            severity = self._get_rule_severity(rule)
            alerts.append({
                "rule_id": rule.get("id"),
                "title": rule.get("title"),
                "description": rule.get("description"),
                "severity": severity,
                "tags": tags,
                "mitre_technique": techniques[:1] or ["T1059"],
                "false_positives": rule.get("falsepositives", []),
            })
        return alerts
