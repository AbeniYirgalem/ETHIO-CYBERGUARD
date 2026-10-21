"""Load and validate declarative SOAR response playbooks."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class PlaybookEngine:
    """Load validated YAML playbooks without silently overwriting duplicates."""

    def __init__(self, playbooks_dir: Optional[str] = None):
        self.playbooks_dir = playbooks_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../playbooks")
        )
        self.playbooks: Dict[str, Dict[str, Any]] = {}
        self.load_playbooks()

    @staticmethod
    def _validate_playbook(playbook: Any) -> Optional[str]:
        """Return a validation error, or None when the document is usable."""
        if not isinstance(playbook, dict):
            return "document must be a YAML mapping"
        for field in ("id", "name", "steps"):
            if field not in playbook:
                return f"missing required field: {field}"
        if not isinstance(playbook["id"], str) or not playbook["id"].strip():
            return "id must be a non-empty string"
        if not isinstance(playbook["name"], str) or not playbook["name"].strip():
            return "name must be a non-empty string"
        if not isinstance(playbook["steps"], list) or not playbook["steps"]:
            return "steps must be a non-empty list"

        step_ids = set()
        for index, step in enumerate(playbook["steps"]):
            if not isinstance(step, dict):
                return f"step {index} must be a mapping"
            for field in ("id", "action"):
                value = step.get(field)
                if not isinstance(value, str) or not value.strip():
                    return f"step {index} requires a non-empty {field}"
            if step["id"] in step_ids:
                return f"duplicate step id: {step['id']}"
            step_ids.add(step["id"])
            if "requires_approval" in step and not isinstance(step["requires_approval"], bool):
                return f"step {index} requires_approval must be a boolean"
        if "trigger" in playbook and not isinstance(playbook["trigger"], dict):
            return "trigger must be a mapping when provided"
        return None

    def load_playbooks(self) -> None:
        """Reload all valid playbooks, logging malformed files and duplicate IDs."""
        self.playbooks = {}
        if not os.path.isdir(self.playbooks_dir):
            logger.warning("SOAR playbooks directory does not exist: %s", self.playbooks_dir)
            return

        for root, _, filenames in os.walk(self.playbooks_dir):
            for filename in sorted(filenames):
                if not filename.endswith((".yml", ".yaml")):
                    continue
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as stream:
                        playbook = yaml.safe_load(stream)
                except (OSError, yaml.YAMLError) as exc:
                    logger.warning("Could not load SOAR playbook %s: %s", filepath, exc)
                    continue

                error = self._validate_playbook(playbook)
                if error:
                    logger.warning("Skipping invalid SOAR playbook %s: %s", filepath, error)
                    continue

                playbook_id = playbook["id"]
                if playbook_id in self.playbooks:
                    logger.warning(
                        "Skipping duplicate SOAR playbook id %s in %s; first valid file wins",
                        playbook_id,
                        filepath,
                    )
                    continue
                self.playbooks[playbook_id] = playbook

    def get_playbook(self, playbook_id: str) -> Optional[Dict[str, Any]]:
        return self.playbooks.get(playbook_id)

    def list_playbooks(self) -> List[Dict[str, Any]]:
        return list(self.playbooks.values())
