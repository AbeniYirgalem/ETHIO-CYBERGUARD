"""
ETHIO-CYBERGUARD SIGMA Rule Evaluator
Loads YAML rules from detection-rules directories and executes them against incoming events.
"""

from typing import Dict, Any, List, Optional
import os
import yaml
from .matcher import SigmaMatcher
from .severity import SeverityScorer

class SigmaRuleEvaluator:
    """Evaluates active YAML detection rules against events."""

    def __init__(self, rules_dir: Optional[str] = None):
        self.rules_dir = rules_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../detection-rules")
        )
        self.rules: List[Dict[str, Any]] = []
        self.load_rules()

    def load_rules(self):
        self.rules = []
        if not os.path.exists(self.rules_dir):
            return

        for root, _, files in os.walk(self.rules_dir):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            rule = yaml.safe_load(f)
                            if rule and "id" in rule and "detection" in rule:
                                self.rules.append(rule)
                    except Exception:
                        pass

    def evaluate(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        alerts = []
        for rule in self.rules:
            det = rule.get("detection", {})
            selection = det.get("selection", {})
            if SigmaMatcher.match_selection(event, selection):
                alerts.append({
                    "rule_id": rule.get("id"),
                    "title": rule.get("title"),
                    "description": rule.get("description"),
                    "severity": (rule.get("severity") or "HIGH").upper(),
                    "tags": rule.get("tags", []),
                    "mitre_technique": [t for t in rule.get("tags", []) if "attack.t" in t.lower()][:1] or ["T1059"],
                    "false_positives": rule.get("falsepositives", [])
                })
        return alerts
