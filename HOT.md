---
project: meta
updated: 2026-07-01
---

# HOT — meta

## Now

Refactored chkp v3.5: removed second Haiku call for backlog-suggest, redirected --backlog-strike to BACKLOG_DONE.md instead of strikethrough, eliminated PROMPT.md and clipboard operations, added diff preview (A4 format), documented CC behavioral rule in meta/rules/chkp.md. All 52/52 pytest passing.

## Last done

- Removed suggest_backlog_strikes() second Haiku call (CC now proposes strikes before chkp invocation)
- Changed --backlog-strike behavior: items moved to BACKLOG_DONE.md (append-only log) instead of ~~strikethrough~~ in active BACKLOG
- Removed PROMPT.md generation and clipboard copy (reduced scope, chkp now pure HOT/WARM/COLD updater)
- Added diff preview (A4 format) for user confirmation before git operations
- Added CC behavioral rule documentation (meta/rules/chkp.md) for workflow coordination
- Unit test suite: 52/52 green (18 warm_ops + 34 backlog integration tests)
- Verified backward compatibility with legacy WARM blocks (no field = default status/tags)

## Next

Real chkp run on a live project (not dry-run) to validate full end-to-end flow: propose insilver-v3-dev or sam checkpoint to test --backlog-strike → BACKLOG_DONE.md redirect, diff preview A4, and multi-project git operations.

## Blockers

None.

## Active branches

- chkp v3.5 refactor: diff preview + BACKLOG_DONE.md redirect (ready for live validation)
- WARM diff-mode (warm_ops): live production, 79% token economy
- httpx logging suppression: 6/6 bots patched
- Sam NBLM Intervention 1: DONE (UUID detection), Intervention 2 queued
- morning_digest systemd timer: live at 09:00 daily
- Infrastructure migration: Pi5→Beelink SER5 complete, meta cleanup done, 5 projects pending

## Open questions

- Will BACKLOG_DONE.md append-only log scale well for 6 projects over months/years (no purge strategy yet)?
- Should diff preview (A4) include COLD.md or only HOT/WARM diffs to keep preview compact?
- Backup redesign for Beelink SER5: systemd timer + USB, cloud S3, or intra-LAN NAS pull?

## Reminders

- **Server:** Beelink SER5 (192.168.72.191, sashok-SER, Ubuntu 24.04 LTS) — primary; Pi5 deprecated June 2026
- **Language:** English for HOT/WARM/PROMPT; COLD.md archive remains Ukrainian
- **API keys:** 9 separate keys per bot — do NOT consolidate (cost tracking)
- **chkp workflow shift:** CC proposes backlog strikes externally (no second LLM call needed inside chkp)
- **BACKLOG_DONE.md:** new append-only archive for struck items, prevents BACKLOG.md bloat