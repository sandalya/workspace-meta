---
project: meta
updated: 2026-07-21
---

# HOT — meta

## Now
Built chkp-sumd: host-side systemd broker that mirrors chkp-pushd, allowing chkp finalize (Anthropic call, warm_ops, backlog, commit/push) to run outside the API-key-isolated sandbox. Refactored chkp.py to separate secret-free pre-flight from finalize logic; finalize moved to run_checkpoint_finalize() callable by the daemon. Committed previously-untracked chkp-pushd.py, chkp_push_client.py, and chkp-sumd.config.json. Live-verified with real key on drone-recon end-to-end.

## Last done
- Designed chkp-sumd architecture: unix socket bridge between sandbox chkp.py and host systemd
- Implemented run_checkpoint_finalize() to encapsulate Anthropic call + warm_ops + backlog strikes + git commit/push
- Refactored do_checkpoint() to call finalize via socket instead of inline
- Committed chkp-pushd.py, chkp_push_client.py, chkp-sumd.config.json to meta repo
- Set up ~/.config/systemd/user/chkp-sumd.service and ~/.config/chkp/sumd.env
- End-to-end validation: real checkpoint run on drone-recon with API key handling via sumd

## Next
Monitor chkp-sumd.log for any future checkpoint failures; otherwise, business as usual. No immediate action needed.

## Blockers
None.

## Active branches
- chkp-sumd: systemd broker live, proven end-to-end
- WARM diff-mode (warm_ops): 79% token economy, production-ready
- httpx logging suppression: 6/6 bots patched
- Sam NBLM Intervention 1: DONE, Intervention 2 queued
- morning_digest systemd timer: 09:00 daily automation
- Infrastructure migration: Pi5→Beelink SER5 complete, 5 projects still have stale refs
- Model ID sweep: meta done, 5 projects queued for Sonnet 5 update

## Open questions
- Does chkp-sumd.log grow unbounded, or should we rotate/vacuum it periodically?
- Should we expand chkp-sumd to handle other bots (insilver-v3, sam, garcia, ed, household_agent) or keep it meta-only for now?
- BACKLOG_DONE.md purge strategy: age-based (e.g., archive > 1 year), count-based (e.g., every 100 items), or never?

## Reminders
- **Server:** Beelink SER5 (192.168.72.191, sashok-SER, Ubuntu 24.04 LTS) — Pi5 deprecated
- **Language:** English for HOT/WARM/PROMPT; COLD.md archive remains Ukrainian
- **API keys:** 9 separate keys per bot — do NOT consolidate (cost tracking)
- **chkp workflow:** CC proposes strikes externally; chkp applies via --backlog-strike
- **BACKLOG_DONE.md:** append-only log prevents active BACKLOG.md bloat
- **Model IDs:** Sonnet 5 latest; audit remaining 5 projects for stale references
- **CC launch:** Always from workspace/ root, not meta/, to load .claude/rules/ files