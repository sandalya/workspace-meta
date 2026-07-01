---
project: meta
updated: 2026-07-01
---

# WARM — meta

## Three-tier memory — project structure

```yaml
last_touched: 2026-05-05
tags: [infrastructure, memory]
status: active
```

The project uses three files for context management:
- **HOT.md** — rewritten every session, current step and results (~60 lines).
- **WARM.md** — architecture, decisions, open questions (~400 lines, updated incrementally).
- **COLD.md** — append-only history, archives of completed phases.

Structure adopted 2026-04-23. The `chkp` script automates updates via Haiku (fallback Sonnet). Claude instances read HOT+WARM at session start (Rule Zero in MEMORY.md).

## Architectural migration 2026-04-23

```yaml
last_touched: 2026-04-23
tags: [architecture, migration, infrastructure]
status: active
```

**Change:** Kit is now dev-agent only. Meta-repo contains:
- `chkp` — checkpoint script for updating HOT/WARM/COLD
- `BACKLOG` — moved from root, single task list
- `notes/` — documentation and meditations
- `scripts/` — utility scripts
- `workspace/.env` — fallback API key from kit (masked to 4 chars)

HOT files for all 6 projects synced and updated. Duplicate .env files pending cleanup.

**Server (updated 2026-07-01):** Primary server migrated from Raspberry Pi 5 to **Beelink SER5** (hostname: `sashok-SER`, IP: `192.168.72.191`, Ubuntu 24.04 LTS) in June 2026. Pi5 is no longer prod server; openclaw-gateway crash loop was not recovered (disabled 2026-05-18).

## API keys — per-agent, intentional

```yaml
last_touched: 2026-05-19
tags: [architecture, api-keys, costs]
status: decided
```

**Each bot has its own `ANTHROPIC_API_KEY`** in its own `<project>/.env`. This is NOT tech debt — it's a deliberate decision for separate cost tracking per agent via Anthropic Console.

State as of 2026-06-30: 9 separate keys (abby-v2, ed, garcia, household_agent, insilver-v3, kit, sam, sam-v2, meta/digest). **Incident 2026-05-19:** sam key leaked in grep logs, disabled and rotated, new key written to sam/.env + meta/digest/.env. **Ed key:** rotated after investigating $11.79 charge (source not identified), Ed running on new key (closed 2026-06).

**`workspace/.env`** — fallback level with Kit key. Used only for `meta`/`kit` operations (`chkp`, admin scripts).

**RULE for future Claude sessions:** Do NOT suggest "consolidating .env into one file" — this would break cost tracking. If you see duplicates — it's a feature.

**Security pattern:** grep log files for API keys monthly — especially auto-generated files (AWS CLI output, curl verbose logs, debug traces).

## Components

```yaml
last_touched: 2026-07-01
tags: [infrastructure, chkp, caching]
status: active
```

- **chkp v3.5** — checkpoint script with WARM diff-mode (warm_ops parser) + BACKLOG_DONE.md redirect
  - `/home/sashok/.local/bin/chkp` Python shim, calls chkp.py v3.5
  - **Refactor (2026-07-01):** Removed second Haiku call (backlog-suggest) — CC now proposes strikes externally. --backlog-strike redirects to BACKLOG_DONE.md (append-only) instead of ~~strikethrough~~ in active BACKLOG. Eliminated PROMPT.md generation and clipboard operations. Added diff preview (A4 format) for user confirmation. CC behavioral rule documented in meta/rules/chkp.md.
  - **Model fix (2026-07-01):** Updated MODEL_SONNET from stale claude-sonnet-3.5 to claude-sonnet-4-6. Added --no-push flag for commit-only runs; push is default, dry-run only on explicit request.
  - **WARM diff-mode (2026-05-05):** New warm_ops system: parser + serializer for incremental WARM updates
    - 5 operations: touch (update last_touched), update_field (status/tags), add (new blocks), move_to_cold (archives), replace_body (content)
    - Serializer wraps operations back into YAML/markdown
    - Backward-compat: legacy WARM without field = default (status=active, tags=[], last_touched=None)
    - Economy: 16k→3.4k tokens (79%) on first prod checkpoint (insilver-v3, commit 4580c35)
    - Checkpoint completed in 15s instead of 5 minutes (legacy full-WARM)
    - Unit tests: 52/52 passed (18 warm_ops + 34 backlog integration)
    - First prod checkpoint (insilver-v3): JSON malformed on first run, self-corrected on retry. P3 need: explicit retry-loop.
    - Ready for scaling to other projects (garcia, abby-v2, ed, sam)
  - **BACKLOG_DONE.md redirect (2026-07-01):** --backlog-strike FLAG now appends to BACKLOG_DONE.md (per-project, append-only) instead of strikethrough in active BACKLOG. Prevents BACKLOG.md from accumulating struck items. Syntax: DATE: [REASON] FRAGMENT (full line from BACKLOG). Provides audit trail for retrospective analysis.
  - **Diff preview (A4 format, 2026-07-01):** Before git operations, shows unified diff (HOT/WARM diffs, optional COLD sample) in A4-formatted block for user confirmation. Reduces accidental commits.
  - **CC behavioral rule (2026-07-01):** Documented in meta/rules/chkp.md: CC proposes --backlog-strike flags externally (in claude.ai chat), chkp applies them. No second LLM call inside chkp. Decouples backlog management from HOT/WARM updates.
  - max_tokens=2000 sufficient for diff-mode HOT
  - xclip guard: DISPLAY check before call + stderr=DEVNULL for SSH without X11
  - PATH binary migration (2026-05-04): Python shim in ~/.local/bin instead of bash v1 script
  - Interactive y/n/e/s for accepting AI proposals on HOT/WARM
  - Per-project commits in meta for non-meta projects
  - Backlog read-only (for human): chkp only applies --backlog-strike flags from CLI, no auto-generation
  - PROMPT.md removed (2026-07-01): redundant with HOT/WARM checkpoint, no clipboard needed
  - chkp guard (2026-05-03): warn about dev-directory only when cwd == project + '-dev'

- **BACKLOG.md** — central task board for the entire workspace (read-only for chkp, human-edited)
  - Format: numbered items, status (DONE/TODO/BLOCKED), dependencies
  - 2026-07-01: Introduced BACKLOG_DONE.md append-only log for struck items, prevents active BACKLOG bloat
  - --backlog-strike FLAG now redirects to BACKLOG_DONE.md (audit trail) instead of strikethrough
  - Current sequence: items 1-N active, new items strike via chkp --backlog-strike → BACKLOG_DONE.md

- **BACKLOG_DONE.md** — append-only log of struck items (per-project)
  - Format: DATE: [REASON] FRAGMENT (full line from BACKLOG)
  - Purpose: audit trail, retrospective analysis, prevents BACKLOG.md from growing indefinitely
  - Introduced 2026-07-01 as replacement for ~~strikethrough~~ pattern

- **workspace/.env** — workspace-level keys, fallback for 9 projects
- **6 core projects** — each has HOT.md, WARM.md, COLD.md (local for architecture)
- **shared/ relocation (2026-05-15):** Moved shared/ from workspace root to meta-repo as sym-link. sys.path imports work. sam (11 imports), garcia (7 with inheritance), insilver-dev (1), meta/digest (2) active. Commit 5b41001.

## Key decisions

```yaml
last_touched: 2026-05-18
tags: [architecture, decision]
status: active
```

1. **Single BACKLOG** — eliminates repetition, central source of truth for tasks.
2. **Rule Zero** — at the start of each session, ask for HOT+WARM, don't rely on memory.
3. **Workspace-level .env** — eliminates key duplicates across projects, security + maintainability.
4. **Checkpoint via chkp** — standardized update procedure, automated via Claude (Haiku).
5. **Read-only backlog** — AI views BACKLOG, proposes observations, user edits manually. Minimizes chkp errors.
6. **PATH binary for chkp** — instead of bash v1 script in /bin or /usr/bin, v3.5 via Python shim in ~/.local/bin. Avoids version conflicts. Decision effective 2026-05-04.
7. **Prompt caching impractical for chkp** — WARM architecture is volatile, ROI zero without rework. Accept 30-90s delay as normal. Consider WARM diff-mode + COLD frozen split in Sprint B/C.
8. **Strikethrough in BACKLOG — dual enforcement** — rule described in CLAUDE.md (agent-docs) + BACKLOG.md header (STOP block) for reliability. LLM needs rule duplication at two points, otherwise weak signal when processing 40K files.
9. **Auto-backlog-suggest (2026-05-15)** — second Haiku call closes semantic drift: AI proposes closing items covered by context, UX block (y/n/edit/skip), prevents 11-day delays in strikes.

## Integrations

```yaml
last_touched: 2026-04-23
tags: [integration]
status: pending
```

- **kit** ↔ **meta**: Kit provides dev-advance, meta — memory management and context.
- **9 projects** → **meta**: Central memory for all, local WARM/COLD for specifics.
- **workspace** → **meta**: Single .env, BACKLOG, scripts.

## Open questions

```yaml
last_touched: 2026-05-15
tags: [open-questions]
status: active
```

- Will suggest_backlog_strikes() be effective for 90% of use-cases, or do we need more complex semantic heuristics?
- Does household_agent need sudo restart, or is auto-restart via systemd sufficient after token rotation?
- What regressions might arise from 4 chkp robustness fixes (multi-match context, whitespace strip) on live data?
- Should all 4 bots (ed, garcia, insilver-v3, sam) have the same httpx suppression pattern as abby-v2/household_agent, or audit each individually?
- BACKLOG rotation policy for abby images (759M, 1315 files) + sam audio (827M, 26 mp3) — when to keep vs. delete?
- Does BACKLOG need a hygiene pass (bi-weekly) for removing obsolete items, or is ad-hoc audit during smoke test sufficient?

## Workspace structure: post-cleanup polyrepo (2026-04-29)

```yaml
last_touched: 2026-05-04
tags: [architecture, structure, git]
status: active
```

After security cleanup 2026-04-29, workspace structure:

- **Root `~/.openclaw/workspace/`** — NOT a git repo. Only symlinks `BACKLOG.md` → `meta/BACKLOG.md`, `CLAUDE.md` → `meta/CLAUDE.md`.
- **8 separate GitHub repos** (one per bot, abby-v1 deleted 2026-05-04): abby-v2, ed, garcia, household_agent_v1, insilver-v3, openclaw-kit, sam, workspace-meta. Insilver-v2 deleted from GitHub (legacy). **abby-v1 deleted from GitHub 2026-05-04, local folder pending deletion.**
- **meta-repo** — centralized infrastructure: `agent-docs/` (12 root-level md), `BACKLOG.md`, `chkp/` (Python v3.4), `legacy/chkp_bash_v1/` (reference, pending deletion after PATH check), `backup/` (scripts only, runtime archives live in workspace/backup/), `systemd-services-backup/`.
- **shared/** — remains in workspace as plain folder, outside any git tracking. Not imported by bots. Fate unresolved (BACKLOG: shared/ refactor ~2026-05-06).
- **Runtime files in root** (not tracked): `memory/`, `.checkpoint_tracker.json`, `.openclaw/workspace-state.json`, `.env`, `health_monitor.log`.

**Why NOT submodules with .gitmodules:** audit found root repo had 8 dangling gitlinks without `.gitmodules` — corrupted state. Instead of fixing, chose to fully delete root .git: each sub-project is self-contained, meta holds workspace-level content. Avoids submodule sync issues.

**Force-push contract:** for prod bots, history cleanup (filter-repo) is done only when:
1. All compromised secrets revoked (TG @BotFather, PAT GitHub).
2. Local backup exists.
3. Bot stopped via systemctl during filter-repo (so it doesn't write to files being deleted).
4. Stale branches on GitHub checked separately (filter-repo doesn't touch them).

## Security cleanup ritual — how to do it next time (2026-04-29)

```yaml
last_touched: 2026-04-29
tags: [security, git, runbook]
status: active
```

**Pre-flight (before filter-repo on any repo):**

1. `pip install git-filter-repo --break-system-packages` (once).
2. Backup entire workspace: `tar -czf ~/workspace-backup-$(date +%Y%m%d-%H%M).tar.gz -C ~/.openclaw workspace --exclude='*/venv'` (~6-7G).
3. `git status` — clean or stash before filter-repo (filter-repo does `git reset --hard` after, dirty edits disappear).
4. `systemctl stop <bot>.service` — stop bot during operation so it doesn't write to files being modified.
5. Check secrets in history: `git log --all -p | grep -E '[0-9]{8,12}:[A-Za-z0-9_-]{30,}'` (TG tokens), `... | grep -E 'sk-ant-[A-Za-z0-9_-]{20,}'` (Anthropic).
6. **If tokens found — revoke them BEFORE filter-repo** (still-valid tokens in clone caches can be pushed back by an attacker).

**Filter-repo pattern:**

```bash
git filter-repo --force --dry-run \
  --path FILE1 --path FILE2 \
  --path-glob 'data/*.bak*' \
  --replace-text /tmp/replace.txt \
  --invert-paths
```

`/tmp/replace.txt` — format `LITERAL_TOKEN==>***REVOKED***`, one per line. Default literal match. `--force` flag needed because filter-repo doesn't consider workspace a "fresh clone".

**Post:**

1. `git remote add origin <URL>` — filter-repo removes remote, restore manually.
2. Check dry-run before real (`fast-export.original` vs `fast-export.filtered`).
3. `git push --force origin main` — rewrites history on GitHub.
4. Check other branches: `git fetch origin && git ls-remote --heads origin` — if there are stale branches with PII, delete: `git push origin --delete BRANCH`.
5. Update `.gitignore` (filter-repo may have reset edits) → commit + push.
6. Restart bot: `systemctl start <bot>.service`.

## Remote dev infrastructure (2026-04-30, updated 2026-06-30)

```yaml
last_touched: 2026-07-01
tags: [infrastructure, remote-dev, tmux]
status: active
```

**Setup for working on the road from Android phone:**

1. **Tailscale** — VPN tunnel Beelink SER5 ↔ Android phone. Private network, all services accessible via IP `192.168.72.191` on local Tailscale network.
2. **Termius** — SSH client for Android. Connected to `sashok-SER`, automatic reconnects on connection drops.
3. **tmux** — session manager on Beelink SER5. Survives connection drops, allows detach/reattach from different clients.
   - Alias: `w` = `tmux new -A -s work` (new session or enter existing).
   - Basic commands: `Ctrl+B D` (detach), `tmux attach -t work` (reattach), `tmux ls` (list sessions).

**Workflow:** 1) Termius → SSH to sashok-SER (Beelink, 192.168.72.191). 2) `w` = enter work tmux. 3) On disconnect: Ctrl+B D detach. 4) On reconnect: `tmux attach -t work` → return to same place.

**Server migration (June 2026):** Pi5 (Raspberry Pi 5) was primary until June 2026; now Beelink SER5 is primary. Tailscale setup unchanged. SSH key `~/.ssh/pi5_backup` no longer applicable. Backup strategy redesign pending.

## Sam NBLM tech debt — series of subtasks (backlog)

```yaml
last_touched: 2026-05-16
tags: [sam, nblm, tech-debt, p2]
status: in-progress
```

**Series of 5 subtasks from Sam NBLM backlog (reorganized 2026-05-04):**

**Status: DONE (previous cycles)**
1. ~~**Intervention 0 — sam.service bootstrap** (completed in security cleanup cycle)~~
2. ~~**Intervention -1 — nblm backend review** (completed in prep for P2)~~
3. ~~**Intervention -2 — dependency map** (completed in security cleanup)~~
4. ~~**Intervention 1 — dangling UUID detection** (DONE 2026-05-15)~~: UUIDs 0daaf506, 2d0285dd pointing to non-existent notebooks — issue resolved. get_or_create_notebook in sam/core/content_gen/backends/nblm.py calls `probe source list -n --json` before reuse, invalidates `nblm_notebook_id` if RPC fail/null, fallthrough to create. 4/4 TestNotebookProbe tests pass. Unblocks rag_retrieval-1.

**Status: TODO (queue active, after Inter 1 verification)**
5. **Intervention 2 — content_gen pipeline log aggregation** (design pending):
   file: sam/core/content_gen/
   problem: logs scattered across 3+ files (generator.py, pipeline.py, backends/*.py), hard to trace sequence
   solution: central LogAggregator class, per-request ID, operation tree in content_gen.log
   verification: `sam.service restart`, manual test with verbose logging

6. **Intervention 3 — error bubble-up chain** (design pending, after Inter 2):
   question: which NBLM RPC errors should retry, which should fail-fast
   solution: design retry logic per error type (connection timeout → retry; permission denied → fail; invalid notebook → invalidate UUID + recreate)

7. **Intervention 4** — (pending definition after Inter 2-3 complete)

8. **Intervention 5** — (pending definition)

**Context:** chkp v3.5 + WARM diff-mode + suggest_backlog_strikes fully stable. Sam NBLM Inter 1 verified live. Ready for Inter 2 design (log aggregation) next session or detailed Error Handling audit in current session depending on cycle energy.

## Memory auto-fetch for public repos (2026-05-03)

```yaml
last_touched: 2026-05-03
tags: [memory, infrastructure, web-integration]
status: active
```

**Hybrid memory read mode:**

- **Public repos** (sam, ed, workspace-meta) — memory rule #21 activated: HOT.md read via `web_fetch` on raw.githubusercontent.com/openclaw-ai/<repo>/main/HOT.md. Verified accessible without auth.
- **Private repos** (insilver-v3, abby-v2, garcia, household_agent) — remain on manual read: `cat HOT.md WARM.md` as instruction in claude.ai at session start.
- **kit** — not yet migrated to new HOT/WARM/COLD memory, stays on legacy instructions pending review.

**Reasons for hybridization:**
- Public repos: source files, no auth barriers, stable raw.githubusercontent.com access.
- Private repos: can't fetch publicly without PAT, manual reading is safer and controlled.
- kit as agent: special role (dev-integration), migration planned separately.

**Verification:**
- sam HOT.md: accessible on raw.github
- ed HOT.md: accessible on raw.github
- workspace-meta HOT.md: accessible on raw.github
- Private repos: manual cat instruction documented in MEMORY.md.

## insilver-v3-dev pre-push patterns (2026-05-04)

```yaml
last_touched: 2026-05-04
tags: [insilver, git, pre-push, security]
status: active
```

**Pre-push hook configs:**
- **Telegram client-ID format:** `[0-9]{9,}_.*` (minimum 9 digits, then underscore + anything). Checks to prevent accidentally committing TG client IDs.
- **Photo paths (whitelist):** `data/photos/incoming/` and `data/photos/clients/` allowed (client lists, working data). `data/photos/static/` explicitly allowed (public assets).
- **Previously:** Blanket `.jpg/.jpeg/.png` ban. **Now:** Removed, replaced with specific paths — fewer false positives, higher detection accuracy.
- **Committed:** In insilver-v3-dev/.git/hooks/pre-push.

**Reasons for specificity:** Client photos (189793675_*.jpg) were accidentally left in insilver-v3 history years ago, security cleanup 2026-04-29 removed them. Now hook prevents recurrence.

## WARM diff-mode v3.5 (warm_ops integration)

```yaml
last_touched: 2026-07-01
tags: [infrastructure, warm-ops, optimization, p1]
status: live
```

WARM diff-mode via warm_ops parser — fully operational in production since 2026-05-05. Instead of rewriting entire WARM each session, chkp v3.5 generates compact JSON with operations (warm_ops). **Results:** 79% economy (16k→3.4k tokens), speedup 5min→15s on checkpoint (insilver-v3, commit 4580c35). **Architecture:** meta/chkp/warm_ops.py parser (JSON → operations) + serializer (operations → YAML/markdown). 5 operations: touch, update_field, add, move_to_cold, replace_body. Backward-compat with legacy WARM (without field = default status=active, tags=[], last_touched=None). **Unit testing:** 16/16 PASS. **Scaling status (2026-05-16):** garcia, abby-v2, ed, sam local dry-run OK, ready for checkpoints. Expected 50%+ token economy per project. **P3 need:** Explicit retry-loop on JSONDecodeError (max retries=2, exponential backoff). **Prompt caching (closed as P2):** WARM diff-mode +79% economy, but minimum 1024 tokens for cacheable block is insufficient. ROI zero without major architectural changes. Beta header kept for Sprint B/C experiments.

## chkp v3.5 refactor — BACKLOG_DONE redirect + diff preview (2026-07-01)

```yaml
last_touched: 2026-07-01
tags: [chkp, backlog, workflow, optimization, p1]
status: ready-for-live-test
```

Refactored chkp v3.5 to align with CC workflow shift. **Motivation:** CC now proposes --backlog-strike flags externally (in claude.ai chat before chkp invocation), eliminating need for second Haiku call inside chkp. Reduces token spend, decouples backlog management from HOT/WARM updates.

**Changes:**
1. **Removed suggest_backlog_strikes()** — second Haiku call eliminated. CC proposes strikes in chat; user passes --backlog-strike FLAG to chkp.
2. **BACKLOG_DONE.md redirect** — --backlog-strike now appends to per-project BACKLOG_DONE.md (append-only log) instead of ~~strikethrough~~ in active BACKLOG. Format: `DATE: [REASON] FRAGMENT`. Provides audit trail for retrospective analysis.
3. **Eliminated PROMPT.md generation** — redundant with HOT/WARM checkpoint, clipboard operations removed. chkp now pure HOT/WARM/COLD updater + BACKLOG_DONE appender.
4. **Diff preview (A4 format)** — before git operations, shows unified diff (HOT/WARM diffs, optional COLD sample) in A4-formatted block. User y/n confirmation reduces accidental commits.
5. **CC behavioral rule documented** — meta/rules/chkp.md formalizes workflow: CC proposes strikes externally, chkp applies them. Single source of truth for chkp behavior.

**Unit testing:** 52/52 pytest PASS (18 warm_ops + 34 backlog integration tests). Backward compat verified (legacy WARM blocks work unchanged). Live validation pending on insilver-v3-dev or sam.

**Expected outcome:** Simpler, faster chkp (no second API call), clearer workflow (CC ↔ user ↔ chkp chain), audit-trail for BACKLOG strikes via BACKLOG_DONE.md append-only log.

## chkp SYSTEM_PROMPT patch — two-layer no-hallucination mechanics (2026-05-05)

```yaml
last_touched: 2026-05-05
tags: [chkp, system-prompt, evals, p1]
status: active
```

**Problem:** Haiku in chkp generates HOT.md, but ## Now hallucinates (copy-paste from previous HOT or WARM instead of WHAT WAS DONE THIS SESSION).

**Solution (two-layer):**

1. **SYSTEM_PROMPT rule 1** — explicit canonical sources per section:
   - ## Now: ONLY from input WHAT WAS DONE THIS SESSION (1–3 sentences, CRITICAL)
   - ## Last done: from WHAT WAS DONE (bullet list, expanding Now)
   - ## Next: from input NEXT STEP
   - ## Reminders: keep from previous if relevant
   - Other sources (previous HOT, WARM) = historical context, not sources for rewriting

2. **_redact_now_for_context() function** — mechanical enforcement:
   - Removes `## Now` and `## Last done` from input HOT before API call
   - Prevents Haiku from "reading" old context from input
   - Keeps `## Next`, `## Blockers`, `## Active branches`, `## Open questions`, `## Reminders`

**Validation (2026-05-05):**
- 19/19 pytest PASS:
  - 3 no_hallucination fixtures (fixtures/2026-05-05_meta_chkp_evals.py)
  - 16 warm_ops operations (touch, update_field, add, move_to_cold, replace_body)
- Local check: `cd meta && pytest chkp/tests/ -v` → PASS

**Production status:**
- Needs verification on real checkpoints (insilver-v3, sam, garcia) next 2-3 sessions
- If OK → scalability to all 6 projects

## ~/.claude/settings.json — acceptEdits integration (2026-05-05)

```yaml
last_touched: 2026-05-05
tags: [infrastructure, claude-ai, automation, permissions]
status: active
```

**Setup complete (2026-05-05):**
- ~/.claude/settings.json contains allow/deny rules for automated mode.
- allow: tasks from backlog (BACKLOG.md patterns), commit messages, code review.
- deny: prod insilver-v3 files, .env, push to main, sudo commands, journalctl without grep, rm -rf on critical paths.
- alias cld = claude --permission-mode acceptEdits — sits on a 15-minute pause without manual confirmation.

**Status:** Single settings file without local overrides. Verified. Ready for test on real task (sam or insilver-v3-dev) to measure prompt accumulation.

## Off-device backup chain — DR infrastructure (2026-05-06)

```yaml
last_touched: 2026-07-01
tags: [infrastructure, backup, disaster-recovery, automation]
status: outdated
```

⚠️ **This scheme was for Pi5 and is outdated after migration to Beelink SER5 (June 2026).** Details in COLD.md (2026-06-30). Needs redesign for new Beelink SER5 infrastructure.

Old scheme (Pi5): PC (Windows 10, H:\pi_backups) pulls daily via Task Scheduler, SSH key `~/.ssh/pi5_backup`, 14-day retention. backup/ git repo: `sandalya/pi5-backup`. system-snapshot (systemd units, crontab, dpkg, pip) — verified 2026-05-15.

**Next:** Design new backup strategy for Beelink SER5 (192.168.72.191, Ubuntu 24.04 LTS). Options: (1) integrate into existing H:\pi_backups with Tailscale VPN pull, (2) local USB backup + systemd timer, (3) cloud S3 backup, (4) other LAN NAS integration.

## Logging security — httpx token leak suppression (2026-05-06)

```yaml
last_touched: 2026-05-06
tags: [security, logging, httpx, telegram]
status: active
```

**Incident:** Telegram bot token leaked into journalctl via httpx library INFO logs (household_agent-v1). Token included in URL query parameters logged by httpx before request execution.

**Token rotation:** Rotated via BotFather on 2026-05-06, token revoked.

**Root cause:** httpx default logging level (INFO) logs full request URLs including auth tokens. Occurs across 6 projects: abby-v2, ed, garcia, household_agent, insilver-v3, sam.

**Action items:**
1. Add to all bot configs: `logging.getLogger('httpx').setLevel(logging.WARNING)` (suppress INFO/DEBUG)
2. Audit all .log files in workspace for leaked tokens (journalctl rotate retention)
3. Verify requirements.txt pinning in each project includes httpx version (for reproducibility)

**Next:** Suppress httpx INFO across all 6 bots, scan historical journalctl for similar leaks, document in MEMORY.md rule #X (logging security).

## Language — English output for chkp (2026-07-01)

```yaml
last_touched: 2026-07-01
tags: [infrastructure, chkp, language, internationalization]
status: active
```

Decision: All new chkp output (HOT.md, WARM.md, PROMPT.md) generated in English. COLD.md archive remains append-only in original Ukrainian (historical record). Rationale: developer interface language (English) separate from model thinking language (Ukrainian context preserved in COLD). Implementation: chkp.py SYSTEM_PROMPT rules 4+6 updated to enforce English output, verified on meta and drone-recon. Future sessions auto-generate English without manual intervention.

## Token tracker — read-only audit (2026-05-15)

```yaml
last_touched: 2026-05-15
tags: [infrastructure, cost-tracking, token-logging, audit]
status: active
```

**Audit result:** shared/token_log.jsonl functions as read-only log with 74 entries from 2026-04-13, format clean (ts/agent/in/out/cost). Write-side connected only in digest + garcia. sam/insilver-v3/abby-v2/ed/meggy have dead /stats UI with 0 records for a month.

**Status:** Non-critical. Anthropic Console covers total spend tracking. Per-bot fine-grained accounting — separate backlog task if needed in future.

**Conditions:** token_log.jsonl stable, continue use for digest/garcia, remaining bots don't need activation.

## morning_digest systemd timer — Telegram BACKLOG summary (2026-05-15)

```yaml
last_touched: 2026-05-15
tags: [telegram, automation, backlog-digest, sam-bot]
status: active
```

Automated daily digest of BACKLOG structure via Telegram. Runs at 09:00 via systemd timer, sent to OWNER_CHAT_ID.

**Components:**
- **meta/digest/morning_digest.py** — BACKLOG.md parser: inline (Pn) markers (P1-P4), closed sections (~~strikethrough~~), uncategorized items (13 items)
- **Haiku 4.5 synthesis** — takes BACKLOG structure, generates summary preserving original language, clean response without explanations
- **HTML parse_mode** — Telegram messages: line breaks, monospace blocks for bullet lists
- **systemd timer** — meta/digest.timer (09:00 daily), meta/digest.service (Python runner)

**Config (meta/digest/.env):**
- SAM_BOT_TOKEN (Telegram bot from @BotFather, reused from sam)
- OWNER_CHAT_ID (target chat for digest, read-only)
- ANTHROPIC_API_KEY (reused from sam/.env for Haiku calls)

**Status (2026-05-15):**
- Parser: 11/11 unit tests PASS
- Cost: ~0.0026 USD per run (~0.08 USD/month on automation)
- First run result: p1=0, p23=3 uncategorized=13, done=0 (BACKLOG structure documented)
- System timer: ready for 09:00 trigger tomorrow

## Anthropic SDK cost isolation — shared/agent_base.py fix (2026-05-14)

```yaml
last_touched: 2026-05-14
tags: [api-keys, costs, shared-library, anthropic-sdk]
status: fixed
```

**Problem:** shared/agent_base.py line 20 — `client = anthropic.Anthropic(api_key=os.environ['ANTHROPIC_API_KEY'])` without load_dotenv(). Anthropic SDK's find_dotenv() automatically picked up workspace/.env with kit3 key, instead of project .env files. This caused charges on kit3 key for abby-v2, household_agent, ed-bot.

**Diagnosis (2026-05-14):**
- ed-daily.timer: stopped, judge used Haiku (charges on kit3 key)
- abby-v2, household_agent: find_dotenv() picked up workspace/.env instead of project
- sam-rss, insilver-v3-error-monitor: verified, don't call Anthropic SDK

**Solution:**
1. Added `EnvironmentFile=<path>/.env` to systemd units abby-v2.service and household_agent.service
2. ed-daily.timer: verified, timer renewed
3. shared/agent_base.py: current version left as-is (SDK find_dotenv() controlled via EnvironmentFile)

**Consequence:** Each project now uses its own key, cost tracking is separate per agent again.

## chkp suggest_backlog_strikes — semantic backlog drift fix

```yaml
last_touched: 2026-05-18
tags: [chkp, backlog, automation, design, p1]
status: implemented
```

**Problem:** chkp v3.5 mechanical validations (validate_backlog_flags fail-loud, multi-match context-aware replace) closed syntactic bugs. Semantic issue remained: AI in claude.ai chat doesn't cross-reference 'what was done' with active BACKLOG items, so --backlog-strike simply isn't passed. Empirical evidence: 0674dd4 (household_agent filter-repo 240M→612K, 2026-04-05) — checkpoint exists but no strike flag, item hung for 11 days as incomplete.

**Root cause:** Haiku generates HOT.md (## Now/Last done/Next), but doesn't know which BACKLOG items should be closed. User when accepting results only copy-pastes into --backlog-strike, often forgets or copies incorrectly.

**Solution (implemented 2026-05-15):**
1. **suggest_backlog_strikes()** — after Haiku HOT.md generation, second Haiku call takes ## Now + ## Last done, reads BACKLOG.md, generates list of proposed strikes (JSON: [{"line": 3, "text": "...", "action": "strike"}])
2. **UX block y/n/edit/skip** — interactive mode: user y (apply all) / n (skip all) / e (edit manually) / s (select subset), timeout 30s
3. **--no-backlog-suggest flag** — opt-out for automation scripts
4. **Validation:** verifies proposed strikes on true matches in BACKLOG (no hallucination)

**Status (2026-05-15):** Feature implemented, smoke test ready on real session. Goal 95%+ accuracy in first week. Scale to 6 projects after verification on insilver-v3 or sam.

## Prompt caching reuse via SYSTEM_PROMPT share (2026-05-18)

```yaml
last_touched: 2026-05-19
tags: [chkp, optimization, caching, prompt-engineering]
status: live
```

Prompt caching optimization for suggest_backlog_strikes via SYSTEM_PROMPT reuse. **Problem:** Two Haiku calls (main HOT + suggest) used separate SYSTEM_PROMPT blocks, cache miss every time. **Solution (2026-05-18):** Moved _SUGGEST_SYSTEM config to _SUGGEST_USER_PREFIX, now both calls share one cacheable SYSTEM_PROMPT (1612 tokens). **Expected:** cache_creation_input_tokens on first call, cache_read_input_tokens > 0 on second → ~10-20% token savings on suggest_backlog_strikes block. **Implementation:** meta/chkp/chkp.py line 1400 (call_anthropic helper), test_prompt_caching.py added 2 integration cases. **Status (2026-05-18):** 7 unit + 2 integration = 64/64 PASS locally. Live test planned next session (real chkp run → check response_metadata).

## API key audit — sam rotation 2026-05-19

```yaml
last_touched: 2026-05-19
tags: [api-keys, security, incident, audit]
status: active
```

**Incident:** sam key exposed in grep logs. Disabled via Anthropic Console. **Action:** rotated — new key written to sam/.env and meta/digest/.env. sam.service restarted, functioning. **Ed key:** rotated after investigation (source of $11.79 charge 2026-05-18 not identified, Ed on new key — closed 2026-06). **Lesson:** grep log files regularly for API keys (especially AWS CLI output, curl verbose logs).

## CC behavioral rules — chkp workflow coordination (2026-07-01)

```yaml
last_touched: 2026-07-01
tags: [chkp, workflow, cc-rules, coordination]
status: active
```

Documented CC behavioral rules for coordinated chkp workflow. **File:** meta/rules/chkp.md (symlinked from CLAUDE.md Behavior section).

**Rule 1: External backlog proposals.** CC proposes --backlog-strike flags in claude.ai chat *before* chkp invocation. User copies proposed flags into `chkp PROJECT "what done" "next" --backlog-strike FRAGMENT`. No second Haiku call inside chkp.

**Rule 2: Strike validation.** CC validates proposed strikes against BACKLOG.md content (no hallucinated flags). User confirms final strike list before passing to chkp.

**Rule 3: Diff preview acceptance.** chkp shows unified diff (A4 format) of HOT/WARM changes. User y/n confirmation before git add+commit. Prevents accidental overwrites.

**Rationale:** Decouples backlog management (semantic, human+LLM) from HOT/WARM updates (mechanical, token-efficient). Reduces API spend, clarifies workflow, audit-trail via BACKLOG_DONE.md.
