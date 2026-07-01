---
project: meta
updated: 2026-07-02
---

# HOT — meta

## Now
Updated MODEL_SONNET to claude-sonnet-5 (was stale claude-sonnet-4-6) in chkp.py.

## Last done
- Fixed MODEL_SONNET reference in meta/chkp/chkp.py from claude-sonnet-4-6 to claude-sonnet-5
- Validated model availability in Anthropic SDK
- Verified no other stale model references in codebase

## Next
Continue with other work or validate chkp v3.5 refactor on live project (insilver-v3-dev or sam) to test --backlog-strike → BACKLOG_DONE.md redirect, diff preview A4, and multi-project git operations.

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