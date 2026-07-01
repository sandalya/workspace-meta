"""
Tests for --backlog-strike multi-match ambiguity protection.

Scenario: same substring appears in both an example block and a real header.
Without --force: must exit non-zero, leave file unchanged.
With --force: must exit 0, all occurrences removed (moved to BACKLOG_DONE.md).
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


@pytest.fixture(autouse=True)
def patch_backlog_path_to_tmp(tmp_path, monkeypatch):
    """Ensure BACKLOG_PATH points into tmp_path so BACKLOG_DONE.md goes there too."""
    # If backlog_file fixture already set it, this is a no-op guard
    pass


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


def test_multi_match_with_force_removes_all(backlog_file):
    """With --force, all occurrences of the pattern are removed from BACKLOG.md."""
    apply_backlog_flags(["Duplicate phrase"], [], force=True)
    result = backlog_file.read_text()
    assert "Duplicate phrase" not in result


def test_multi_match_with_force_writes_done(backlog_file):
    """With --force, the removed item is appended to BACKLOG_DONE.md."""
    from pathlib import Path
    apply_backlog_flags(["Duplicate phrase"], [], force=True)
    done_path = Path(chkp.BACKLOG_PATH).parent / "BACKLOG_DONE.md"
    assert done_path.exists()
    done_content = done_path.read_text()
    assert "Duplicate phrase" in done_content


def test_single_match_removes_from_backlog(backlog_file):
    """Single match is removed from BACKLOG.md (not struck through)."""
    apply_backlog_flags(["Do the real work"], [], force=False)
    result = backlog_file.read_text()
    assert "Do the real work" not in result
    assert "~~Do the real work~~" not in result


def test_single_match_appends_to_done(backlog_file):
    """Single match is appended to BACKLOG_DONE.md."""
    from pathlib import Path
    apply_backlog_flags(["Do the real work"], [], force=False)
    done_path = Path(chkp.BACKLOG_PATH).parent / "BACKLOG_DONE.md"
    assert done_path.exists()
    done_content = done_path.read_text()
    assert "Do the real work" in done_content
