---
project: meta
updated: 2026-07-02
---

# HOT — meta

## Now
Updated MODEL_SONNET in shared/agent_base.py and token_logger.py to claude-sonnet-5 (was claude-sonnet-4-20250514).

## Last done
- Updated MODEL_SONNET references from claude-sonnet-4-20250514 to claude-sonnet-5
- Swept shared/ library for stale model IDs
- No backward compatibility issues found

## Next
Continue workspace-wide model ID sweep to remaining 5 projects (insilver-v3, sam, garcia, ed, household_agent).

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

## Reminders
- **Server:** Beelink SER5 (192.168.72.191, sashok-SER, Ubuntu 24.04 LTS) — primary; Pi5 deprecated June 2026
- **Language:** English for HOT/WARM/PROMPT; COLD.md archive remains Ukrainian
- **API keys:** 9 separate keys per bot — do NOT consolidate (cost tracking)
- **chkp workflow shift:** CC proposes backlog strikes externally (no second LLM call needed inside chkp)
- **BACKLOG_DONE.md:** new append-only archive for struck items, prevents BACKLOG.md bloat
- **Model IDs:** Sonnet 5 is latest; audit shared/ + all projects for stale references