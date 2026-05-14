"""
morning_digest.py — Daily BACKLOG.md digest → Telegram at 09:00.
Pipeline: READ → PARSE → SYNTHESIZE (Haiku 4.5) → FORMAT → SEND
"""
import argparse
import logging
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

BASE_DIR  = Path(__file__).parent
WORKSPACE = BASE_DIR.parent.parent
BACKLOG_DEFAULT = WORKSPACE / "meta" / "BACKLOG.md"

sys.path.insert(0, str(WORKSPACE))

from shared.logger import setup_logging
from shared.token_tracker import TokenTracker

log = logging.getLogger("morning_digest")

UNCATEGORIZED_CAP = 15

# ── Regex patterns ────────────────────────────────────────────────────────────

# Heading closed formats (all levels 1-6):
#   ~~## full title~~
_CLOSED_HEADING        = re.compile(r'^~~(#{1,6})\s+(.+?)~~\s*$')
#   ## ~~full title~~
_CLOSED_HEADING_INNER  = re.compile(r'^(#{1,6})\s+~~(.+?)~~\s*$')
#   ## ~~partial~~ rest  (struck prefix)
_CLOSED_HEADING_PREFIX = re.compile(r'^(#{1,6})\s+~~(.+?)~~')
#   Any active heading
_ACTIVE_HEADING        = re.compile(r'^(#{1,6})\s+')
#   Bullet line (any indent)
_BULLET_LINE           = re.compile(r'^[ \t]*[-*]\s+(.+)')
#   Fully struck bullet content: ~~...~~
_STRUCK_CONTENT        = re.compile(r'^~~.+~~\s*$')
#   Inline priority marker: (P0), (P1), (P2), (P3), (P3, extra text), etc.
_PRIORITY_MARKER       = re.compile(r'\(P([0-3])[^)]*\)', re.IGNORECASE)


# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    from dotenv import load_dotenv  # lazy: not in system Python
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        log.error(f".env not found at {env_path}. Run: cp .env.example .env and fill values.")
        sys.exit(1)
    load_dotenv(env_path, override=True)
    missing = [k for k in ("SAM_BOT_TOKEN", "OWNER_CHAT_ID", "ANTHROPIC_API_KEY")
               if not os.environ.get(k)]
    if missing:
        log.error(f"Missing env keys: {', '.join(missing)}")
        sys.exit(1)
    return {
        "bot_token": os.environ["SAM_BOT_TOKEN"],
        "chat_id":   os.environ["OWNER_CHAT_ID"],
        "api_key":   os.environ["ANTHROPIC_API_KEY"],
    }


# ── Read ──────────────────────────────────────────────────────────────────────

def read_backlog(path) -> str:
    path = Path(path) if not isinstance(path, Path) else path
    if not path.exists():
        log.warning(f"BACKLOG not found: {path}")
        return ""
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        log.warning("BACKLOG is empty")
    return text


# ── Parse helpers ─────────────────────────────────────────────────────────────

def _heading_info(s: str) -> tuple[int, bool]:
    """Return (level, is_closed) for a stripped heading line. (0, False) if not a heading."""
    m = _CLOSED_HEADING.match(s)
    if m: return len(m.group(1)), True
    m = _CLOSED_HEADING_INNER.match(s)
    if m: return len(m.group(1)), True
    m = _CLOSED_HEADING_PREFIX.match(s)
    if m: return len(m.group(1)), True
    m = _ACTIVE_HEADING.match(s)
    if m: return len(m.group(1)), False
    return 0, False


def _extract_heading_title(s: str) -> str:
    """Extract clean title from a closed heading line (strip hashes, ~~, dates)."""
    for pat in (_CLOSED_HEADING, _CLOSED_HEADING_INNER, _CLOSED_HEADING_PREFIX):
        m = pat.match(s)
        if m:
            title = m.group(2)
            break
    else:
        title = s
    title = title.replace('~~', '')
    title = re.sub(r'\s*\(~?[\d]{4}-[\d]{2}-[\d]{2}\)\s*$', '', title)
    return title.strip()


def _heading_as_item(s: str) -> str:
    """
    Convert an active heading line to a plain item string.
    '#### 5. nblm_notebook_id refactor (P3, big plan)' → 'nblm_notebook_id refactor (P3, big plan)'
    """
    s = re.sub(r'^#{1,6}\s+', '', s)   # strip #### markers
    s = re.sub(r'^\d+[.)]\s+', '', s)  # strip leading '5. '
    return s.strip()


def _extract_inline_priority(text: str) -> int | None:
    """Return 0-3 if (P0)-(P3) found, None otherwise."""
    m = _PRIORITY_MARKER.search(text)
    return int(m.group(1)) if m else None


def _strip_priority_marker(text: str) -> str:
    """Remove (Pn) marker and tidy trailing punctuation."""
    return _PRIORITY_MARKER.sub('', text).strip(' ,.')


# ── Core extractor ────────────────────────────────────────────────────────────

_DONE_SECTION_RE = re.compile(r'✅|DONE\b', re.IGNORECASE)


def _extract_all_bullets(text: str) -> dict:
    """
    Single-pass scan of BACKLOG text. Tracks closed sections.

    Returns {"p0","p1","p2","p3","uncategorized","done_fallback"}: list[str].

    Section state:
      closed_level    — inside a ~~struck~~ heading: all sub-content → done_fallback
      done_sec_level  — inside a '### ✅ DONE'-style heading: #### sub-items are done, skip
      item_sec_level  — inside a #### item heading: bullets are description, skip

    Bullets/headings → classified by (Pn) marker or → uncategorized.
    """
    buckets: dict[str, list[str]] = {
        "p0": [], "p1": [], "p2": [], "p3": [],
        "uncategorized": [], "done_fallback": [],
    }
    closed_level:   int | None = None  # inside a ~~closed~~ section
    done_sec_level: int | None = None  # inside a ✅ DONE sub-section
    item_sec_level: int | None = None  # inside a #### item (skip its bullets)

    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue

        level, is_closed = _heading_info(s)
        if level > 0:
            # ── Closed section tracking ──────────────────────────────────
            if is_closed:
                if closed_level is None or level < closed_level:
                    closed_level = level
            elif closed_level is not None and level <= closed_level:
                closed_level = None

            # ── ✅ DONE sub-section tracking ─────────────────────────────
            if not is_closed and closed_level is None:
                title = _heading_as_item(s)
                if _DONE_SECTION_RE.search(title):
                    done_sec_level = level           # entering ✅ DONE section
                elif done_sec_level is not None and level <= done_sec_level:
                    done_sec_level = None            # leaving ✅ DONE section

            # ── #### item-section tracking (skip description bullets) ────
            if not is_closed and closed_level is None:
                if level >= 4:
                    item_sec_level = level           # entering a #### item block
                elif item_sec_level is not None and level < item_sec_level:
                    item_sec_level = None            # heading at shallower depth → exit

            # ── Extract #### active headings as TODO items ───────────────
            if (level >= 4 and not is_closed
                    and closed_level is None and done_sec_level is None):
                content = _heading_as_item(s)
                prio = _extract_inline_priority(content)
                if prio is not None:
                    buckets[f"p{prio}"].append(_strip_priority_marker(content))
                else:
                    buckets["uncategorized"].append(content)

            continue

        bm = _BULLET_LINE.match(line)
        if not bm:
            continue

        content = bm.group(1).strip()

        # Fully struck bullet
        if _STRUCK_CONTENT.match(content):
            clean = content.replace('~~', '').strip()
            if clean:
                buckets["done_fallback"].append(clean)
            continue

        # Inside a closed section → done
        if closed_level is not None:
            clean = content.replace('~~', '').strip()
            if clean:
                buckets["done_fallback"].append(clean)
            continue

        # Inside a #### item block → description content, skip
        if item_sec_level is not None:
            continue

        # Active bullet — classify by (Pn) marker
        prio = _extract_inline_priority(content)
        if prio is not None:
            buckets[f"p{prio}"].append(_strip_priority_marker(content))
        else:
            buckets["uncategorized"].append(content)

    return buckets


# ── Done-yesterday via git ────────────────────────────────────────────────────

def _done_yesterday_git(backlog_path: Path) -> list[str]:
    """
    Find items that became struck in last 24 h via git log.
    Handles both struck bullets (- ~~text~~) and struck headings (~~## title~~).
    """
    try:
        result = subprocess.run(
            ["git", "log", "-p", "--since=24 hours ago", "--", backlog_path.name],
            capture_output=True, text=True, timeout=15,
            cwd=str(backlog_path.parent),
        )
        if result.returncode != 0 or not result.stdout.strip():
            return []

        done: list[str] = []
        seen: set[str] = set()

        for line in result.stdout.splitlines():
            if not line.startswith('+') or line.startswith('+++'):
                continue
            added = line[1:]  # strip leading '+'

            # Added struck bullet: + - ~~text~~
            bm = _BULLET_LINE.match(added)
            if bm:
                content = bm.group(1).strip()
                if _STRUCK_CONTENT.match(content):
                    clean = content.replace('~~', '').strip()
                    if clean and clean not in seen:
                        done.append(clean)
                        seen.add(clean)
                continue

            # Added struck heading: + ~~## title~~
            level, is_closed = _heading_info(added.strip())
            if level > 0 and is_closed:
                title = _extract_heading_title(added.strip())
                if title and title not in seen:
                    done.append(title)
                    seen.add(title)

        return done
    except Exception as e:
        log.warning(f"git log failed: {e}")
        return []


# ── parse_backlog ─────────────────────────────────────────────────────────────

def parse_backlog(text: str, backlog_path: Path | None = None) -> dict:
    """
    Parse BACKLOG.md.

    Returns {
        "p01":          list[str]  — P0 + P1 items,
        "p23":          list[str]  — P2 + P3 items,
        "uncategorized": list[str] — items without (Pn) marker,
        "done":         list[str]  — struck items from last 24 h (git) or all struck (fallback),
    }
    """
    if not text:
        return {"p01": [], "p23": [], "uncategorized": [], "done": []}

    raw = _extract_all_bullets(text)

    # Done: only items struck in last 24 h (git). No fallback — stale data stays silent.
    done = _done_yesterday_git(backlog_path) if backlog_path else []

    return {
        "p01":          raw["p0"] + raw["p1"],
        "p23":          raw["p2"] + raw["p3"],
        "uncategorized": raw["uncategorized"],
        "done":         done,
    }


# ── Synthesize ────────────────────────────────────────────────────────────────

def _parse_synthesized(raw: str, fallback: dict) -> dict:
    import json
    try:
        clean = raw.strip()
        if clean.startswith("```"):
            parts = clean.split("```")
            clean = parts[1].lstrip("json").strip() if len(parts) > 1 else clean
        data = json.loads(clean)
        return {
            "p01":           data.get("p01",           fallback["p01"]),
            "p23":           data.get("p23",            fallback["p23"]),
            "uncategorized": data.get("uncategorized",  fallback["uncategorized"]),
            "done":          data.get("done",           fallback["done"]),
        }
    except Exception as e:
        log.warning(f"Failed to parse Haiku JSON: {e}. Using raw items.")
        return fallback


def synthesize(sections: dict, client, tracker: TokenTracker) -> dict:
    prompt_path = BASE_DIR / "prompts" / "synthesize.md"
    system_prompt = prompt_path.read_text(encoding="utf-8")

    parts = []
    labels = [("p01", "P0/P1"), ("p23", "P2/P3"),
              ("uncategorized", "Uncategorized"), ("done", "Done")]
    for key, label in labels:
        if sections.get(key):
            bullets = "\n".join(f"- {item}" for item in sections[key])
            parts.append(f"## {label}\n{bullets}")

    if not parts:
        log.info("All sections empty — skipping synthesize")
        return sections

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1500,
            system=[{"type": "text", "text": system_prompt,
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": "\n\n".join(parts)}],
        )
        tracker.track(response.usage, extra={"call_type": "synthesize"})
        return _parse_synthesized(response.content[0].text, sections)
    except Exception as e:
        log.error(f"Haiku synthesize failed: {e}. Using raw items.")
        return sections


# ── Format ────────────────────────────────────────────────────────────────────

def format_message(sections: dict, today: date | None = None) -> str:
    import html as _html
    if today is None:
        today = date.today()

    lines = [f"🌅 Доброго ранку! Дайджест на {today.strftime('%d.%m')}", ""]

    section_defs = [
        ("p01",           "🔴 P0/P1 — Hot &amp; Soon", None),
        ("p23",           "🟢 P2/P3 — Later",           None),
        ("uncategorized", "📥 Uncategorized",            UNCATEGORIZED_CAP),
        ("done",          "✅ Done вчора",                None),
    ]

    for key, header, cap in section_defs:
        items = sections.get(key, [])
        if not items:
            continue

        if cap and len(items) > cap:
            shown_header = f"{header} ({cap} з {len(items)})"
            shown_items  = items[:cap]
            overflow     = len(items) - cap
        else:
            shown_header = header
            shown_items  = items
            overflow     = 0

        lines.append(f"<b>{shown_header}</b>")
        for item in shown_items:
            lines.append(f"• {_html.escape(item)}")
        if overflow:
            lines.append(f"+ ще {overflow} у беклозі")
        lines.append("")

    return "\n".join(lines).rstrip()


# ── Send ──────────────────────────────────────────────────────────────────────

def send_telegram(token: str, chat_id: str, text: str) -> None:
    import httpx  # lazy: not in system Python
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = httpx.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=15,
        )
        resp.raise_for_status()
        log.info("Digest sent successfully")
    except httpx.HTTPStatusError as e:
        log.error(f"Telegram error {e.response.status_code}: {e.response.text[:200]}")
        sys.exit(1)
    except Exception as e:
        log.error(f"Send failed: {e}")
        sys.exit(1)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    setup_logging(agent="digest")
    logging.getLogger("httpx").setLevel(logging.WARNING)

    ap = argparse.ArgumentParser(description="Morning BACKLOG digest → Telegram")
    ap.add_argument("--dry-run",   action="store_true", help="Print to stdout, do not send")
    ap.add_argument("--no-ai",     action="store_true", help="Skip Haiku, send raw items")
    ap.add_argument("--from-file", metavar="PATH",      help="Read BACKLOG from custom path")
    args = ap.parse_args()

    backlog_path = Path(args.from_file) if args.from_file else BACKLOG_DEFAULT
    cfg = load_config()

    text = read_backlog(backlog_path)
    if not text:
        log.warning("Empty BACKLOG — nothing to digest")
        sys.exit(0)

    sections = parse_backlog(text, backlog_path if not args.from_file else None)
    log.info(
        f"Parsed: p01={len(sections['p01'])} p23={len(sections['p23'])} "
        f"uncategorized={len(sections['uncategorized'])} done={len(sections['done'])}"
    )

    if not args.no_ai:
        import anthropic  # lazy: not in system Python
        tracker = TokenTracker(
            log_path=str(WORKSPACE / "shared" / "token_log.jsonl"),
            agent="digest",
            model="haiku",
        )
        ai_client = anthropic.Anthropic(api_key=cfg["api_key"])
        sections = synthesize(sections, ai_client, tracker)

    message = format_message(sections)

    if args.dry_run:
        print("─" * 50)
        print(message)
        print("─" * 50)
        log.info("Dry-run complete. NOT sent.")
    else:
        send_telegram(cfg["bot_token"], cfg["chat_id"], message)


if __name__ == "__main__":
    main()
