---
project: meta
updated: 2026-07-01
---

# HOT — meta

## Now

Completed English language migration for chkp and project documentation: updated chkp.py SYSTEM_PROMPT to enforce English for HOT/WARM/PROMPT output, translated meta HOT.md+WARM.md+PROMPT.md to English, added Language rule to meta/CLAUDE.md. drone-recon also updated (PROMPT.md and CLAUDE.md Rule 1).

## Last done

- Updated chkp.py SYSTEM_PROMPT rules 4+6: enforce English for all generated files (HOT, WARM, PROMPT)
- Translated meta HOT.md, WARM.md, PROMPT.md from Ukrainian to English
- Added Language rule to meta/CLAUDE.md: "COLD.md remains append-only in Ukrainian (archive). All new entries HOT/WARM/PROMPT generated in English."
- Updated drone-recon PROMPT.md to English
- Updated drone-recon CLAUDE.md Rule 1 for language consistency
- Verified chkp runs auto-generate English output (no manual intervention needed in future sessions)

## Next

- Continue Pi5 reference cleanup in remaining 5 projects (insilver-v3, sam, garcia, ed, household_agent): remove Pi5 refs, update COLD.md entries, verify Beelink IP usage
- Redesign backup strategy for Beelink SER5 (replace H:\pi_backups + SSH pi5_backup scheme with systemd timer + local USB, or cloud S3, or intra-LAN pull)
- Sam NBLM Intervention 2 — log aggregation design ready for next implementation session

## Blockers

None.

## Active branches

- WARM diff-mode v3.5: live production, 79% token economy (6 projects ready for scaling)
- suggest_backlog_strikes: live production, semantic drift fix, 54/54 pytest PASS
- httpx logging suppression: 6/6 bots deployed, security patch active
- Sam NBLM Intervention 1: DONE (UUID dangling detection live), Intervention 2 design queued
- morning_digest systemd timer: live at 09:00 daily, Telegram BACKLOG summary active
- Infrastructure migration: Pi5→Beelink SER5 complete (June 2026), meta cleanup done, 5 projects pending
- Language migration: English for HOT/WARM/PROMPT output, COLD.md remains Ukrainian (archive)

## Open questions

- Backup strategy for Beelink SER5: should we use systemd timer + local USB, cloud S3, or intra-LAN NAS pull? (current H:\pi_backups scheme tied to Windows + Pi5 SSH key)
- Priority order for remaining 5 projects cleanup (insilver-v3, sam, garcia, ed, household_agent): this session or defer to next?
- Sam NBLM Intervention 2 (log aggregation) — should design be implemented now or deferred to Sam-dedicated session?

## Reminders

- **Server:** Beelink SER5, hostname `sashok-SER`, IP `192.168.72.191`, Ubuntu 24.04 LTS (primary; Pi5 deprecated since June 2026)
- **Backup chain (outdated):** Pi5-specific H:\pi_backups + SSH pi5_backup scheme archived 2026-06-30, needs redesign for Beelink
- **API keys:** 9 separate (abby-v2, ed, garcia, household_agent, insilver-v3, kit, sam, sam-v2, meta/digest) — do NOT consolidate (cost tracking requirement)
- **Language:** All new HOT/WARM/PROMPT in English; COLD.md archive remains Ukrainian
- **DIY UPS for Pi5:** assembled 2026-05-19 (XL4015 + 2S2P 18650), GPIO integration incomplete (leftover from Pi5 era)