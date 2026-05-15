---
project: meta
updated: 2026-05-15
---

# HOT — meta

## Now

Token tracker audit completed: read-only log works, write-side connected only to digest + garcia. Sam/insilver/abby/ed/meggy have dead /stats UI with 0 records for a month — not a blocker, Anthropic Console covers total spend.

## Last done

- Token tracker audit: verified read-only log functionality (74 entries since 2026-04-13, clean format ts/agent/in/out/cost)
- Confirmed write-side integration for digest + garcia only
- Verified /stats UI on sam/insilver/abby/ed/meggy: inactive, 0 records for 30 days
- Conclusion: per-bot logging not critical, Anthropic Console sufficient for cost tracking

## Next

Household_agent .git audit (712K, not 239M as initially suspected). If clean, proceed to optional antypastka #24 on another BACKLOG item, or defer to Влада-Ксюші voice extraction task (~2h, when time allocated).

## Blockers

None.

## Active branches

- httpx logging suppression: live on 2/6 bots (abby-v2, household_agent), 4 remaining (ed, garcia, insilver-v3, sam) queued for audit
- chkp.py robustness: 4 fixes + 22 new unit tests (48/48 pass), ready for production validation
- morning_digest: systemd timer live 09:00 daily, Telegram delivery confirmed
- shared/ library: audit completed, BACKLOG item corrected (active library, not dead code)
- token tracker: audit validates non-critical status for live ops

## Open questions

- Will shared/ usage remain stable, or does garcia refactor (PodcastModule inheritance) require polyrepo planning later?
- Does household_agent require sudo restart, or is auto-restart via systemd sufficient after token rotation?
- What regressions might arise from 4 chkp robustness fixes on live data (multi-match context, whitespace strip, validation messages)?
- Should all 6 bots (abby-v2, ed, garcia, household_agent, insilver-v3, sam) adopt identical httpx suppression pattern, or audit each individually?
- Token tracker write-side expansion needed for all 6 bots, or is current digest + garcia sampling sufficient for cost allocation?

## Reminders

- household_agent token rotated (BotFather, 2026-05-15) — monitor for anomalous usage
- Backup chain ready, DR drill awaits spare SD card arrival
- BACKLOG rotation policy for abby images (759M) + sam audio (827M) deferred to next session
- Strikethrough rule enforcement (CLAUDE.md + BACKLOG.md dual-location): observe 2–3 sessions, then decide [CLOSED] markup if recurrence
- httpx suppression needed on 4 bots (ed, garcia, insilver-v3, sam) before next checkpoint
- shared/ BACKLOG item removed (confirmed active library with 11+7+1+2 imports across 4 users)
- Token tracker non-critical conclusion: no action needed unless per-bot fine-grained billing required in future