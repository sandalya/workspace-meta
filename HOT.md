---
project: meta
updated: 2026-07-11
---

# HOT — meta

## Now
Ran /doctor health check on workspace: no broken files/extensions/stale installs. Set defaultMode=auto in ~/.claude/settings.json (was null). Discovered workspace/CLAUDE.md symlink to meta/CLAUDE.md causes CC rules/chkp rules/backlog rules to miss when launched from meta/.

## Last done
- Executed /doctor skill (health check clean)
- Updated ~/.claude/settings.json: permissions.defaultMode=auto (was null)
- Identified symlink gap: CC from meta/ misses .claude/rules/* files
- Verified no backlog items struck this session

## Next
Normal project work. BACKLOG.md at 50K chars (warning threshold 40K) — user deferred hygiene decision.

## Blockers
None.

## Active branches
- chkp v3.5 refactor: diff preview + BACKLOG_DONE.md redirect (ready for live validation)
- WARM diff-mode (warm_ops): live production, 79% token economy
- httpx logging suppression: 6/6 bots patched
- Sam NBLM Intervention 1: DONE (UUID detection), Intervention 2 queued
- morning_digest systemd timer: live at 09:00 daily
- Infrastructure migration: Pi5→Beelink SER5 complete, meta cleanup done, 5 projects pending
- Model ID sweep: meta done, 5 projects queued

## Open questions
- Will BACKLOG_DONE.md append-only log scale well for 6 projects over months/years (no purge strategy yet)?
- Should diff preview (A4) include COLD.md or only HOT/WARM diffs to keep preview compact?
- Backup redesign for Beelink SER5: systemd timer + USB, cloud S3, or intra-LAN NAS pull?
- BACKLOG.md hygiene: bi-weekly audit, age-sort inactive tasks, or link items to commits?

## Reminders
- **Server:** Beelink SER5 (192.168.72.191, sashok-SER, Ubuntu 24.04 LTS) — primary; Pi5 deprecated June 2026
- **Language:** English for HOT/WARM/PROMPT; COLD.md archive remains Ukrainian
- **API keys:** 9 separate keys per bot — do NOT consolidate (cost tracking)
- **chkp workflow shift:** CC proposes backlog strikes externally (no second LLM call needed inside chkp)
- **BACKLOG_DONE.md:** new append-only archive for struck items, prevents BACKLOG.md bloat
- **Model IDs:** Sonnet 5 is latest; audit shared/ + all projects for stale references
- **CC launch location:** Always from workspace/ not meta/ to load .claude/rules/ files correctly