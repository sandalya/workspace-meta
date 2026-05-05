"""
Unit tests for WARM.md diff-mode: parse_warm / serialize_warm / apply_warm_ops.
Run: cd meta/chkp && pytest tests/test_warm_ops.py -v
"""

import os
import sys
import logging
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from chkp import parse_warm, serialize_warm, apply_warm_ops, format_moved_block_for_cold

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")

# ── fixtures ──────────────────────────────────────────────────────────────────

BASIC_WARM = """\
---
project: test
updated: 2026-01-01
---

# WARM — Test Project

## Block Alpha

```yaml
last_touched: 2026-01-01
tags: [alpha, test]
status: active
```

Body of alpha block.

## Block Beta

```yaml
last_touched: 2026-01-15
tags: [beta]
status: done
```

Body of beta block with **markdown**.

## Block Gamma

```yaml
last_touched: 2026-02-01
tags: [gamma]
status: active
```

Body of gamma.
"""

UNICODE_WARM = """\
---
project: тест
updated: 2026-03-01
---

# WARM — Тестовий Проект

## 🚨 ПРАВИЛО: Едік тільки для тестів

```yaml
last_touched: 2026-03-01
tags: [тести, правило]
status: active
```

Функціональні тести тільки через Едіка.

## Архітектура — Смарт Роутер

```yaml
last_touched: 2026-02-15
tags: [архітектура, роутер]
status: active
```

Роутер класифікує intent через Haiku.
"""


def _blocks_equal(a, b):
    """Semantic comparison of two Block lists: title + yaml dict + stripped body."""
    if len(a) != len(b):
        return False
    for ba, bb in zip(a, b):
        if ba["title"] != bb["title"]:
            return False
        if ba["yaml"] != bb["yaml"]:
            return False
        if ba["body"].strip() != bb["body"].strip():
            return False
    return True


# ── parse ─────────────────────────────────────────────────────────────────────

def test_parse_warm_blocks_basic():
    fm, hdr, blocks = parse_warm(BASIC_WARM)
    assert fm.startswith("---")
    assert "project: test" in fm
    assert hdr == "# WARM — Test Project"
    assert len(blocks) == 3
    assert blocks[0]["title"] == "Block Alpha"
    assert blocks[0]["yaml"]["last_touched"] == "2026-01-01"
    assert blocks[0]["yaml"]["tags"] == ["alpha", "test"]
    assert blocks[0]["yaml"]["status"] == "active"
    assert "Body of alpha block." in blocks[0]["body"]
    assert blocks[1]["title"] == "Block Beta"
    assert blocks[2]["title"] == "Block Gamma"


def test_parse_preserves_unicode():
    fm, hdr, blocks = parse_warm(UNICODE_WARM)
    assert "project: тест" in fm
    assert hdr == "# WARM — Тестовий Проект"
    assert len(blocks) == 2
    assert blocks[0]["title"] == "🚨 ПРАВИЛО: Едік тільки для тестів"
    assert blocks[0]["yaml"]["tags"] == ["тести", "правило"]
    assert "Функціональні тести" in blocks[0]["body"]
    assert blocks[1]["title"] == "Архітектура — Смарт Роутер"


# ── serialize roundtrip ───────────────────────────────────────────────────────

def _roundtrip_check(warm_text, project_name):
    fm1, hdr1, blocks1 = parse_warm(warm_text)
    serialized = serialize_warm(fm1, hdr1, blocks1, "2099-12-31")
    fm2, hdr2, blocks2 = parse_warm(serialized)
    assert hdr1 == hdr2, f"{project_name}: header mismatch after roundtrip"
    assert _blocks_equal(blocks1, blocks2), f"{project_name}: blocks mismatch after roundtrip"
    assert "updated: 2099-12-31" in fm2, f"{project_name}: updated date not written"


def test_serialize_roundtrip_insilver():
    path = os.path.join(WORKSPACE, "insilver-v3", "WARM.md")
    if not os.path.exists(path):
        pytest.skip("insilver-v3/WARM.md not found")
    _roundtrip_check(open(path, encoding="utf-8").read(), "insilver-v3")


def test_serialize_roundtrip_sam():
    path = os.path.join(WORKSPACE, "sam", "WARM.md")
    if not os.path.exists(path):
        pytest.skip("sam/WARM.md not found")
    _roundtrip_check(open(path, encoding="utf-8").read(), "sam")


# ── apply_warm_ops ────────────────────────────────────────────────────────────

def test_apply_touch_updates_date():
    new_text, moved = apply_warm_ops(BASIC_WARM, [
        {"op": "touch", "block": "Block Alpha", "last_touched": "2026-05-05"},
    ], "2026-05-05")
    _, _, blocks = parse_warm(new_text)
    alpha = next(b for b in blocks if b["title"] == "Block Alpha")
    assert alpha["yaml"]["last_touched"] == "2026-05-05"
    assert "last_touched: 2026-05-05" in alpha["yaml_raw"]
    assert moved == []


def test_apply_touch_unknown_block_warns_not_raises(caplog):
    with caplog.at_level(logging.WARNING, logger="chkp.warm"):
        new_text, moved = apply_warm_ops(BASIC_WARM, [
            {"op": "touch", "block": "Block Does Not Exist", "last_touched": "2026-05-05"},
        ], "2026-05-05")
    assert "block not found" in caplog.text.lower()
    _, _, blocks = parse_warm(new_text)
    assert len(blocks) == 3
    assert moved == []


def test_apply_add_after_existing():
    new_text, moved = apply_warm_ops(BASIC_WARM, [
        {"op": "add", "after": "Block Alpha",
         "content": "## Block New\n\n```yaml\nlast_touched: 2026-05-05\ntags: [new]\nstatus: active\n```\n\nNew body."},
    ], "2026-05-05")
    _, _, blocks = parse_warm(new_text)
    assert len(blocks) == 4
    assert blocks[0]["title"] == "Block Alpha"
    assert blocks[1]["title"] == "Block New"
    assert blocks[1]["yaml"]["tags"] == ["new"]
    assert "New body." in blocks[1]["body"]
    assert moved == []


def test_apply_add_top():
    new_text, _ = apply_warm_ops(BASIC_WARM, [
        {"op": "add", "after": "TOP",
         "content": "## Block Top\n\n```yaml\nlast_touched: 2026-05-05\ntags: [top]\nstatus: active\n```\n\nAt the top."},
    ], "2026-05-05")
    _, _, blocks = parse_warm(new_text)
    assert blocks[0]["title"] == "Block Top"
    assert len(blocks) == 4


def test_apply_add_bottom():
    new_text, _ = apply_warm_ops(BASIC_WARM, [
        {"op": "add", "after": "BOTTOM",
         "content": "## Block Bottom\n\n```yaml\nlast_touched: 2026-05-05\ntags: [bottom]\nstatus: active\n```\n\nAt the bottom."},
    ], "2026-05-05")
    _, _, blocks = parse_warm(new_text)
    assert blocks[-1]["title"] == "Block Bottom"
    assert len(blocks) == 4


def test_apply_add_unknown_anchor_falls_back_to_bottom(caplog):
    with caplog.at_level(logging.WARNING, logger="chkp.warm"):
        new_text, _ = apply_warm_ops(BASIC_WARM, [
            {"op": "add", "after": "Nonexistent Block",
             "content": "## Block Fallback\n\n```yaml\nlast_touched: 2026-05-05\ntags: []\nstatus: active\n```\n\nFallback."},
        ], "2026-05-05")
    assert "not found" in caplog.text.lower()
    _, _, blocks = parse_warm(new_text)
    assert blocks[-1]["title"] == "Block Fallback"


def test_apply_move_to_cold_removes_and_returns():
    new_text, moved = apply_warm_ops(BASIC_WARM, [
        {"op": "move_to_cold", "block": "Block Beta"},
    ], "2026-05-05")
    _, _, blocks = parse_warm(new_text)
    assert len(blocks) == 2
    assert all(b["title"] != "Block Beta" for b in blocks)
    assert len(moved) == 1
    assert moved[0]["title"] == "Block Beta"
    cold_entry = format_moved_block_for_cold(moved[0], "2026-05-05")
    assert "2026-05-05: Block Beta" in cold_entry
    assert "archived_at: 2026-05-05" in cold_entry
    assert "Body of beta block" in cold_entry


def test_apply_replace_body_preserves_yaml():
    new_text, _ = apply_warm_ops(BASIC_WARM, [
        {"op": "replace_body", "block": "Block Alpha", "content": "Completely new body content."},
    ], "2026-05-05")
    _, _, blocks = parse_warm(new_text)
    alpha = next(b for b in blocks if b["title"] == "Block Alpha")
    assert "Completely new body content." in alpha["body"]
    assert alpha["yaml"]["last_touched"] == "2026-01-01"
    assert alpha["yaml"]["tags"] == ["alpha", "test"]
    assert alpha["yaml"]["status"] == "active"


def test_apply_update_field_status():
    new_text, _ = apply_warm_ops(BASIC_WARM, [
        {"op": "update_field", "block": "Block Alpha", "field": "status", "value": "done"},
    ], "2026-05-05")
    _, _, blocks = parse_warm(new_text)
    alpha = next(b for b in blocks if b["title"] == "Block Alpha")
    assert alpha["yaml"]["status"] == "done"
    assert "status: done" in alpha["yaml_raw"]


def test_apply_update_field_invalid_field_warns(caplog):
    with caplog.at_level(logging.WARNING, logger="chkp.warm"):
        new_text, _ = apply_warm_ops(BASIC_WARM, [
            {"op": "update_field", "block": "Block Alpha", "field": "secret_field", "value": "hack"},
        ], "2026-05-05")
    assert "allowlist" in caplog.text.lower()
    _, _, blocks = parse_warm(new_text)
    alpha = next(b for b in blocks if b["title"] == "Block Alpha")
    assert "secret_field" not in alpha["yaml"]


def test_unknown_op_warns_not_fails(caplog):
    with caplog.at_level(logging.WARNING, logger="chkp.warm"):
        new_text, moved = apply_warm_ops(BASIC_WARM, [
            {"op": "teleport", "block": "Block Alpha"},
        ], "2026-05-05")
    assert "unknown op" in caplog.text.lower()
    _, _, blocks = parse_warm(new_text)
    assert len(blocks) == 3


def test_updated_date_in_frontmatter_changes():
    fm, hdr, blocks = parse_warm(BASIC_WARM)
    serialized = serialize_warm(fm, hdr, blocks, "2099-01-01")
    assert "updated: 2099-01-01" in serialized
    assert "updated: 2026-01-01" not in serialized
