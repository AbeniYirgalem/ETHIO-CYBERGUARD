"""
ETHIO-CYBERGUARD SIGMA Matcher
Provides expression and selection matching for SIGMA YAML rules against ECS-normalized events.
"""

from typing import Dict, Any, List
import re

class SigmaMatcher:
    """Matches field expressions against security events."""

    @staticmethod
    def match_selection(event: Dict[str, Any], selection: Dict[str, Any]) -> bool:
        for field, expected in selection.items():
            actual = SigmaMatcher._extract_field(event, field)
            if actual is None:
                return False

            if isinstance(expected, list):
                # Any match in list
                if not any(SigmaMatcher._check_value(actual, exp) for exp in expected):
                    return False
            else:
                if not SigmaMatcher._check_value(actual, expected):
                    return False
        return True

    @staticmethod
    def _extract_field(event: Dict[str, Any], field_path: str) -> Any:
        parts = field_path.split(".")
        curr = event
        for p in parts:
            if isinstance(curr, dict) and p in curr:
                curr = curr[p]
            else:
                return None
        return curr

    @staticmethod
    def _check_value(actual: Any, expected: Any) -> bool:
        act_str = str(actual).lower()
        exp_str = str(expected).lower()

        # Wildcard support (*something*)
        if exp_str.startswith("*") and exp_str.endswith("*"):
            return exp_str[1:-1] in act_str
        elif exp_str.startswith("*"):
            return act_str.endswith(exp_str[1:])
        elif exp_str.endswith("*"):
            return act_str.startswith(exp_str[:-1])
        return act_str == exp_str
