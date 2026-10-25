"""Sigma field and condition matching for ECS-normalized security events."""

from __future__ import annotations

import fnmatch
import itertools
import re
from typing import Any, Dict, Iterable, List, Mapping, Sequence


class SigmaConditionError(ValueError):
    """Raised when a Sigma condition uses unsupported or invalid syntax."""


class SigmaMatcher:
    """Match event fields and evaluate common Sigma condition expressions.

    Supported condition syntax: selection names, ``and``, ``or``, ``not``,
    parentheses, and ``1|all of <pattern>`` (including ``them``). Selection
    dictionaries use Sigma's default AND-between-fields / OR-between-values
    behavior. Unsupported expressions fail closed rather than creating alerts.
    """

    @staticmethod
    def match_selection(event: Dict[str, Any], selection: Any) -> bool:
        if not isinstance(selection, Mapping):
            return False
        for field, expected in selection.items():
            actual = SigmaMatcher._extract_field(event, str(field))
            if actual is None:
                return False
            if isinstance(expected, list):
                if not any(SigmaMatcher._check_value(actual, value) for value in expected):
                    return False
            elif not SigmaMatcher._check_value(actual, expected):
                return False
        return True

    @staticmethod
    def match_condition(event: Dict[str, Any], detection: Mapping[str, Any]) -> bool:
        """Evaluate a rule's ``detection.condition`` against its selections."""
        condition = detection.get("condition")
        if not isinstance(condition, str) or not condition.strip():
            return False

        selections = {
            str(name): value
            for name, value in detection.items()
            if name != "condition" and isinstance(value, Mapping)
        }
        if not selections:
            return False

        matched = {
            name: SigmaMatcher.match_selection(event, selection)
            for name, selection in selections.items()
        }

        try:
            return SigmaMatcher._evaluate_condition(condition.strip(), matched)
        except SigmaConditionError:
            # A malformed/unsupported rule must never generate a false alert.
            return False

    @staticmethod
    def _evaluate_condition(condition: str, matched: Mapping[str, bool]) -> bool:
        # Expand Sigma quantifiers such as "1 of selection_*" and "all of them".
        quantifier = re.compile(r"\b(\d+|all)\s+of\s+([A-Za-z0-9_*?]+)(?![A-Za-z0-9_])", re.IGNORECASE)

        def expand(match: re.Match[str]) -> str:
            count_text, pattern = match.group(1).lower(), match.group(2)
            names = list(matched) if pattern.lower() == "them" else [
                name for name in matched if fnmatch.fnmatchcase(name, pattern)
            ]
            if not names:
                raise SigmaConditionError(f"No selections match {pattern!r}")
            count = len(names) if count_text == "all" else int(count_text)
            if count < 1 or count > len(names):
                return "FALSE"
            # Expand N-of into combinations of N selections, without eval.
            clauses = []
            for combination in itertools.combinations(names, count):
                clauses.append("(" + " and ".join(combination) + ")")
            return "(" + " or ".join(clauses) + ")"

        expression = quantifier.sub(expand, condition)
        # Tokenize only the supported grammar. Reject every unknown token.
        token_pattern = re.compile(r"\s*(\(|\)|\band\b|\bor\b|\bnot\b|\bTRUE\b|\bFALSE\b|[A-Za-z_][A-Za-z0-9_.*?-]*)", re.IGNORECASE)
        tokens: List[str] = []
        pos = 0
        while pos < len(expression):
            m = token_pattern.match(expression, pos)
            if not m:
                raise SigmaConditionError(f"Unsupported condition syntax near {expression[pos:]!r}")
            tokens.append(m.group(1))
            pos = m.end()

        # Recursive-descent parser: NOT > AND > OR.
        index = 0

        def parse_or() -> bool:
            nonlocal index
            value = parse_and()
            while index < len(tokens) and tokens[index].lower() == "or":
                index += 1
                right = parse_and()
                value = value or right
            return value

        def parse_and() -> bool:
            nonlocal index
            value = parse_not()
            while index < len(tokens) and tokens[index].lower() == "and":
                index += 1
                right = parse_not()
                value = value and right
            return value

        def parse_not() -> bool:
            nonlocal index
            if index < len(tokens) and tokens[index].lower() == "not":
                index += 1
                return not parse_not()
            if index < len(tokens) and tokens[index] == "(":
                index += 1
                value = parse_or()
                if index >= len(tokens) or tokens[index] != ")":
                    raise SigmaConditionError("Missing closing parenthesis")
                index += 1
                return value
            if index >= len(tokens):
                raise SigmaConditionError("Expected a selection name")
            name = tokens[index]
            index += 1
            if name.upper() == "TRUE":
                return True
            if name.upper() == "FALSE":
                return False
            if name not in matched:
                raise SigmaConditionError(f"Unknown selection {name!r}")
            return bool(matched[name])

        result = parse_or()
        if index != len(tokens):
            raise SigmaConditionError(f"Unexpected token {tokens[index]!r}")
        return result

    @staticmethod
    def _extract_field(event: Dict[str, Any], field_path: str) -> Any:
        current: Any = event
        for part in field_path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current

    @staticmethod
    def _check_value(actual: Any, expected: Any) -> bool:
        # Sigma wildcard matching is case-insensitive. Other values are exact.
        actual_values: Iterable[Any] = actual if isinstance(actual, list) else [actual]
        for actual_value in actual_values:
            actual_text = str(actual_value).casefold()
            expected_text = str(expected).casefold()
            if any(char in expected_text for char in "*?"):
                if fnmatch.fnmatchcase(actual_text, expected_text):
                    return True
            elif actual_text == expected_text:
                return True
        return False
