"""
Tests for validate_backlog_flags() and _check_backlog_match().

These tests do NOT invoke main flow or mock sys.exit — they test the
validate function directly, checking returned tuples.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import chkp
from chkp import validate_backlog_flags


FIXTURE_CONTENT = """\
# BACKLOG

## Phase 5 — zakaz.ua / metro

- Integrate zakaz.ua order history
- Shopping list priority logic
- Cart item comments for weighted products

## Phase 6 — reporting

- Weekly summary report
- Export to CSV
"""


@pytest.fixture
def backlog_file(tmp_path, monkeypatch):
    path = tmp_path / "BACKLOG.md"
    path.write_text(FIXTURE_CONTENT, encoding="utf-8")
    monkeypatch.setattr(chkp, "BACKLOG_PATH", str(path))
    return path


def test_valid_strike(backlog_file):
    """Exact text present in BACKLOG — no failures."""
    failures = validate_backlog_flags(["Integrate zakaz.ua order history"], [])
    assert failures == []


def test_invalid_strike(backlog_file):
    """Text not in BACKLOG — returns 1 failure with suggestions."""
    failures = validate_backlog_flags(["Integrate zakaz order history"], [])
    assert len(failures) == 1
    kind, query, suggestions = failures[0]
    assert kind == "strike"
    assert query == "Integrate zakaz order history"
    assert len(suggestions) > 0
    assert any("zakaz" in s for s in suggestions)


def test_valid_add_section(backlog_file):
    """Section header present in BACKLOG — no failures."""
    failures = validate_backlog_flags([], [("## Phase 6 — reporting", "- New item")])
    assert failures == []


def test_invalid_add_section(backlog_file):
    """Section header absent in BACKLOG — returns 1 failure."""
    failures = validate_backlog_flags([], [("## Phase 7 — analytics", "- New item")])
    assert len(failures) == 1
    kind, query, suggestions = failures[0]
    assert kind == "add-section"
    assert "Phase 7" in query


def test_mixed_valid_invalid(backlog_file):
    """1 valid strike + 1 invalid strike + 1 valid add → exactly 1 failure (the invalid strike)."""
    failures = validate_backlog_flags(
        [
            "Shopping list priority logic",    # valid
            "Nonexistent backlog item XYZ",    # invalid
        ],
        [("## Phase 5 — zakaz.ua / metro", "- New item")],  # valid
    )
    assert len(failures) == 1
    kind, query, suggestions = failures[0]
    assert kind == "strike"
    assert "Nonexistent" in query


def test_no_flags_skips_file_read(backlog_file):
    """Empty strikes and adds — returns [] without touching BACKLOG."""
    failures = validate_backlog_flags([], [])
    assert failures == []


def test_missing_backlog_returns_empty(tmp_path, monkeypatch):
    """BACKLOG.md absent — returns [] (same as apply_backlog_flags behaviour)."""
    monkeypatch.setattr(chkp, "BACKLOG_PATH", str(tmp_path / "NONEXISTENT.md"))
    failures = validate_backlog_flags(["anything"], [])
    assert failures == []
