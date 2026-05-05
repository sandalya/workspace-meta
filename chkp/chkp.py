#!/usr/bin/env python3
"""
VERSION = "3.0"
chkp — AI-powered checkpoint with three-tier memory (HOT/WARM/COLD).

Usage:
    chkp <project> "<what done>" "<next step>" "<context>"
    chkp sam "Added exam module" "Test with real questions" "Phase 3"
    chkp --sonnet sam "Complex refactor" "Continue" "Big changes"
    chkp --init <project_name>       # initialize new project from templates

Projects are registered in kit/projects.yaml.
Requires: ANTHROPIC_API_KEY in project .env or environment.
"""

import sys
import os
import re
import json
import logging
import subprocess
import argparse
import datetime
import urllib.request
import urllib.error

try:
    import yaml
except ImportError:
    print("❌ pyyaml is required. Install: pip3 install pyyaml --break-system-packages", file=sys.stderr)
    sys.exit(1)

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────

WORKSPACE = os.environ.get("CHKP_WORKSPACE") or os.path.expanduser("~/.openclaw/workspace")
META_DIR = os.path.join(WORKSPACE, "meta")
CHKP_DIR = os.path.join(META_DIR, "chkp")
TEMPLATES_DIR = os.path.join(CHKP_DIR, "templates")
PROJECTS_YAML = os.path.join(CHKP_DIR, "projects.yaml")

MODEL_HAIKU = "claude-haiku-4-5-20251001"
MODEL_SONNET = "claude-sonnet-4-20250514"
TIER_FILES = ["HOT.md", "WARM.md", "COLD.md", "MEMORY.md"]
BACKLOG_PATH = os.path.join(WORKSPACE, "BACKLOG.md")

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def die(msg, code=1):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)


def read_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None


def write_file(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def load_projects():
    if not os.path.exists(PROJECTS_YAML):
        die(f"projects.yaml not found at {PROJECTS_YAML}")
    try:
        with open(PROJECTS_YAML, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            die(f"projects.yaml must be a dict, got {type(data).__name__}")
        return data
    except yaml.YAMLError as e:
        die(f"Invalid projects.yaml: {e}")


def load_api_key(project_dir):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        return key
    env_path = os.path.join(project_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip("'\"")
                    if val:
                        return val
    env_path = os.path.join(WORKSPACE, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip("'\"")
                    if val:
                        return val
    return None


_CACHE_MIN_TOKENS = 1024
_CHARS_PER_TOKEN = 4


def call_anthropic(api_key, model, system_prompt, user_prompt_cacheable, user_prompt_volatile,
                   max_tokens=16000, timeout=300):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "prompt-caching-2024-07-31",
    }
    system_block = [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]
    estimated_tokens = len(user_prompt_cacheable) // _CHARS_PER_TOKEN
    if estimated_tokens >= _CACHE_MIN_TOKENS:
        user_content = [
            {"type": "text", "text": user_prompt_cacheable, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": user_prompt_volatile},
        ]
    else:
        user_content = [{"type": "text", "text": user_prompt_cacheable + user_prompt_volatile}]
    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "system": system_block,
        "messages": [{"role": "user", "content": user_content}],
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            text_parts = []
            for block in data.get("content", []):
                if block.get("type") == "text":
                    text_parts.append(block["text"])
            full_text = "\n".join(text_parts)
            usage = data.get("usage", {})
            inp = usage.get("input_tokens", 0)
            out = usage.get("output_tokens", 0)
            cache_r = usage.get("cache_read_input_tokens", 0)
            cache_w = usage.get("cache_creation_input_tokens", 0)
            stop = data.get("stop_reason", "")
            print(f"   📊 Tokens: in={inp} out={out} cache_r={cache_r} cache_w={cache_w} stop={stop}")
            if stop == "max_tokens":
                print(f"   ⚠️  Response truncated at max_tokens={max_tokens}! Consider --sonnet or increasing limit.")
            return full_text
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        die(f"API error {e.code}: {body}")
    except urllib.error.URLError as e:
        die(f"Network error: {e.reason}")


def git_commit_push(project_dir, commit_msg):
    git_dir = project_dir
    if not os.path.isdir(os.path.join(git_dir, ".git")):
        git_dir = WORKSPACE
        if not os.path.isdir(os.path.join(git_dir, ".git")):
            die(f"No git repo in {project_dir} or {WORKSPACE}")
    def run_git(*args):
        return subprocess.run(["git"] + list(args), cwd=git_dir, capture_output=True, text=True)
    run_git("add", "-A")
    result = run_git("commit", "--no-verify", "-m", commit_msg)
    if result.returncode != 0:
        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
            print("   ⚠️  Nothing to commit (working tree clean)")
            return None
        die(f"Git commit failed: {result.stderr}")
    result = run_git("push")
    if result.returncode != 0:
        print(f"   ⚠️  Git push failed: {result.stderr}")
    else:
        print("   ✅ Pushed")
    result = run_git("rev-parse", "--short", "HEAD")
    return result.stdout.strip()


def copy_to_clipboard(text, project_dir):
    prompt_path = os.path.join(project_dir, "PROMPT.md")
    write_file(prompt_path, text)
    if not os.environ.get("DISPLAY"):
        return False
    try:
        proc = subprocess.Popen(
            ["xclip", "-selection", "clipboard"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        proc.communicate(text.encode("utf-8"))
        return proc.returncode == 0
    except FileNotFoundError:
        return False


# ──────────────────────────────────────────────
# --init mode
# ──────────────────────────────────────────────

def do_init(project_name):
    if not project_name or "/" in project_name or " " in project_name:
        die(f"Invalid project name: {project_name!r}")
    projects = load_projects()
    if project_name in projects:
        die(f"Project '{project_name}' already in projects.yaml")
    project_dir = os.path.join(WORKSPACE, project_name)
    os.makedirs(project_dir, exist_ok=True)
    existing = [f for f in TIER_FILES if os.path.exists(os.path.join(project_dir, f))]
    if existing:
        die(
            f"Project dir already has tier files: {', '.join(existing)}\n"
            f"   Remove them manually or pick different project name."
        )
    if not os.path.isdir(TEMPLATES_DIR):
        die(f"Templates dir not found: {TEMPLATES_DIR}")
    today = datetime.date.today().isoformat()
    substitutions = {
        "{PROJECT_NAME}": project_name,
        "{PROJECT_DIR}": project_name,
        "{DATE}": today,
        "{SERVICE_NAME}": project_name,
        "{CURRENT_FOCUS}": "Щойно ініціалізовано через chkp --init. Триярусна памʼять активована.",
        "{LAST_SESSION_SUMMARY}": f"**{today}** — Міграція на HOT/WARM/COLD/MEMORY структуру. Rule Zero прийнято.",
        "{NEXT_STEP_1}": "Заповнити WARM.md реальною архітектурою проекту.",
        "{NEXT_STEP_2}": "Провести першу робочу сесію + чекпоінт через chkp.",
        "{BLOCKERS_OR_NONE}": "Немає.",
        "{BRANCH_STATUS}": "Стан гілки — уточнити.",
        "{OPEN_QUESTIONS_OR_NONE}": "Немає.",
        "{OPEN_QUESTIONS}": "Немає.",
        "{ARCHITECTURE_OVERVIEW}": "(заповнити при першому сеансі)",
        "{COMPONENTS}": "(заповнити при першому сеансі)",
        "{KEY_DECISIONS}": "(заповнити при першому сеансі)",
        "{INTEGRATIONS}": "(заповнити при першому сеансі)",
        "{PROJECT_SPECIFIC_RULES}": "(додати специфічні правила проекту)",
    }
    print(f"\n🚀 Initializing project '{project_name}'...")
    print(f"   📁 Project dir: {project_dir}")
    for tmpl_file in ["MEMORY.md", "HOT.md", "WARM.md", "COLD.md", "PROMPT.md"]:
        src = os.path.join(TEMPLATES_DIR, tmpl_file)
        dst = os.path.join(project_dir, tmpl_file)
        if not os.path.exists(src):
            die(f"Template not found: {src}")
        content = read_file(src)
        for key, val in substitutions.items():
            content = content.replace(key, val)
        write_file(dst, content)
        print(f"      ✅ {tmpl_file}")
    new_entry = {
        "dir": project_name,
        "env_file": f"{project_name}/.env",
        "service": project_name,
    }
    projects[project_name] = new_entry
    with open(PROJECTS_YAML, "w", encoding="utf-8") as f:
        yaml.safe_dump(projects, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    print(f"   ✅ Registered in projects.yaml")
    print(f"\n✅ Project '{project_name}' initialized.")
    print(f"\n   Next steps:")
    print(f"   1. Edit {project_dir}/HOT.md + WARM.md with real state")
    print(f"   2. Run: chkp {project_name} \"done\" \"next\" \"context\"")
    print()


# ──────────────────────────────────────────────
# AI prompt
# ──────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a project memory manager. Your job is to update three-tier project memory files after a development session.

## Three-tier memory model

- **HOT.md** — Current session state. Fully rewritten every checkpoint. Sections: Now, Last done, Next, Blockers, Active branches, Open questions, Reminders.
- **WARM.md** — Architecture & active knowledge. Structured blocks, each starting with `## Title`, followed by a ```yaml``` header (last_touched, tags, status) and body text. Return ONLY a list of operations (warm_ops) — DO NOT return the full WARM text.
- **COLD.md** — Archive. Append-only. Each entry: `## YYYY-MM-DD: Title`, YAML with `archived_at`, `reason`, `tags`, description 3-10 lines.

## Output format

Respond with EXACTLY this JSON structure (no markdown fences, no preamble):
{
  "hot": "<full content of HOT.md>",
  "warm_ops": [
    {"op": "touch", "block": "<exact H2 title>", "last_touched": "YYYY-MM-DD"},
    {"op": "update_field", "block": "<exact H2 title>", "field": "status|tags", "value": "<new value>"},
    {"op": "add", "after": "<exact H2 title> | TOP | BOTTOM", "content": "## Title\\n\\n```yaml\\nlast_touched: YYYY-MM-DD\\ntags: [...]\\nstatus: active\\n```\\n\\nbody text"},
    {"op": "move_to_cold", "block": "<exact H2 title>"},
    {"op": "replace_body", "block": "<exact H2 title>", "content": "<new body — NOT including ## title or yaml header>"}
  ],
  "cold_append": "<new entries to APPEND to COLD.md, or empty string if nothing to archive>",
  "prompt": "<next-session prompt in Ukrainian for pasting into Claude.ai>"
}

## Rules

1. HOT.md: Always rewrite completely. Canonical source for each section:
   - **## Now** (CRITICAL): Write ONLY from the **"WHAT WAS DONE THIS SESSION"** field — 1–3 sentences. No other source is allowed: not the previous HOT.md sections, not WARM.md blocks, not the background context field. Do NOT write "Попередня сесія:" or any summary of past sessions. If unsure whether something belongs in ## Now — it doesn't; use ## Reminders instead.
   - **## Last done**: Bullet-list expanding "What done".
   - **## Next**: From the "Next step" input field.
   - **## Reminders**: Keep from previous HOT if still relevant.
2. WARM.md — warm_ops rules:
   - For blocks affected by this session: emit {"op": "touch", "block": "<exact title>", "last_touched": "<today>"}
   - For new architecture/concepts introduced this session: emit {"op": "add", "after": "BOTTOM", "content": "## Title\\n\\n```yaml\\n...\\n```\\n\\nbody"}
   - For blocks needing body update: emit {"op": "replace_body", "block": "...", "content": "<body only>"}
   - For blocks with status:done AND last_touched older than 30 days: emit {"op": "move_to_cold", "block": "..."}
   - "block" value MUST be the EXACT H2 title string (copy from the WARM block index provided — do not paraphrase)
   - DO NOT return the full WARM text. Return only operations that need to change.
   - If nothing changes in WARM, return an empty array: "warm_ops": []
3. COLD.md: cold_append is APPENDED to existing file. Use append format: `---\\n\\n## YYYY-MM-DD: Title\\n...`. Empty string if nothing to archive.
4. Prompt: Write in Ukrainian. Include: project name, current state summary (2-3 sentences), what to do next, any blockers. Format it as a message the developer will paste into a new Claude.ai session. Start with "Проект: <n>". Include instruction to share HOT.md + WARM.md. Keep it under 15 lines.
5. Preserve the YAML frontmatter (---\\nproject: ...\\nupdated: ...\\n---) at the top of HOT.md. Update the `updated` date to today. (WARM frontmatter is updated automatically by the system.)
6. Keep all content in the same language as the original files (Ukrainian or English, match what's there).
7. Do NOT invent information. Only use what's provided in the current files and session description.
"""


def _redact_now_for_context(hot: str) -> str:
    """Replace ## Now and ## Last done with placeholders.

    Prevents the model from copy-pasting previous session content into the new
    HOT.md. Both sections are derived from "What done" of the CURRENT session.
    All other sections (Next, Reminders, Blockers, Active branches) are kept
    intact so the model has full continuity context.
    """
    if not hot:
        return hot
    result = re.sub(
        r"(## Now\n+).*?(?=\n## |\Z)",
        r"\1[PREVIOUS SESSION — generate NEW ## Now from \"What done\" in session summary above]\n",
        hot,
        flags=re.DOTALL,
    )
    result = re.sub(
        r"(## Last done\n+).*?(?=\n## |\Z)",
        r"\1[PREVIOUS SESSION — generate NEW ## Last done from \"What done\" in session summary above]\n",
        result,
        flags=re.DOTALL,
    )
    return result


def build_user_prompt(project, what_done, next_step, context, hot, warm, cold, memory, today):
    # Build WARM block index for model reference (exact titles for warm_ops)
    index_lines = ["=== WARM block index (use exact titles in warm_ops) ==="]
    if warm:
        _, _, _idx_blocks = parse_warm(warm)
        for b in _idx_blocks:
            lt = b["yaml"].get("last_touched", "?")
            st = b["yaml"].get("status", "?")
            index_lines.append(f"{b['title']} [last_touched: {lt}, status: {st}]")
    else:
        index_lines.append("(empty)")
    warm_index = "\n".join(index_lines)

    # Cacheable prefix: stable memory files (WARM/COLD/MEMORY rarely change between consecutive calls)
    prefix_parts = [
        warm_index,
        "",
        "=== Current WARM.md ===",
        warm or "(empty — first checkpoint, create from scratch)",
        "",
        "=== Current COLD.md ===",
        cold or "(empty — first checkpoint)",
        "",
    ]
    if memory:
        prefix_parts.extend(["=== MEMORY.md (read-only, do not modify) ===", memory, ""])

    # Volatile suffix: session info + HOT (always new each checkpoint)
    volatile_parts = [
        f"Project: {project}",
        f"Date: {today}",
        "=== CURRENT SESSION INPUT ===",
        f"WHAT WAS DONE THIS SESSION (→ use for ## Now and ## Last done): {what_done}",
        f"NEXT STEP (→ use for ## Next): {next_step}",
        f"BACKGROUND CONTEXT (do NOT use for ## Now; background only): {context}",
        "",
        "=== Current HOT.md (## Now and ## Last done show PAST sessions; rewrite both from What done above) ===",
        _redact_now_for_context(hot) if hot else "(empty — first checkpoint, create from scratch)",
        "",
    ]
    return "\n".join(prefix_parts), "\n".join(volatile_parts)


# ──────────────────────────────────────────────
# WARM diff-mode: parse / serialize / apply_warm_ops
# ──────────────────────────────────────────────

_warm_log = logging.getLogger("chkp.warm")
_ALLOWED_UPDATE_FIELDS = {"last_touched", "tags", "status"}


def _update_yaml_raw_field(yaml_raw, field, value):
    """Regex-replace one field in a yaml_raw string. Preserves original formatting."""
    if isinstance(value, list):
        val_str = "[" + ", ".join(str(v) for v in value) + "]"
    else:
        val_str = str(value)
    pattern = rf'^({re.escape(field)}:\s*).*$'
    new_raw, count = re.subn(pattern, lambda m: m.group(1) + val_str, yaml_raw, flags=re.MULTILINE)
    if count == 0:
        new_raw = yaml_raw.rstrip('\n') + f'\n{field}: {val_str}'
    return new_raw


def _find_block(blocks, title):
    for i, b in enumerate(blocks):
        if b["title"] == title:
            return i
    return -1


def parse_warm(text):
    """Parse WARM.md into (frontmatter_str, header_str, blocks).

    Each block: {"title", "yaml_raw", "yaml", "body"}.
    yaml dict has datetime.date values converted to ISO strings.
    """
    if not text:
        return "", "", []

    fm_match = re.match(r'^(---\n.*?\n---)\n?', text, re.DOTALL)
    frontmatter_str = fm_match.group(1) if fm_match else ""
    rest = text[fm_match.end():] if fm_match else text

    header_match = re.search(r'(# [^\n]+)', rest)
    header_str = header_match.group(1) if header_match else ""
    after_header = rest[header_match.end():] if header_match else rest

    raw_chunks = re.split(r'\n## ', after_header)
    blocks = []
    for chunk in raw_chunks[1:]:
        nl_idx = chunk.find('\n')
        if nl_idx == -1:
            title, content = chunk.strip(), ""
        else:
            title, content = chunk[:nl_idx].strip(), chunk[nl_idx + 1:]

        ym = re.search(r'```yaml\n(.*?)\n```', content, re.DOTALL)
        if ym:
            yaml_raw = ym.group(1)
            try:
                yaml_data = yaml.safe_load(yaml_raw) or {}
                for k, v in list(yaml_data.items()):
                    if hasattr(v, 'isoformat'):
                        yaml_data[k] = v.isoformat()
            except Exception:
                yaml_data = {}
            body = content[ym.end():].strip('\n')
        else:
            yaml_raw, yaml_data, body = "", {}, content.strip('\n')

        blocks.append({"title": title, "yaml_raw": yaml_raw, "yaml": yaml_data, "body": body})

    return frontmatter_str, header_str, blocks


def serialize_warm(frontmatter_str, header_str, blocks, today):
    """Rebuild WARM.md text. Updates 'updated:' date in frontmatter."""
    updated_fm = re.sub(r'(updated:\s*)[\d-]+', lambda m: m.group(1) + today, frontmatter_str)
    parts = [updated_fm, "", header_str]
    for block in blocks:
        block_text = f"## {block['title']}\n\n```yaml\n{block['yaml_raw']}\n```"
        if block["body"].strip():
            block_text += f"\n\n{block['body']}"
        parts.append("")
        parts.append(block_text)
    return "\n".join(parts) + "\n"


def apply_warm_ops(warm_text, ops, today):
    """Apply warm_ops list to warm_text. Returns (new_warm_text, moved_to_cold: list[Block])."""
    frontmatter_str, header_str, blocks = parse_warm(warm_text)
    moved_to_cold = []

    for op_dict in ops:
        op = op_dict.get("op", "")

        if op == "touch":
            idx = _find_block(blocks, op_dict.get("block", ""))
            if idx == -1:
                _warm_log.warning("warm_ops touch: block not found: %r", op_dict.get("block"))
                continue
            new_date = op_dict.get("last_touched", today)
            blocks[idx]["yaml"]["last_touched"] = new_date
            blocks[idx]["yaml_raw"] = _update_yaml_raw_field(blocks[idx]["yaml_raw"], "last_touched", new_date)

        elif op == "update_field":
            field = op_dict.get("field", "")
            if field not in _ALLOWED_UPDATE_FIELDS:
                _warm_log.warning("warm_ops update_field: field %r not in allowlist", field)
                continue
            idx = _find_block(blocks, op_dict.get("block", ""))
            if idx == -1:
                _warm_log.warning("warm_ops update_field: block not found: %r", op_dict.get("block"))
                continue
            value = op_dict.get("value")
            blocks[idx]["yaml"][field] = value
            blocks[idx]["yaml_raw"] = _update_yaml_raw_field(blocks[idx]["yaml_raw"], field, value)

        elif op == "add":
            content = op_dict.get("content", "").lstrip('\n')
            after = op_dict.get("after", "BOTTOM")
            if content.startswith("## "):
                content = content[3:]
            nl_idx = content.find('\n')
            if nl_idx == -1:
                new_title, new_content = content.strip(), ""
            else:
                new_title, new_content = content[:nl_idx].strip(), content[nl_idx + 1:]

            ym = re.search(r'```yaml\n(.*?)\n```', new_content, re.DOTALL)
            if ym:
                new_yaml_raw = ym.group(1)
                try:
                    new_yaml = yaml.safe_load(new_yaml_raw) or {}
                    for k, v in list(new_yaml.items()):
                        if hasattr(v, 'isoformat'):
                            new_yaml[k] = v.isoformat()
                except Exception:
                    new_yaml = {}
                new_body = new_content[ym.end():].strip('\n')
            else:
                new_yaml_raw, new_yaml, new_body = "", {}, new_content.strip('\n')

            new_block = {"title": new_title, "yaml_raw": new_yaml_raw, "yaml": new_yaml, "body": new_body}
            if after == "TOP":
                blocks.insert(0, new_block)
            elif after == "BOTTOM":
                blocks.append(new_block)
            else:
                anchor = _find_block(blocks, after)
                if anchor == -1:
                    _warm_log.warning("warm_ops add: anchor %r not found, appending to BOTTOM", after)
                    blocks.append(new_block)
                else:
                    blocks.insert(anchor + 1, new_block)

        elif op == "move_to_cold":
            idx = _find_block(blocks, op_dict.get("block", ""))
            if idx == -1:
                _warm_log.warning("warm_ops move_to_cold: block not found: %r", op_dict.get("block"))
                continue
            moved_to_cold.append(blocks.pop(idx))

        elif op == "replace_body":
            idx = _find_block(blocks, op_dict.get("block", ""))
            if idx == -1:
                _warm_log.warning("warm_ops replace_body: block not found: %r", op_dict.get("block"))
                continue
            blocks[idx]["body"] = op_dict.get("content", "").strip('\n')

        else:
            _warm_log.warning("warm_ops: unknown op %r, skipping", op)

    return serialize_warm(frontmatter_str, header_str, blocks, today), moved_to_cold


def format_moved_block_for_cold(block, today):
    """Format a WARM Block as a COLD.md archive entry."""
    tags = block["yaml"].get("tags", [])
    tags_str = "[" + ", ".join(str(t) for t in tags) + "]" if isinstance(tags, list) else str(tags)
    status = block["yaml"].get("status", "done")
    yaml_section = f"archived_at: {today}\nreason: moved from WARM (status:{status}, stale)\ntags: {tags_str}"
    result = f"## {today}: {block['title']}\n\n```yaml\n{yaml_section}\n```"
    if block["body"].strip():
        result += f"\n\n{block['body']}"
    return result


def apply_backlog_flags(strikes, adds):
    """Mechanical apply of CLI-provided strike/add operations to BACKLOG.md.

    strikes: list of strings — each is exact text to wrap in ~~...~~
    adds: list of (section, text) tuples — section is exact header line, text is content to insert
    """
    if not strikes and not adds:
        return

    content = read_file(BACKLOG_PATH)
    if content is None:
        print("   ⚠️    BACKLOG.md not found, skipping backlog flags.")
        return

    print("\n   📋 Applying BACKLOG flags...")

    applied_strikes = 0
    skipped_strikes = 0
    for match in strikes:
        match = match.strip()
        if not match:
            continue
        if match in content:
            content = content.replace(match, f"~~{match}~~", 1)
            applied_strikes += 1
            preview = match[:60] + ("..." if len(match) > 60 else "")
            print(f"      ✏️   strike: \"{preview}\"")
        else:
            preview = match[:60] + ("..." if len(match) > 60 else "")
            print(f"      ⚠️    not found: \"{preview}\" — skip")
            skipped_strikes += 1

    applied_adds = 0
    skipped_adds = 0
    for section, text in adds:
        section = section.strip()
        text = text.rstrip()
        if not section or not text:
            continue
        idx = content.find(section)
        if idx == -1:
            preview = section[:60] + ("..." if len(section) > 60 else "")
            print(f"      ⚠️    section not found: \"{preview}\" — skip")
            skipped_adds += 1
            continue
        line_end = content.find("\n", idx)
        if line_end == -1:
            content = content + "\n" + text + "\n"
        else:
            insert_pos = line_end + 1
            if insert_pos < len(content) and content[insert_pos] == "\n":
                insert_pos += 1
            content = content[:insert_pos] + text + "\n\n" + content[insert_pos:]
        applied_adds += 1
        sec_preview = section[:50] + ("..." if len(section) > 50 else "")
        text_preview = text[:60] + ("..." if len(text) > 60 else "")
        print(f"      ➕  add to \"{sec_preview}\": \"{text_preview}\"")

    write_file(BACKLOG_PATH, content)
    print(f"   ✅ BACKLOG: {applied_strikes} strikes, {applied_adds} adds"
          + (f" (skipped: {skipped_strikes}+{skipped_adds})" if skipped_strikes or skipped_adds else ""))


def commit_backlog(project):
    if project == "meta":
        return
    git_dir = META_DIR
    if not os.path.isdir(os.path.join(git_dir, ".git")):
        git_dir = WORKSPACE
        if not os.path.isdir(os.path.join(git_dir, ".git")):
            return

    def run_git(*args):
        return subprocess.run(["git"] + list(args), cwd=git_dir, capture_output=True, text=True)

    real_path = os.path.realpath(BACKLOG_PATH)
    try:
        rel_path = os.path.relpath(real_path, git_dir)
    except ValueError:
        rel_path = "BACKLOG.md"

    status = run_git("status", "--porcelain", rel_path)
    if not status.stdout.strip():
        return

    print("\n   📋 Committing BACKLOG.md...")
    run_git("add", rel_path)
    result = run_git("commit", "--no-verify", "-m", "chore(backlog): update via chkp")
    if result.returncode != 0:
        if "nothing to commit" not in (result.stdout + result.stderr):
            print(f"   ⚠️  BACKLOG commit failed: {result.stderr.strip()}")
        return
    result = run_git("push")
    if result.returncode != 0:
        print(f"   ⚠️  BACKLOG push failed: {result.stderr.strip()}")
    else:
        print("   ✅ BACKLOG.md pushed.")


# ──────────────────────────────────────────────
# Checkpoint mode
# ──────────────────────────────────────────────

def do_checkpoint(args, projects):
    project_cfg = projects[args.project]
    project_dir = os.path.join(WORKSPACE, project_cfg["dir"])
    if not os.path.isdir(project_dir):
        die(f"Project dir not found: {project_dir}")

    # Detect dev-vs-prod mismatch (Model A workflow)
    # Warn only when cwd basename equals "<project>-dev" — i.e. dev-counterpart of THIS project.
    # Cross-project chkp (e.g. cd insilver-v3-dev && chkp meta) — no warning.
    cwd_base = os.path.basename(os.getcwd())
    if cwd_base == args.project + "-dev":
        print(f"\n\u26a0\ufe0f  WARNING: запущено з dev-каталогу проекту {args.project}", file=sys.stderr)
        print(f"   chkp оновить prod-каталог: {project_dir}", file=sys.stderr)
        print(f"   Це нормально per Model A (single prod-memory).", file=sys.stderr)
        print(f"   Продовжити? [y/N] ", end="", file=sys.stderr, flush=True)
        if input().strip().lower() != "y":
            die("Скасовано користувачем.")
    api_key = load_api_key(project_dir)
    if not api_key:
        die("ANTHROPIC_API_KEY not found in .env or environment")
    key_suffix = api_key[-4:]
    print(f"🔑 API key: ...{key_suffix}")
    hot = read_file(os.path.join(project_dir, "HOT.md"))
    warm = read_file(os.path.join(project_dir, "WARM.md"))
    cold = read_file(os.path.join(project_dir, "COLD.md"))
    memory = read_file(os.path.join(project_dir, "MEMORY.md"))
    if hot is None and warm is None:
        die(
            f"No HOT.md or WARM.md in {project_dir}.\n"
            f"   Create initial tier files first (or run: chkp --init {args.project})."
        )
    today = datetime.date.today().isoformat()
    model = MODEL_SONNET if args.sonnet else MODEL_HAIKU
    print(f"\n{'='*50}")
    print(f"  chkp — {args.project} [{model.split('-')[1]}]")
    print(f"{'='*50}")
    print(f"   📝 {args.what_done}")
    print(f"   ➡️  {args.next_step}")
    print(f"   📎 {args.context}")
    print(f"\n   🤖 Calling {model}...")
    cacheable, volatile = build_user_prompt(
        args.project, args.what_done, args.next_step, args.context,
        hot, warm, cold, memory, today,
    )
    response_text = call_anthropic(api_key, model, SYSTEM_PROMPT, cacheable, volatile)
    try:
        text = response_text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)
        result = json.loads(text)
    except json.JSONDecodeError:
        if args.sonnet:
            die(f"Failed to parse AI response as JSON:\n{response_text[:500]}")
        else:
            print(f"\n   ⚠️  Haiku response not valid JSON, retrying with Sonnet...")
            response_text = call_anthropic(api_key, MODEL_SONNET, SYSTEM_PROMPT, cacheable, volatile)
            try:
                text = response_text.strip()
                if text.startswith("```"):
                    lines = text.split("\n")
                    lines = [l for l in lines if not l.strip().startswith("```")]
                    text = "\n".join(lines)
                result = json.loads(text)
            except json.JSONDecodeError:
                die(f"Sonnet fallback also failed:\n{response_text[:500]}")
    for field in ["hot", "prompt"]:
        if field not in result or not result[field].strip():
            die(f"AI response missing or empty field: {field}")
    if "warm_ops" not in result and "warm" not in result:
        die("AI response missing both 'warm_ops' and 'warm'")
    if args.dry_run:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    print("\n   📁 Writing tier files...")
    WARM_path = os.path.join(project_dir, "WARM.md")
    write_file(os.path.join(project_dir, "HOT.md"), result["hot"])
    print(f"      HOT.md  ✅ ({len(result['hot'].splitlines())} lines)")
    cold_append = result.get("cold_append", "").strip()
    if "warm_ops" in result:
        new_warm, moved = apply_warm_ops(warm or "", result["warm_ops"], today)
        write_file(WARM_path, new_warm)
        print(f"      WARM.md ✅ (warm_ops: {len(result['warm_ops'])} ops → {len(new_warm.splitlines())} lines)")
        if moved:
            cold_extra = "\n\n".join(format_moved_block_for_cold(b, today) for b in moved)
            cold_append = (cold_append + "\n\n" + cold_extra).strip() if cold_append else cold_extra
    else:
        write_file(WARM_path, result["warm"])
        print(f"      WARM.md ✅ ({len(result['warm'].splitlines())} lines) [legacy format]")
    if cold_append:
        cold_path = os.path.join(project_dir, "COLD.md")
        existing_cold = read_file(cold_path) or ""
        write_file(cold_path, existing_cold.rstrip() + "\n\n" + cold_append + "\n")
        print(f"      COLD.md ✅ (appended {len(cold_append.splitlines())} lines)")
    else:
        print(f"      COLD.md — (no changes)")
    adds_parsed = []
    for s in (args.backlog_add or []):
        if "::" not in s:
            print(f"   ⚠️    --backlog-add без '::' розділювача: {s!r} — skip")
            continue
        section, text = s.split("::", 1)
        adds_parsed.append((section, text))
    apply_backlog_flags(args.backlog_strike or [], adds_parsed)
    # Save PROMPT.md before commit so git add -A includes it
    prompt = result["prompt"]
    prompt_path = os.path.join(project_dir, "PROMPT.md")
    write_file(prompt_path, prompt)

    print("\n   🔀 Git commit & push...")
    commit_msg = (
        f"chkp({args.project}): {args.what_done}\n\n"
        f"Next: {args.next_step}\n"
        f"Context: {args.context}"
    )
    sha = git_commit_push(project_dir, commit_msg)
    if sha:
        print(f"   Commit: {sha}")
    commit_backlog(args.project)
    print(f"\n{'='*50}")
    print("  📋 NEXT SESSION PROMPT")
    print(f"{'='*50}\n")
    print(prompt)
    print(f"\n{'='*50}\n")
    if copy_to_clipboard(prompt, project_dir):
        print(f"   📎 Copied to clipboard + saved to PROMPT.md")
    else:
        print(f"   📄 Saved to {project_dir}/PROMPT.md (xclip unavailable)")
    print("\n   ✅ chkp done.\n")


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    if "--init" in sys.argv:
        parser = argparse.ArgumentParser(description="chkp --init <project>")
        parser.add_argument("--init", metavar="PROJECT", required=True, help="Initialize new project")
        args = parser.parse_args()
        do_init(args.init)
        return
    projects = load_projects()
    parser = argparse.ArgumentParser(
        description="chkp — AI-powered three-tier memory checkpoint",
        usage='chkp [--sonnet] <project> "<what done>" "<next step>" "<context>"\n'
              '       chkp --init <project>',
    )
    parser.add_argument("--sonnet", action="store_true", help="Use Sonnet instead of Haiku")
    parser.add_argument("--dry-run", action="store_true", help="Print parsed AI response JSON to stdout, skip writing files and git")
    parser.add_argument(
        "--backlog-strike",
        action="append",
        default=[],
        metavar="TEXT",
        help="Substring у BACKLOG.md що буде обгорнуто в ~~...~~. Можна повторювати."
    )
    parser.add_argument(
        "--backlog-add",
        action="append",
        default=[],
        metavar="SECTION::TEXT",
        help="Додати TEXT у секцію SECTION. Розділювач '::'. Можна повторювати."
    )
    parser.add_argument("project", choices=list(projects.keys()), help="Project name")
    parser.add_argument("what_done", help="What was done this session")
    parser.add_argument("next_step", help="Next step")
    parser.add_argument("context", help="Additional context")
    args = parser.parse_args()
    do_checkpoint(args, projects)


if __name__ == "__main__":
    main()
