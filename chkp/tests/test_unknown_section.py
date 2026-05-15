"""
Tests for --backlog-add with unknown section:
- validate_backlog_flags returns failure with suggestions from section headers
- CLI exits 2 with message on stderr
"""

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import chkp
from chkp import validate_backlog_flags

FIXTURE_BACKLOG = """\
# BACKLOG

## Alpha section

- item A1
- item A2

## Beta section

- item B1

~~## Closed section~~

- archived
"""


@pytest.fixture
def backlog_file(tmp_path, monkeypatch):
    path = tmp_path / "BACKLOG.md"
    path.write_text(FIXTURE_BACKLOG, encoding="utf-8")
    monkeypatch.setattr(chkp, "BACKLOG_PATH", str(path))
    return path


def test_unknown_section_returns_failure(backlog_file):
    failures = validate_backlog_flags([], [("## Nonexistent section", "- new item")])
    assert len(failures) == 1
    kind, query, suggestions = failures[0]
    assert kind == "add-section"
    assert "Nonexistent" in query


def test_unknown_section_suggestions_from_headers(backlog_file):
    """Suggestions come from actual ## headers, not arbitrary lines."""
    failures = validate_backlog_flags([], [("## Alph section", "- new item")])
    assert len(failures) == 1
    _, _, suggestions = failures[0]
    assert any("Alpha" in s for s in suggestions)


def test_closed_section_not_in_suggestions(backlog_file):
    """Closed (~~...~~) sections must not appear in suggestions pool."""
    # "## Closedish" is not in BACKLOG; "## Closed section" exists but is closed.
    # Suggestions must come only from active sections, so no ~~ in results.
    failures = validate_backlog_flags([], [("## Closedish section XYZ", "- new item")])
    assert len(failures) == 1
    _, _, suggestions = failures[0]
    assert not any("~~" in s for s in suggestions)


def test_cli_exits_nonzero_unknown_section(tmp_path):
    """CLI subprocess must exit non-zero and emit 'not found' on stderr."""
    backlog = tmp_path / "BACKLOG.md"
    backlog.write_text(FIXTURE_BACKLOG, encoding="utf-8")

    chkp_script = str(Path(__file__).parent.parent / "chkp.py")
    result = subprocess.run(
        [sys.executable, chkp_script,
         "meta", "done", "next", "ctx",
         "--backlog-add", "Nonexistent::some text",
         "--dry-run"],
        cwd=str(tmp_path),
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "CHKP_WORKSPACE": str(tmp_path)},
    )
    assert result.returncode != 0
    combined = result.stderr + result.stdout
    assert "not found" in combined.lower() or "match failed" in combined.lower()
