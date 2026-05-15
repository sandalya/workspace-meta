"""
Tests for --backlog-strike multi-match ambiguity protection.

Scenario: same substring appears in both an example block and a real header.
Without --force: must exit non-zero, leave file unchanged.
With --force: must exit 0, all occurrences struck.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import chkp
from chkp import apply_backlog_flags

FIXTURE_BACKLOG = """\
# BACKLOG

> Приклад: `Duplicate phrase` — що таке дублікат
>

## Duplicate phrase task

- Do the real work

## Other section

- Something else
"""


@pytest.fixture
def backlog_file(tmp_path, monkeypatch):
    path = tmp_path / "BACKLOG.md"
    path.write_text(FIXTURE_BACKLOG, encoding="utf-8")
    monkeypatch.setattr(chkp, "BACKLOG_PATH", str(path))
    return path


def test_multi_match_without_force_exits(backlog_file):
    """Without --force, ambiguous strike must call sys.exit(1)."""
    with pytest.raises(SystemExit) as exc_info:
        apply_backlog_flags(["Duplicate phrase"], [], force=False)
    assert exc_info.value.code == 1


def test_multi_match_without_force_file_unchanged(backlog_file, capsys):
    """Without --force, BACKLOG.md must not be modified."""
    original = backlog_file.read_text()
    with pytest.raises(SystemExit):
        apply_backlog_flags(["Duplicate phrase"], [], force=False)
    assert backlog_file.read_text() == original


def test_multi_match_with_force_strikes_all(backlog_file):
    """With --force, all occurrences of the pattern are struck."""
    apply_backlog_flags(["Duplicate phrase"], [], force=True)
    result = backlog_file.read_text()
    assert result.count("~~Duplicate phrase~~") == 2
    assert "Duplicate phrase" not in result.replace("~~Duplicate phrase~~", "")


def test_single_match_no_force_needed(backlog_file):
    """Single match does not require --force."""
    apply_backlog_flags(["Do the real work"], [], force=False)
    result = backlog_file.read_text()
    assert "~~Do the real work~~" in result
