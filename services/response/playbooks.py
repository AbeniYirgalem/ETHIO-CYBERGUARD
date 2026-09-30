"""
ETHIO-CYBERGUARD SOAR Playbook Loader & Executor
Loads declarative incident response playbooks for automated containment pipelines.
"""

from typing import Dict, Any, List, Optional
import os
import yaml

class PlaybookEngine:
    """Loads and executes structured YAML playbooks."""

    def __init__(self, playbooks_dir: Optional[str] = None):
        self.playbooks_dir = playbooks_dir or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../playbooks")
        )
        self.playbooks: Dict[str, Dict[str, Any]] = {}
        self.load_playbooks()

    def load_playbooks(self):
        if not os.path.exists(self.playbooks_dir):
            return

        for root, _, files in os.walk(self.playbooks_dir):
            for file in files:
                if file.endswith((".yml", ".yaml")):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            pb = yaml.safe_load(f)
                            if pb and "id" in pb:
                                self.playbooks[pb["id"]] = pb
                    except Exception:
                        pass

    def get_playbook(self, playbook_id: str) -> Optional[Dict[str, Any]]:
        return self.playbooks.get(playbook_id)

    def list_playbooks(self) -> List[Dict[str, Any]]:
        return list(self.playbooks.values())
