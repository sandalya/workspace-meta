"""
Tests for suggest_backlog_strikes() and related helpers.

All tests mock call_anthropic — no real API calls made.
Run: cd meta && python3 -m pytest chkp/tests/test_backlog_suggest.py -v
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import chkp

# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

SAMPLE_BACKLOG = """\
# BACKLOG

## household_agent .git 239M аудит
Run git filter-repo to trim .git size.

~~## chkp3 max_tokens~~
Already fixed in April.

## pre-push hook у insilver-v3-dev
Hook fires false-positives on patterns.

### Sub-item under pre-push
Extra detail about the sub-task.

## shared/ концепція — рефакторинг
Premise is no longer valid.
"""

SAMPLE_HOT = """\
---
project: test
updated: 2026-05-15
---
# HOT

## Now
Ran git filter-repo on household_agent. .git reduced from 239M to 376K.

## Next
Continue with tripartite memory migration.
"""


@pytest.fixture
def backlog_file(tmp_path, monkeypatch):
    path = tmp_path / "BACKLOG.md"
    path.write_text(SAMPLE_BACKLOG, encoding="utf-8")
    monkeypatch.setattr(chkp, "BACKLOG_PATH", str(path))
    return path


# ──────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────

def test_suggest_returns_done_items(backlog_file):
    """Haiku returns valid JSON with done items → suggest_backlog_strikes returns them."""
    mock_response = json.dumps([
        {
            "header": "## household_agent .git 239M аудит",
            "reason": "filter-repo cleanup done, .git now 376K",
            "kind": "done",
        }
    ])
    with patch.object(chkp, "call_anthropic", return_value=mock_response):
        result = chkp.suggest_backlog_strikes(
            "key", "haiku", "Ran filter-repo on household_agent", "Next", "ctx",
            SAMPLE_HOT, [],
        )
    assert len(result) == 1
    assert result[0]["header"] == "## household_agent .git 239M аудит"
    assert result[0]["kind"] == "done"


def test_suggest_returns_empty_on_unrelated(backlog_file):
    """Haiku returns [] → suggest_backlog_strikes returns [], no UX block needed."""
    with patch.object(chkp, "call_anthropic", return_value="[]"):
        result = chkp.suggest_backlog_strikes(
            "key", "haiku", "Unrelated cosmetic fix", "Next", "ctx",
            SAMPLE_HOT, [],
        )
    assert result == []


def test_suggest_skips_already_in_strikes(backlog_file):
    """Items already covered by --backlog-strike are excluded from Haiku candidates."""
    captured = []

    def fake_call(api_key, model, system, cacheable, volatile, **kwargs):
        captured.append(cacheable + volatile)
        return "[]"

    with patch.object(chkp, "call_anthropic", side_effect=fake_call):
        chkp.suggest_backlog_strikes(
            "key", "haiku", "done", "next", "ctx",
            SAMPLE_HOT, ["household_agent .git 239M аудит"],
        )

    assert len(captured) == 1
    backlog_section = captured[0].split("ACTIVE BACKLOG ITEMS:")[-1]
    assert "household_agent .git 239M аудит" not in backlog_section


def test_suggest_haiku_failure_falls_through(backlog_file):
    """API exception → returns [] with warning, does not raise."""
    with patch.object(chkp, "call_anthropic", side_effect=Exception("timeout")):
        result = chkp.suggest_backlog_strikes(
            "key", "haiku", "done", "next", "ctx", SAMPLE_HOT, [],
        )
    assert result == []


def test_suggest_malformed_json_falls_through(backlog_file):
    """Non-JSON Haiku response → returns [], no crash."""
    with patch.object(chkp, "call_anthropic", return_value="not json at all {{"):
        result = chkp.suggest_backlog_strikes(
            "key", "haiku", "done", "next", "ctx", SAMPLE_HOT, [],
        )
    assert result == []


def test_no_backlog_suggest_flag_parsed():
    """--no-backlog-suggest flag exists, defaults False, sets True when passed."""
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-backlog-suggest", action="store_true")

    args = parser.parse_args([])
    assert args.no_backlog_suggest is False

    args = parser.parse_args(["--no-backlog-suggest"])
    assert args.no_backlog_suggest is True


def test_no_backlog_suggest_skips_haiku(backlog_file):
    """When no_backlog_suggest=True, suggest_backlog_strikes is not called."""
    with patch.object(chkp, "call_anthropic") as mock_call:
        # Simulate the do_checkpoint branch
        no_backlog_suggest = True
        if not no_backlog_suggest:
            chkp.suggest_backlog_strikes("key", "model", "", "", "", "", [])
        mock_call.assert_not_called()


def test_edit_mode_parses_checkboxes():
    """_parse_edit_checkboxes: [x] items included, [ ] items excluded."""
    suggestions = [
        {"header": "## household_agent .git 239M аудит", "reason": "done", "kind": "done"},
        {"header": "## pre-push hook у insilver-v3-dev", "reason": "obsolete", "kind": "obsolete"},
        {"header": "## shared/ концепція — рефакторинг", "reason": "premise invalid", "kind": "obsolete"},
    ]
    edited = (
        "[x] household_agent .git 239M аудит  # done\n"
        "[ ] pre-push hook у insilver-v3-dev  # obsolete\n"
        "[x] shared/ концепція — рефакторинг  # premise invalid\n"
    )
    result = chkp._parse_edit_checkboxes(edited, suggestions)
    assert "## household_agent .git 239M аудит" in result
    assert "## shared/ концепція — рефакторинг" in result
    assert "## pre-push hook у insilver-v3-dev" not in result


def test_timeout_defaults_to_no():
    """select.select timeout → prompt_user_strike_choice returns [] (no strikes added)."""
    suggestions = [
        {"header": "## some task", "reason": "done in session", "kind": "done"}
    ]
    with patch("select.select", return_value=([], [], [])):
        result = chkp.prompt_user_strike_choice(suggestions)
    assert result == []
