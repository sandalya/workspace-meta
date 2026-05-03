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
import json
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

WORKSPACE = os.path.expanduser("~/.openclaw/workspace")
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


def call_anthropic(api_key, model, system_prompt, user_prompt, max_tokens=16000, timeout=300):
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
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
- **WARM.md** — Architecture & active knowledge. Each block has a YAML header with `last_touched`, `tags`, `status`. Update `last_touched` on blocks affected by this session. Add new blocks for new concepts. If a block is no longer relevant (status: done + not touched in 2+ weeks), move it to COLD.
- **COLD.md** — Archive. Append-only. Each entry: `## YYYY-MM-DD: Title`, YAML with `archived_at`, `reason`, `tags`, description 3-10 lines.

## Output format

Respond with EXACTLY this JSON structure (no markdown fences, no preamble):
{
  "hot": "<full content of HOT.md>",
  "warm": "<full content of WARM.md>",
  "cold_append": "<new entries to APPEND to COLD.md, or empty string if nothing to archive>",
  "prompt": "<next-session prompt in Ukrainian for pasting into Claude.ai>"
}

## Rules

1. HOT.md: Always rewrite completely. "Last done" = summary of this session. "Next" = from user input. Keep Reminders section from previous HOT if still relevant.
2. WARM.md: Preserve ALL existing blocks. Only update `last_touched` date on blocks that were affected. Add new blocks if this session introduced new architecture/concepts. Move blocks to cold_append ONLY if they are status:done AND clearly obsolete.
3. COLD.md: cold_append is APPENDED to existing file. Use append format: `---\\n\\n## YYYY-MM-DD: Title\\n...`. Empty string if nothing to archive.
4. Prompt: Write in Ukrainian. Include: project name, current state summary (2-3 sentences), what to do next, any blockers. Format it as a message the developer will paste into a new Claude.ai session. Start with "Проект: <n>". Include instruction to share HOT.md + WARM.md. Keep it under 15 lines.
5. Preserve the YAML frontmatter (---\\nproject: ...\\nupdated: ...\\n---) at the top of HOT.md and WARM.md. Update the `updated` date to today.
6. Keep all content in the same language as the original files (Ukrainian or English, match what's there).
7. Do NOT invent information. Only use what's provided in the current files and session description.
"""


def build_user_prompt(project, what_done, next_step, context, hot, warm, cold, memory, today):
    parts = [
        f"Project: {project}",
        f"Date: {today}",
        f"Session summary:",
        f"  What done: {what_done}",
        f"  Next step: {next_step}",
        f"  Context: {context}",
        "",
        "=== Current HOT.md ===",
        hot or "(empty — first checkpoint, create from scratch)",
        "",
        "=== Current WARM.md ===",
        warm or "(empty — first checkpoint, create from scratch)",
        "",
        "=== Current COLD.md ===",
        cold or "(empty — first checkpoint)",
        "",
    ]
    if memory:
        parts.extend(["=== MEMORY.md (read-only, do not modify) ===", memory, ""])
    return "\n".join(parts)


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
    cwd = os.getcwd()
    if cwd.endswith("-dev") and not project_dir.endswith("-dev"):
        print(f"\n\u26a0\ufe0f  WARNING: запущено з {cwd}", file=sys.stderr)
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
    user_prompt = build_user_prompt(
        args.project, args.what_done, args.next_step, args.context,
        hot, warm, cold, memory, today,
    )
    response_text = call_anthropic(api_key, model, SYSTEM_PROMPT, user_prompt)
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
            response_text = call_anthropic(api_key, MODEL_SONNET, SYSTEM_PROMPT, user_prompt)
            try:
                text = response_text.strip()
                if text.startswith("```"):
                    lines = text.split("\n")
                    lines = [l for l in lines if not l.strip().startswith("```")]
                    text = "\n".join(lines)
                result = json.loads(text)
            except json.JSONDecodeError:
                die(f"Sonnet fallback also failed:\n{response_text[:500]}")
    for field in ["hot", "warm", "prompt"]:
        if field not in result or not result[field].strip():
            die(f"AI response missing or empty field: {field}")
    print("\n   📁 Writing tier files...")
    write_file(os.path.join(project_dir, "HOT.md"), result["hot"])
    print(f"      HOT.md  ✅ ({len(result['hot'].splitlines())} lines)")
    write_file(os.path.join(project_dir, "WARM.md"), result["warm"])
    print(f"      WARM.md ✅ ({len(result['warm'].splitlines())} lines)")
    cold_append = result.get("cold_append", "").strip()
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
    prompt = result["prompt"]
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
