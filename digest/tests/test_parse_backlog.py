"""
Tests for parse_backlog() — pure Python, no AI, no network.
All fixtures use bullet-based BACKLOG structure with inline (Pn) markers.
"""
import pytest
from pathlib import Path
from morning_digest import (
    parse_backlog,
    _extract_all_bullets,
    _extract_inline_priority,
    _strip_priority_marker,
    read_backlog,
)

FIXTURES = Path(__file__).parent / "fixtures"
REAL_BACKLOG = Path(__file__).parents[3] / "meta" / "BACKLOG.md"


# ── Unit: regex for (Pn) markers ──────────────────────────────────────────────

def test_priority_regex_basic():
    """(P0)-(P3) in plain form."""
    assert _extract_inline_priority("fix something (P0)") == 0
    assert _extract_inline_priority("add feature (P1)") == 1
    assert _extract_inline_priority("refactor (P2)") == 2
    assert _extract_inline_priority("nice-to-have (P3)") == 3


def test_priority_regex_with_extra_text():
    """(P3, big plan), (P3, тривіально), (P1, critical) — real BACKLOG examples."""
    assert _extract_inline_priority("retry/backoff на flaky API (P3)") == 3
    assert _extract_inline_priority("nblm_notebook_id consolidation refactor (P3, big plan)") == 3
    assert _extract_inline_priority("wait-loop curriculum reload performance (P3)") == 3
    assert _extract_inline_priority("regen handler stale UI (P3, тривіально)") == 3
    assert _extract_inline_priority("external_stop zombie state (P3, побічний ефект)") == 3


def test_priority_regex_no_match():
    """Must NOT match P4+, plain 'P3' without parens, or (Б) option labels."""
    assert _extract_inline_priority("(P4) out of range") is None
    assert _extract_inline_priority("priority P3 in text") is None
    assert _extract_inline_priority("(А) option label") is None
    assert _extract_inline_priority("(Б, рекомендовано) option") is None
    assert _extract_inline_priority("no marker here") is None


def test_priority_marker_stripped():
    """(Pn) and (Pn, text) are fully removed from item text."""
    assert _strip_priority_marker("fix bug (P2)") == "fix bug"
    assert _strip_priority_marker("refactor (P3, big plan)") == "refactor"
    assert _strip_priority_marker("(P1) urgent task") == "urgent task"


# ── Fixture-based integration tests ──────────────────────────────────────────

def test_parse_inline_priority():
    """(P0)/(P1)/(P2)/(P3) markers route bullets to correct buckets."""
    text = (FIXTURES / "backlog_mixed.md").read_text()
    s = parse_backlog(text)
    assert len(s["p01"]) == 2, f"Expected 2 P0/P1 items, got: {s['p01']}"
    assert len(s["p23"]) == 2, f"Expected 2 P2/P3 items, got: {s['p23']}"
    assert len(s["uncategorized"]) >= 2
    for item in s["p01"] + s["p23"]:
        assert "(P" not in item, f"Priority marker not stripped: {item}"


def test_parse_uncategorized():
    """Bullets without (Pn) markers all land in uncategorized."""
    text = (FIXTURES / "backlog_only_uncategorized.md").read_text()
    s = parse_backlog(text)
    assert s["p01"] == []
    assert s["p23"] == []
    assert len(s["uncategorized"]) > 0


def test_parse_strikethrough_bullet():
    """Bullets with ~~struck~~ content go to done_fallback (not in active buckets)."""
    text = (FIXTURES / "backlog_strikethrough_bullet.md").read_text()
    # No backlog_path → git skipped → done=[] (no fallback)
    s = parse_backlog(text)
    assert s["done"] == [], "Without backlog_path, done must be empty (git-only, no fallback)"

    # Raw extractor still finds struck bullets as done_fallback
    raw = _extract_all_bullets(text)
    assert len(raw["done_fallback"]) >= 2, f"Expected ≥2 struck bullets, got: {raw['done_fallback']}"

    # Active items are clean
    active = s["p01"] + s["p23"] + s["uncategorized"]
    assert len(active) >= 2
    for item in active:
        assert "~~" not in item, f"Residual ~~ in active item: {item!r}"


def test_parse_strikethrough_heading():
    """Bullets under ~~closed~~ heading go to done_fallback (not shown without git)."""
    text = (FIXTURES / "backlog_strikethrough_heading.md").read_text()
    s = parse_backlog(text)
    # No backlog_path → git skipped → done=[]
    assert s["done"] == [], "Without backlog_path, done must be empty (git-only, no fallback)"

    raw = _extract_all_bullets(text)
    assert len(raw["done_fallback"]) >= 3, f"Expected ≥3 items from closed section"

    active = s["p01"] + s["p23"] + s["uncategorized"]
    assert len(active) >= 2

    done_set = set(raw["done_fallback"])
    for item in active:
        assert item not in done_set, f"Done item leaked into active: {item!r}"


def test_parse_real_file():
    """Real BACKLOG.md must parse cleanly and return sensible counts."""
    if not REAL_BACKLOG.exists():
        pytest.skip("Real BACKLOG.md not found")
    text = REAL_BACKLOG.read_text()
    s = parse_backlog(text)

    assert isinstance(s, dict)
    for key in ("p01", "p23", "uncategorized", "done"):
        assert key in s
        assert isinstance(s[key], list)

    # Real BACKLOG has active items
    active_total = len(s["p01"]) + len(s["p23"]) + len(s["uncategorized"])
    assert active_total > 0, "Real BACKLOG must have active items"

    # No ~~ residue in any active bucket
    for item in s["p01"] + s["p23"] + s["uncategorized"]:
        assert "~~" not in item, f"Residual ~~ in active item: {item!r}"

    # Done is empty when no git path given (no fallback)
    assert s["done"] == [], "parse_backlog without path must return done=[]"


def test_read_backlog_accepts_str():
    """read_backlog must accept both str and Path without AttributeError."""
    result = read_backlog(str(REAL_BACKLOG))
    assert isinstance(result, str)
    assert len(result) > 0


def test_synthesize_prompt_language_rule():
    """synthesize.md must contain the language-preservation instruction."""
    prompt_path = Path(__file__).parents[1] / "prompts" / "synthesize.md"
    assert prompt_path.exists(), "prompts/synthesize.md missing"
    text = prompt_path.read_text()
    assert "PRESERVE" in text, "Language rule keyword PRESERVE missing"
    assert "translate" in text.lower(), "No mention of translate in prompt"
    assert "Ukrainian" in text, "Ukrainian language not mentioned in prompt"
