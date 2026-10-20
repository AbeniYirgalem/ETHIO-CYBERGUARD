
from services.detection.matcher import SigmaMatcher


def test_condition_and_or_not_precedence():
    detection = {
        "selection_a": {"process.name": "powershell.exe"},
        "selection_b": {"user.name": "admin"},
        "selection_c": {"event.action": "blocked"},
        "condition": "selection_a and (selection_b or not selection_c)",
    }
    event = {
        "process": {"name": "PowerShell.EXE"},
        "user": {"name": "analyst"},
        "event": {"action": "allowed"},
    }

    assert SigmaMatcher.match_condition(event, detection) is True


def test_condition_requires_all_named_selections():
    detection = {
        "selection_a": {"process.name": "powershell.exe"},
        "selection_b": {"user.name": "admin"},
        "condition": "selection_a and selection_b",
    }

    event = {"process": {"name": "powershell.exe"}}

    assert SigmaMatcher.match_condition(event, detection) is False


def test_condition_supports_one_of_wildcard_selections():
    detection = {
        "selection_process": {"process.name": "powershell.exe"},
        "selection_user": {"user.name": "admin"},
        "condition": "1 of selection_*",
    }

    event = {"process": {"name": "powershell.exe"}}

    assert SigmaMatcher.match_condition(event, detection) is True


def test_condition_supports_all_of_them():
    detection = {
        "selection_process": {"process.name": "powershell.exe"},
        "selection_user": {"user.name": "admin"},
        "condition": "all of them",
    }

    matching_event = {
        "process": {"name": "powershell.exe"},
        "user": {"name": "admin"},
    }
    nonmatching_event = {"process": {"name": "powershell.exe"}}

    assert SigmaMatcher.match_condition(matching_event, detection) is True
    assert SigmaMatcher.match_condition(nonmatching_event, detection) is False


def test_unknown_selection_fails_closed():
    detection = {
        "selection": {"process.name": "powershell.exe"},
        "condition": "missing_selection",
    }

    event = {"process": {"name": "powershell.exe"}}

    assert SigmaMatcher.match_condition(event, detection) is False


def test_condition_supports_wildcard_values():
    detection = {
        "selection": {"process.name": "powershell*"},
        "condition": "selection",
    }

    event = {"process": {"name": "powershell.exe"}}

    assert SigmaMatcher.match_condition(event, detection) is True


def test_selection_supports_multiple_expected_values():
    detection = {
        "selection": {"process.name": ["cmd.exe", "powershell.exe"]},
        "condition": "selection",
    }

    event = {"process": {"name": "powershell.exe"}}

    assert SigmaMatcher.match_condition(event, detection) is True


def test_selection_supports_nested_fields():
    detection = {
        "selection": {"process.parent.name": "explorer.exe"},
        "condition": "selection",
    }

    event = {
        "process": {
            "name": "powershell.exe",
            "parent": {"name": "explorer.exe"},
        }
    }

    assert SigmaMatcher.match_condition(event, detection) is True


def test_malformed_condition_fails_closed():
    detection = {
        "selection": {"process.name": "powershell.exe"},
        "condition": "selection and",
    }

    event = {"process": {"name": "powershell.exe"}}

    assert SigmaMatcher.match_condition(event, detection) is False
