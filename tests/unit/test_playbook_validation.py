from pathlib import Path

import yaml

from services.response.playbooks import PlaybookEngine


def write_yaml(directory: Path, name: str, document):
    path = directory / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(document), encoding="utf-8")
    return path


def valid_playbook(playbook_id="PB-TEST"):
    return {
        "id": playbook_id,
        "name": "Test playbook",
        "trigger": {"incident_type": "test"},
        "steps": [{"id": "step_1", "action": "COLLECT_EVIDENCE", "requires_approval": False}],
    }


def test_loads_valid_playbook(tmp_path):
    write_yaml(tmp_path, "valid.yml", valid_playbook())
    engine = PlaybookEngine(str(tmp_path))
    assert engine.get_playbook("PB-TEST")["name"] == "Test playbook"
    assert len(engine.list_playbooks()) == 1


def test_skips_playbook_with_missing_required_field(tmp_path):
    write_yaml(tmp_path, "invalid.yml", {"id": "PB-BAD", "name": "Missing steps"})
    assert PlaybookEngine(str(tmp_path)).list_playbooks() == []


def test_skips_playbook_with_duplicate_step_ids(tmp_path):
    playbook = valid_playbook()
    playbook["steps"].append({"id": "step_1", "action": "BLOCK_IP"})
    write_yaml(tmp_path, "duplicate-steps.yml", playbook)
    assert PlaybookEngine(str(tmp_path)).list_playbooks() == []


def test_skips_malformed_yaml_and_continues_loading(tmp_path):
    (tmp_path / "broken.yml").write_text("id: [broken", encoding="utf-8")
    write_yaml(tmp_path, "valid.yml", valid_playbook())
    engine = PlaybookEngine(str(tmp_path))
    assert list(engine.playbooks) == ["PB-TEST"]


def test_duplicate_playbook_ids_do_not_overwrite_first_valid_file(tmp_path):
    write_yaml(tmp_path, "a.yml", valid_playbook())
    write_yaml(tmp_path, "b.yml", {**valid_playbook(), "name": "Second definition"})
    engine = PlaybookEngine(str(tmp_path))
    assert engine.get_playbook("PB-TEST")["name"] == "Test playbook"
    assert len(engine.list_playbooks()) == 1


def test_reload_clears_stale_playbooks(tmp_path):
    write_yaml(tmp_path, "valid.yml", valid_playbook())
    engine = PlaybookEngine(str(tmp_path))
    (tmp_path / "valid.yml").unlink()
    engine.load_playbooks()
    assert engine.list_playbooks() == []
