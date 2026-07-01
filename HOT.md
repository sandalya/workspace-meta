---
project: meta
updated: 2026-07-01
---

# HOT — meta

## Now

Fixed stale MODEL_SONNET (was claude-sonnet-3.5, updated to claude-sonnet-4-6) and added --no-push flag for commit-only test runs; chkp.md rules clarified that push is default behavior, dry-run only on explicit request.

## Last done

- Corrected MODEL_SONNET to claude-sonnet-4-6 in meta/chkp/chkp.py
- Added --no-push CLI flag to prevent git operations during workflow validation
- Updated meta/rules/chkp.md: documented push-by-default pattern and --no-push override
- Post-refactor validation on meta checkpoint

## Next

Continue with real chkp run on a live project (not dry-run) to validate full end-to-end flow: propose insilver-v3-dev or sam checkpoint to test --backlog-strike → BACKLOG_DONE.md redirect, diff preview A4, and multi-project git operations.

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